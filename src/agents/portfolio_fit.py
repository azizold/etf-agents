from .. import db
from .base import call_stage


def check(theme_id: str, ticker: str, composition_eval: dict, risk_result: dict) -> dict:
    open_positions = db.get_open_positions()
    input_data = {
        "ticker": ticker,
        "tier": composition_eval.get("tier"),
        "is_leveraged_inverse": composition_eval.get("is_leveraged_inverse", False),
        "top_holdings": composition_eval.get("top_holdings", []),
        "confidence": risk_result.get("confidence"),
        "open_positions": [
            {
                "ticker": p["ticker"], "tier": p["tier"], "confidence": p["confidence"],
                "thesis_state": p["thesis_state"],
            }
            for p in open_positions
        ],
        "open_slot_count": max(0, 8 - len(open_positions)),
    }
    result = call_stage(
        workflow="A", agent_name="portfolio_fit", doc_filename="05_portfolio_fit.md",
        input_data=input_data, use_web_search=False, theme_id=theme_id, max_tokens=4096,
    )
    return result["parsed"]


def check_lockups(open_positions: list[dict]) -> list[dict]:
    """Workflow B: which flagged (broken/structural-risk) positions have a
    lockup that has now cleared and can move to 'cleared for exit'."""
    import datetime as dt
    cleared = []
    now = dt.datetime.now(dt.timezone.utc)
    for p in open_positions:
        if p["thesis_state"] != "broken":
            continue
        eligible_exit_at = db.get_position_eligible_exit_at(p["id"])
        if eligible_exit_at and eligible_exit_at <= now:
            cleared.append({**p, "eligible_exit_at": eligible_exit_at})
    return cleared
