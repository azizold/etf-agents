from .base import call_stage


def verify(theme_id: str, ticker: str, composition_eval: dict, valuation: dict,
           risk_result: dict, portfolio_fit_result: dict) -> dict:
    input_data = {
        "ticker": ticker,
        "composition_eval": composition_eval,
        "valuation": valuation,
        "risk_result": risk_result,
        "portfolio_fit_result": portfolio_fit_result,
    }
    result = call_stage(
        workflow="A", agent_name="verification", doc_filename="06_verification.md",
        input_data=input_data, use_web_search=False, theme_id=theme_id, max_tokens=4096,
    )
    return result["parsed"]


def verify_monitoring(position: dict, risk_monitor_result: dict) -> dict:
    input_data = {
        "position": {k: position[k] for k in ("ticker", "thesis", "thesis_state")},
        "risk_monitor_result": risk_monitor_result,
    }
    result = call_stage(
        workflow="B", agent_name="verification_monitoring", doc_filename="06_verification.md",
        input_data=input_data, use_web_search=False, position_id=position["id"], max_tokens=4096,
    )
    return result["parsed"]
