import datetime as dt
import json

from .. import db
from .base import call_stage


def evaluate(theme_id: str, candidate_tickers: list[str]) -> dict:
    existing_positions = db.get_open_positions()
    input_data = {
        "candidate_tickers": candidate_tickers,
        "existing_position_tickers": [p["ticker"] for p in existing_positions],
    }
    result = call_stage(
        workflow="A", agent_name="composition", doc_filename="02_composition.md",
        input_data=input_data, use_web_search=True, theme_id=theme_id, max_tokens=16000,
    )
    parsed = result["parsed"]

    for ev in parsed.get("evaluations", []):
        # For a hard-screened-out candidate (e.g. a single-company ticker
        # that isn't an ETF at all), the model sometimes fills fields it
        # couldn't find with "" rather than omitting them or using null —
        # that breaks the date/numeric columns in `funds` (Postgres rejects
        # "" for a `date` column outright). Treat "" as "not provided" for
        # any field that isn't a plain string column.
        db.upsert_fund(
            ticker=ev["ticker"], name=ev["ticker"], theme_id=theme_id,
            asset_class=ev.get("asset_class"), tier=ev.get("tier"),
            aum_usd=_blank_to_none(ev.get("aum_usd")),
            inception_date=_blank_to_none(ev.get("inception_date")),
            expense_ratio=_blank_to_none(ev.get("expense_ratio")),
            is_leveraged_inverse=ev.get("is_leveraged_inverse", False),
            is_fx_exposed=ev.get("is_fx_exposed", False), fx_note=ev.get("fx_note"),
            last_screened_at=dt.datetime.now(dt.timezone.utc),
            screen_result=ev.get("screen_result"), screen_notes=ev.get("screen_notes"),
            selected_over=json.dumps(ev.get("selected_over", [])),
        )
    return parsed


def _blank_to_none(value):
    """Postgres rejects "" for date/numeric columns; the model occasionally
    emits "" instead of null for a field it couldn't find (typically on a
    hard-screened-out, not-actually-an-ETF candidate)."""
    return None if value == "" else value
