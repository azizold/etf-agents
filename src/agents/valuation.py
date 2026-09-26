from .base import call_stage


def value(theme_id: str, ticker: str, composition_eval: dict) -> dict:
    input_data = {
        "ticker": ticker,
        "asset_class": composition_eval.get("asset_class"),
        "expense_ratio": composition_eval.get("expense_ratio"),
        "current_price": composition_eval.get("current_price"),
        "current_price_source": composition_eval.get("current_price_source"),
        "top_holdings": composition_eval.get("top_holdings", []),
        "is_fx_exposed": composition_eval.get("is_fx_exposed", False),
        "fx_note": composition_eval.get("fx_note"),
    }
    result = call_stage(
        workflow="A", agent_name="valuation", doc_filename="03_valuation.md",
        input_data=input_data, use_web_search=True, theme_id=theme_id, max_tokens=8192,
    )
    return result["parsed"]
