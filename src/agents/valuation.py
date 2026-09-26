from .. import market_data
from .base import call_stage


def value(theme_id: str, ticker: str, composition_eval: dict) -> dict:
    top_holding_data = {}
    if composition_eval.get("asset_class") == "equity":
        for h in composition_eval.get("top_holdings", []):
            holding_ticker = h.get("ticker")
            if holding_ticker:
                top_holding_data[holding_ticker] = {
                    "key_metrics": market_data.company_key_metrics(holding_ticker),
                    "income_statement": market_data.company_income_statement(holding_ticker),
                }

    input_data = {
        "ticker": ticker,
        "asset_class": composition_eval.get("asset_class"),
        "expense_ratio": composition_eval.get("expense_ratio"),
        "top_holdings": composition_eval.get("top_holdings", []),
        "top_holding_financials": top_holding_data,
        "current_quote": market_data.quote(ticker),
        "is_fx_exposed": composition_eval.get("is_fx_exposed", False),
        "fx_note": composition_eval.get("fx_note"),
    }
    result = call_stage(
        workflow="A", agent_name="valuation", doc_filename="03_valuation.md",
        input_data=input_data, use_web_search=True, theme_id=theme_id, max_tokens=8192,
    )
    return result["parsed"]
