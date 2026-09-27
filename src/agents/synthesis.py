from .base import call_stage


def assemble_new_opportunity(theme_id: str, ticker: str, composition_eval: dict,
                              valuation: dict, risk_result: dict,
                              portfolio_fit_result: dict) -> dict:
    input_data = {
        "deck_type": "new_opportunity",
        "ticker": ticker,
        "composition_eval": composition_eval,
        "valuation": valuation,
        "risk_result": risk_result,
        "portfolio_fit_result": portfolio_fit_result,
    }
    result = call_stage(
        workflow="A", agent_name="synthesis", doc_filename="07_synthesis.md",
        # field_9_target_price now renders a full per-holding, per-scenario
        # markdown table plus four labeled disclosure paragraphs (the deeper
        # valuation format) — 8192 risks the same starvation seen in
        # verification.py; match the research-stage ceiling.
        input_data=input_data, use_web_search=False, theme_id=theme_id, max_tokens=16000,
    )
    return result["parsed"]


def assemble_monitoring(position: dict, risk_monitor_result: dict, lockup_status: dict) -> dict:
    input_data = {
        "deck_type": "monitoring",
        "ticker": position["ticker"],
        "position": {k: position[k] for k in ("thesis", "thesis_state")},
        "risk_monitor_result": risk_monitor_result,
        "lockup_status": lockup_status,
    }
    result = call_stage(
        workflow="B", agent_name="synthesis_monitoring", doc_filename="07_synthesis.md",
        input_data=input_data, use_web_search=False, position_id=position["id"], max_tokens=4096,
    )
    return result["parsed"]
