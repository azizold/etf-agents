"""Data access layer over the Supabase Postgres instance.

Kept deliberately thin and explicit — every agent module calls these
functions rather than writing raw SQL inline, so the schema only needs to be
understood in one place.
"""
import json
import datetime as dt
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from . import config

psycopg2.extras.register_uuid()


@contextmanager
def get_conn():
    conn = psycopg2.connect(config.DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def dict_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


# kept for internal call sites written before the public alias existed
_dict_cursor = dict_cursor


# ── Themes ───────────────────────────────────────────────────────────────

def insert_theme(name, description, convergence, why_now, discovery_source):
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            """insert into themes (name, description, convergence, why_now, discovery_source)
               values (%s,%s,%s,%s,%s) returning *""",
            (name, description, convergence, why_now, discovery_source),
        )
        return cur.fetchone()


def update_theme_status(theme_id, status):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("update themes set status = %s where id = %s", (status, theme_id))


# ── Funds ────────────────────────────────────────────────────────────────

def upsert_fund(ticker, **fields):
    columns = ["ticker"] + list(fields.keys())
    values = [ticker] + list(fields.values())
    placeholders = ", ".join(["%s"] * len(columns))
    updates = ", ".join(f"{c} = excluded.{c}" for c in fields.keys())
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            f"""insert into funds ({", ".join(columns)}) values ({placeholders})
                on conflict (ticker) do update set {updates}
                returning *""",
            values,
        )
        return cur.fetchone()


def get_fund_by_ticker(ticker):
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute("select * from funds where ticker = %s", (ticker,))
        return cur.fetchone()


# ── Positions & lots ─────────────────────────────────────────────────────

def open_position(fund_id, thesis, thesis_evidence, invalidation_condition,
                   confidence, tier, opening_deck_id):
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            """insert into positions
               (fund_id, thesis, thesis_evidence, invalidation_condition,
                confidence, tier, opening_deck_id)
               values (%s,%s,%s,%s,%s,%s,%s) returning *""",
            (fund_id, thesis, thesis_evidence, invalidation_condition,
             confidence, tier, opening_deck_id),
        )
        return cur.fetchone()


def open_lot(position_id, shares, fill_price, deck_id, fill_date=None):
    """Opens a new lot and starts its own 30-day clock (Section 5).
    The position's effective eligible-exit date is always its most recent lot's
    date (LIFO) — callers should not assume the original entry date still applies.
    """
    fill_date = fill_date or dt.datetime.now(dt.timezone.utc)
    eligible_exit_at = fill_date + dt.timedelta(days=30)
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            """insert into lots (position_id, shares, fill_price, opened_at,
                                  eligible_exit_at, deck_id)
               values (%s,%s,%s,%s,%s,%s) returning *""",
            (position_id, shares, fill_price, fill_date, eligible_exit_at, deck_id),
        )
        return cur.fetchone()


def get_open_positions():
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            """select p.*, f.ticker, f.name as fund_name, f.tier as fund_tier
               from positions p join funds f on f.id = p.fund_id
               where p.status = 'open'"""
        )
        return cur.fetchall()


def get_position_eligible_exit_at(position_id):
    """A position's true eligible-exit date = its most recent OPEN lot's date (LIFO)."""
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            """select eligible_exit_at from lots
               where position_id = %s and status = 'open'
               order by opened_at desc limit 1""",
            (position_id,),
        )
        row = cur.fetchone()
        return row["eligible_exit_at"] if row else None


def update_thesis_state(position_id, thesis_state, notes=None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """update positions set thesis_state = %s, last_scored_at = now()
               where id = %s""",
            (thesis_state, position_id),
        )


def close_position(position_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "update positions set status = 'closed', closed_at = now() where id = %s",
            (position_id,),
        )


# ── Decks ────────────────────────────────────────────────────────────────

def create_deck(deck_type, content, fund_id=None, theme_id=None, position_id=None,
                 confidence=None, recommended_action=None, urgent=False):
    expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=7)  # ~5 business days
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            """insert into decks (deck_type, fund_id, theme_id, position_id, content,
                                   confidence, recommended_action, urgent, expires_at)
               values (%s,%s,%s,%s,%s,%s,%s,%s,%s) returning *""",
            (deck_type, fund_id, theme_id, position_id, json.dumps(content),
             confidence, recommended_action, urgent, expires_at),
        )
        return cur.fetchone()


def set_deck_github_issue(deck_id, issue_number, issue_url):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "update decks set github_issue_number = %s, github_issue_url = %s where id = %s",
            (issue_number, issue_url, deck_id),
        )


def record_decision(deck_id, decision, notes=None):
    with get_conn() as conn, conn.cursor() as cur:
        status = {
            "yes": "approved", "confirm": "approved",
            "no": "rejected", "override": "approved",
            "more_info": "more_info_requested",
        }.get(decision, "pending")
        cur.execute(
            """update decks set decision = %s, decision_notes = %s,
                                 decided_at = now(), status = %s
               where id = %s""",
            (decision, notes, status, deck_id),
        )


def increment_more_info_round(deck_id):
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            "update decks set round_count = round_count + 1 where id = %s returning round_count",
            (deck_id,),
        )
        return cur.fetchone()["round_count"]


def get_pending_decks_past_expiry():
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            """select * from decks
               where status in ('pending','more_info_requested')
                 and expires_at < now()"""
        )
        return cur.fetchall()


def expire_deck(deck_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("update decks set status = 'expired' where id = %s", (deck_id,))


# ── Sources (anti-hallucination) ────────────────────────────────────────

def record_sources(deck_id, sources: list[dict]):
    """sources: [{"claim":..., "source":..., "url":..., "verified": bool}, ...]"""
    with get_conn() as conn, conn.cursor() as cur:
        for s in sources:
            cur.execute(
                """insert into sources (deck_id, claim, source, url, verified)
                   values (%s,%s,%s,%s,%s)""",
                (deck_id, s["claim"], s["source"], s.get("url"), s.get("verified", False)),
            )


# ── Agent run log ────────────────────────────────────────────────────────

def start_agent_run(workflow, agent_name, theme_id=None, fund_id=None,
                     position_id=None, deck_id=None, input_summary=None):
    with get_conn() as conn, _dict_cursor(conn) as cur:
        cur.execute(
            """insert into agent_runs
               (workflow, agent_name, theme_id, fund_id, position_id, deck_id, input_summary)
               values (%s,%s,%s,%s,%s,%s,%s) returning *""",
            (workflow, agent_name, theme_id, fund_id, position_id, deck_id,
             json.dumps(input_summary) if input_summary is not None else None),
        )
        return cur.fetchone()["id"]


def finish_agent_run(run_id, status, output_summary=None, error=None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """update agent_runs set finished_at = now(), status = %s,
                                      output_summary = %s, error = %s
               where id = %s""",
            (status, json.dumps(output_summary) if output_summary is not None else None,
             error, run_id),
        )


# ── Cash ledger ──────────────────────────────────────────────────────────

def record_cash_entry(entry_type, amount, trade_id=None, notes=None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """insert into cash_ledger (entry_type, amount, trade_id, notes)
               values (%s,%s,%s,%s)""",
            (entry_type, amount, trade_id, notes),
        )
