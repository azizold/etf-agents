from .base import call_stage


def screen(theme_id: str, ticker: str, composition_eval: dict, valuation: dict) -> dict:
    input_data = {
        "ticker": ticker,
        "theme_description": composition_eval.get("screen_notes"),
        "tier": composition_eval.get("tier"),
        "asset_class": composition_eval.get("asset_class"),
        "valuation_summary": {
            "target_price_base": valuation.get("target_price_base"),
            "implied_return_base_pct": valuation.get("implied_return_base_pct"),
        },
    }
    result = call_stage(
        workflow="A", agent_name="risk_counter_case", doc_filename="04_risk_counter_case.md",
        input_data=input_data, use_web_search=True, theme_id=theme_id, max_tokens=8192,
    )
    return result["parsed"]


def monitor(position: dict) -> dict:
    """Workflow B monitoring pass — re-scores an existing position's thesis."""
    input_data = {
        "ticker": position["ticker"],
        "thesis": position["thesis"],
        "thesis_evidence": position["thesis_evidence"],
        "invalidation_condition": position["invalidation_condition"],
        "current_thesis_state": position["thesis_state"],
    }
    result = call_stage(
        workflow="B", agent_name="risk_counter_case_monitoring",
        doc_filename="04b_risk_monitoring.md", input_data=input_data,
        use_web_search=True, position_id=position["id"], max_tokens=8192,
    )
    return result["parsed"]
