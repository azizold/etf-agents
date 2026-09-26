import datetime as dt
import json

from .. import db, market_data
from .base import call_stage


def evaluate(theme_id: str, candidate_tickers: list[str]) -> dict:
    fund_data = {}
    for ticker in candidate_tickers:
        fund_data[ticker] = {
            "profile": market_data.etf_profile(ticker),
            "holdings": market_data.etf_holdings(ticker),
            "sector_weights": market_data.etf_sector_weights(ticker),
            "country_weights": market_data.etf_country_weights(ticker),
            "quote": market_data.quote(ticker),
        }

    existing_positions = db.get_open_positions()
    input_data = {
        "candidate_tickers": candidate_tickers,
        "fund_data": fund_data,
        "existing_position_tickers": [p["ticker"] for p in existing_positions],
    }
    result = call_stage(
        workflow="A", agent_name="composition", doc_filename="02_composition.md",
        input_data=input_data, use_web_search=False, theme_id=theme_id, max_tokens=8192,
    )
    parsed = result["parsed"]

    for ev in parsed.get("evaluations", []):
        db.upsert_fund(
            ticker=ev["ticker"], name=ev["ticker"], theme_id=theme_id,
            asset_class=ev.get("asset_class"), tier=ev.get("tier"),
            aum_usd=ev.get("aum_usd"), inception_date=ev.get("inception_date"),
            expense_ratio=ev.get("expense_ratio"),
            is_leveraged_inverse=ev.get("is_leveraged_inverse", False),
            is_fx_exposed=ev.get("is_fx_exposed", False), fx_note=ev.get("fx_note"),
            last_screened_at=dt.datetime.now(dt.timezone.utc),
            screen_result=ev.get("screen_result"), screen_notes=ev.get("screen_notes"),
            selected_over=json.dumps(ev.get("selected_over", [])),
        )
    return parsed
