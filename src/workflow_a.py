"""Workflow A — New Opportunity.

Run modes (see .github/workflows/workflow_a.yml for the schedule):
  discover   — Theme Discovery Agent proposes candidates, pipeline runs on
               each one that clears composition/risk screening.
  responses  — reads new GitHub Issue comments on pending decks and applies
               decisions (see docs/PIPELINE.md for the exact comment format).
  fills      — reads "FILLED: ..." comments on approved decks and opens the
               position/lot in the database.
  expire     — applies the 5-business-day no-response default (Section 8).

A fresh GitHub Actions run does all four in sequence, in that order, so a
single scheduled trigger keeps the whole workflow moving.
"""
import argparse
import datetime as dt
import re

from . import db, github_issues
from .agents import composition, portfolio_fit, risk, synthesis, theme_discovery, valuation, verification

MAX_VERIFICATION_RETRIES = 2

# Bounds cost/runtime per discovery run and matches the policy's own review
# cadence (Section 9: "typically 1/week, max 2-3" new-opportunity decks) —
# there's no reason a single run should push more candidates through the
# full Valuation->Verification chain than that in one pass.
MAX_CANDIDATES_PER_RUN = 3


def run_pipeline_for_candidate(theme_id: str, ticker: str, composition_eval: dict) -> dict | None:
    """Runs stages 3-7 (Valuation -> Verification, looping on failure) for one
    ticker, then creates + posts the deck. Returns the created deck row, or
    None if the candidate was rejected/failed verification too many times."""
    print(f"[pipeline] {ticker}: running valuation...")
    val = valuation.value(theme_id, ticker, composition_eval)
    print(f"[pipeline] {ticker}: running risk screen...")
    risk_result = risk.screen(theme_id, ticker, composition_eval, val)
    print(f"[pipeline] {ticker}: risk confidence = {risk_result.get('confidence')}")

    if risk_result.get("confidence") == "reject":
        print(f"[pipeline] {ticker}: REJECTED by risk agent — {risk_result.get('confidence_reasoning')}")
        return None

    pf_result = portfolio_fit.check(theme_id, ticker, composition_eval, risk_result)
    print(f"[pipeline] {ticker}: portfolio-fit sizing = {pf_result.get('recommended_position_size_pct_of_book')}%")

    for attempt in range(MAX_VERIFICATION_RETRIES + 1):
        verdict = verification.verify(theme_id, ticker, composition_eval, val, risk_result, pf_result)
        print(f"[pipeline] {ticker}: verification attempt {attempt} passed = {verdict.get('passed')}")
        if verdict.get("passed"):
            break
        send_back = set(verdict.get("send_back_to", []))
        if attempt == MAX_VERIFICATION_RETRIES:
            print(f"[pipeline] {ticker}: DROPPED — failed verification after {MAX_VERIFICATION_RETRIES} retries. "
                  f"notes={verdict.get('notes')}")
            return None
        if "composition" in send_back:
            composition_eval = composition.evaluate(theme_id, [ticker])["evaluations"][0]
        if "valuation" in send_back:
            val = valuation.value(theme_id, ticker, composition_eval)
        if "risk" in send_back:
            risk_result = risk.screen(theme_id, ticker, composition_eval, val)
        pf_result = portfolio_fit.check(theme_id, ticker, composition_eval, risk_result)

    print(f"[pipeline] {ticker}: assembling deck...")
    deck_content = synthesis.assemble_new_opportunity(
        theme_id, ticker, composition_eval, val, risk_result, pf_result
    )
    print(f"[pipeline] {ticker}: DECK CREATED, confidence={deck_content.get('confidence')}")

    fund = db.get_fund_by_ticker(ticker)
    deck = db.create_deck(
        deck_type="new_opportunity", content=deck_content,
        fund_id=fund["id"] if fund else None, theme_id=theme_id,
        confidence=deck_content.get("confidence"),
    )

    sources = []
    for key in ("sources",):
        sources.extend(val.get(key, []))
        sources.extend(risk_result.get(key, []))
    if sources:
        db.record_sources(deck["id"], sources)

    issue = github_issues.create_deck_issue(
        title=f"[Deck] New opportunity: {ticker} ({deck_content.get('confidence', '?').title()} confidence)",
        body=deck_content.get("markdown", "(no markdown rendered)") + "\n\n---\n"
             + _response_instructions(),
        labels=["new-opportunity-deck"],
    )
    db.set_deck_github_issue(deck["id"], issue["number"], issue["url"])
    return deck


def _response_instructions() -> str:
    return (
        "**To respond:** comment `YES`, `NO`, or `MORE INFO[stage]: your question` "
        "(stage is one of `composition`, `valuation`, `risk` — omit for a general follow-up). "
        "Silence for 5 business days defaults to **NO** (logged as expired, not rejected)."
    )


def run_discovery(discovery_source: str) -> None:
    discovered = theme_discovery.discover(discovery_source)
    print(f"[discover] {len(discovered['candidates'])} candidate theme(s), "
          f"{len(discovered.get('screened_out', []))} screened out")
    for s in discovered.get("screened_out", []):
        print(f"[discover] screened out: {s}")

    processed = 0
    for candidate in discovered["candidates"]:
        if processed >= MAX_CANDIDATES_PER_RUN:
            print(f"[discover] hit MAX_CANDIDATES_PER_RUN ({MAX_CANDIDATES_PER_RUN}) — "
                  f"remaining candidates stay logged as 'candidate' themes for a future run.")
            break
        theme_id = candidate["theme_id"]
        tickers = candidate.get("candidate_tickers") or []
        print(f"[discover] theme '{candidate['theme_name']}' -> candidate tickers: {tickers}")
        if not tickers:
            continue
        comp_result = composition.evaluate(theme_id, tickers)
        print(f"[discover] composition advance_to_valuation: {comp_result.get('advance_to_valuation')}")
        for ev in comp_result.get("evaluations", []):
            print(f"[discover]   {ev['ticker']}: tier={ev.get('tier')} "
                  f"screen_result={ev.get('screen_result')} notes={ev.get('screen_notes')}")
        for ticker in comp_result.get("advance_to_valuation", []):
            if processed >= MAX_CANDIDATES_PER_RUN:
                break
            ev = next((e for e in comp_result["evaluations"] if e["ticker"] == ticker), None)
            if ev is None or ev.get("tier") == "excluded":
                continue
            run_pipeline_for_candidate(theme_id, ticker, ev)
            processed += 1


_DECISION_RE = re.compile(r"^\s*(YES|NO|MORE INFO(?:\[(\w+)\])?)\s*:?\s*(.*)$", re.IGNORECASE | re.DOTALL)


def process_responses() -> None:
    pending = [d for d in _get_pending_decks()]
    for deck in pending:
        if not deck["github_issue_number"]:
            continue
        comments = github_issues.get_new_comments(deck["github_issue_number"])
        for c in comments:
            match = _DECISION_RE.match(c["body"].strip())
            if not match:
                continue
            raw_decision, stage, notes = match.groups()
            decision_key = raw_decision.split("[")[0].strip().lower().replace(" ", "_")
            db.record_decision(deck["id"], decision_key, notes)
            if decision_key == "more_info":
                round_count = db.increment_more_info_round(deck["id"])
                if round_count > 2:
                    github_issues.comment_on_issue(
                        deck["github_issue_number"],
                        "More-information loop cap (2 rounds) reached — presenting the best "
                        "available answer with the gap disclosed. Please decide YES/NO on what's known.",
                    )
                else:
                    github_issues.comment_on_issue(
                        deck["github_issue_number"],
                        f"Noted — routing your question to the {stage or 'relevant'} stage for a "
                        f"deeper look. (Automatic re-run of this stage is not yet wired up in this "
                        f"build; re-run workflow_a manually with this ticker/question in the meantime.)",
                    )
            elif decision_key == "yes":
                github_issues.comment_on_issue(
                    deck["github_issue_number"],
                    "Approved. Once you place the paper trade, comment `FILLED: <shares> shares "
                    "at $<price> on <YYYY-MM-DD>` so it gets logged and the 30-day hold clock starts.",
                )
            break  # one decision per deck per run


_FILL_RE = re.compile(
    r"FILLED:\s*([\d.]+)\s*shares\s*at\s*\$?([\d.]+)\s*(?:on\s*([\d-]+))?", re.IGNORECASE
)


def process_fills() -> None:
    approved = [d for d in _get_approved_unfilled_decks()]
    for deck in approved:
        if not deck["github_issue_number"]:
            continue
        comments = github_issues.get_new_comments(deck["github_issue_number"])
        for c in comments:
            match = _FILL_RE.search(c["body"])
            if not match:
                continue
            shares, price, date_str = match.groups()
            fill_date = dt.datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc) \
                if date_str else dt.datetime.now(dt.timezone.utc)

            fund_id = deck["fund_id"]
            content = deck["content"]
            fields = content.get("fields", {})
            position = db.open_position(
                fund_id=fund_id,
                thesis=fields.get("field_1_thesis", ""),
                thesis_evidence=fields.get("field_1_thesis", ""),
                invalidation_condition=fields.get("field_8_thesis_invalidation_trigger", ""),
                confidence=deck["confidence"], tier=fields.get("field_2_tier_classification", "speculative"),
                opening_deck_id=deck["id"],
            )
            lot = db.open_lot(position["id"], float(shares), float(price), deck["id"], fill_date)
            trade = _record_trade(lot["position_id"], lot["id"], "buy", float(shares), float(price), deck["id"])
            db.record_cash_entry("buy", -float(shares) * float(price), trade_id=trade, notes=f"{deck['id']}")
            github_issues.comment_on_issue(
                deck["github_issue_number"],
                f"Logged: {shares} shares at ${price}, eligible-exit date {lot['eligible_exit_at']:%Y-%m-%d}.",
            )
            github_issues.close_issue(deck["github_issue_number"])
            break


def _record_trade(position_id, lot_id, side, shares, price, deck_id):
    with db.get_conn() as conn, db.dict_cursor(conn) as cur:
        cur.execute(
            """insert into trades (lot_id, position_id, side, shares, price, deck_id)
               values (%s,%s,%s,%s,%s,%s) returning id""",
            (lot_id, position_id, side, shares, price, deck_id),
        )
        return cur.fetchone()["id"]


def apply_no_response_default() -> None:
    for deck in db.get_pending_decks_past_expiry():
        db.expire_deck(deck["id"])
        if deck["github_issue_number"]:
            github_issues.comment_on_issue(
                deck["github_issue_number"],
                "No response within 5 business days — defaulting to **NO** per policy "
                "(Section 8). Logged as expired, not rejected on the merits; it can "
                "resurface later as a fresh deck if the theme still holds.",
            )
            github_issues.close_issue(deck["github_issue_number"])


def _get_pending_decks():
    with db.get_conn() as conn, db.dict_cursor(conn) as cur:
        cur.execute("select * from decks where status in ('pending','more_info_requested')")
        return cur.fetchall()


def _get_approved_unfilled_decks():
    with db.get_conn() as conn, db.dict_cursor(conn) as cur:
        cur.execute(
            """select d.* from decks d
               where d.status = 'approved' and d.decision = 'yes'
                 and d.deck_type = 'new_opportunity'
                 and not exists (select 1 from lots l where l.deck_id = d.id)"""
        )
        return cur.fetchall()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["discover", "responses", "fills", "expire"])
    parser.add_argument("--source", default="scheduled")
    args = parser.parse_args()

    if args.mode == "discover":
        run_discovery(args.source)
    elif args.mode == "responses":
        process_responses()
    elif args.mode == "fills":
        process_fills()
    elif args.mode == "expire":
        apply_no_response_default()
