"""Thin wrapper around Financial Modeling Prep's /stable/ REST API.

CURRENTLY UNUSED by any agent — kept for reference / a possible future
re-introduction. During the first dry run (2026-09-26), FMP's free tier
turned out to only serve fundamental/ETF data for a small sample of ~87
well-known tickers (AAPL, TSLA, etc.); every real thematic-ETF candidate
returned 402 Payment Required. Rather than pay for FMP's Starter plan, every
agent that needs fund or company facts now uses Claude's own web search
instead (docs/agents/02_composition.md, 03_valuation.md) — see
docs/PIPELINE.md for the full explanation.

If a paid FMP plan (or another data provider) is added later, this module
is the place to wire it back in. All calls below use the /stable/ endpoints
with ?symbol=... query params, per FMP's current docs
(site.financialmodelingprep.com/developer/docs/stable).
"""
import requests

from . import config

BASE_URL = "https://financialmodelingprep.com/stable"
SOURCE_NAME = "Financial Modeling Prep"


def _get(path, params=None):
    params = dict(params or {})
    params["apikey"] = config.FMP_API_KEY
    resp = requests.get(f"{BASE_URL}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def quote(ticker: str) -> dict:
    """Current price snapshot for a ticker."""
    data = _get("/quote", params={"symbol": ticker})
    row = data[0] if data else {}
    return {"data": row, "source": SOURCE_NAME, "endpoint": "/quote"}


def etf_profile(ticker: str) -> dict:
    """AUM, expense ratio, inception date, asset class hints."""
    data = _get("/etf/info", params={"symbol": ticker})
    row = data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})
    return {"data": row, "source": SOURCE_NAME, "endpoint": "/etf/info"}


def etf_holdings(ticker: str) -> dict:
    """Holdings breakdown with weights."""
    data = _get("/etf/holdings", params={"symbol": ticker})
    return {"data": data, "source": SOURCE_NAME, "endpoint": "/etf/holdings"}


def etf_sector_weights(ticker: str) -> dict:
    data = _get("/etf/sector-weightings", params={"symbol": ticker})
    return {"data": data, "source": SOURCE_NAME, "endpoint": "/etf/sector-weightings"}


def etf_country_weights(ticker: str) -> dict:
    data = _get("/etf/country-weightings", params={"symbol": ticker})
    return {"data": data, "source": SOURCE_NAME, "endpoint": "/etf/country-weightings"}


def company_key_metrics(ticker: str) -> dict:
    """Revenue/EBITDA and related figures for a top holding (equity valuation, Section 6)."""
    data = _get("/key-metrics", params={"symbol": ticker, "limit": 5})
    return {"data": data, "source": SOURCE_NAME, "endpoint": "/key-metrics"}


def company_income_statement(ticker: str) -> dict:
    data = _get("/income-statement", params={"symbol": ticker, "limit": 5})
    return {"data": data, "source": SOURCE_NAME, "endpoint": "/income-statement"}


def historical_prices(ticker: str, days: int = 30) -> dict:
    data = _get("/historical-price-eod/light", params={"symbol": ticker})
    rows = data[:days] if isinstance(data, list) else []
    return {"data": rows, "source": SOURCE_NAME, "endpoint": "/historical-price-eod/light"}


def commodity_quote(symbol: str) -> dict:
    """e.g. symbol='GCUSD' for gold futures-equivalent spot."""
    data = _get("/quote", params={"symbol": symbol})
    row = data[0] if data else {}
    return {"data": row, "source": SOURCE_NAME, "endpoint": "/quote"}
