"""Thin wrapper around Financial Modeling Prep's REST API.

Every function returns raw provider data plus a `source` tag, so callers can
carry sourcing through to the deck (Section 1's sourcing rule) without
re-deriving it later.
"""
import requests

from . import config

BASE_URL = "https://financialmodelingprep.com"
SOURCE_NAME = "Financial Modeling Prep"

# NOTE: FMP has migrated some endpoints from /api/v3/ to /stable/ over time,
# and free-tier access to certain endpoints (e.g. etf-holder) has shifted
# between plans. Verify each endpoint below still returns data on the free
# tier during the first dry run (Task: "Dry run of full pipeline") and swap
# to the /stable/ equivalent if an endpoint 401s/404s.


def _get(path, params=None):
    params = dict(params or {})
    params["apikey"] = config.FMP_API_KEY
    resp = requests.get(f"{BASE_URL}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def quote(ticker: str) -> dict:
    """Current price snapshot for a ticker."""
    data = _get(f"/api/v3/quote/{ticker}")
    row = data[0] if data else {}
    return {"data": row, "source": SOURCE_NAME, "endpoint": f"/api/v3/quote/{ticker}"}


def etf_profile(ticker: str) -> dict:
    """AUM, expense ratio, inception date, asset class hints."""
    data = _get(f"/api/v3/etf-info", params={"symbol": ticker})
    row = data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})
    return {"data": row, "source": SOURCE_NAME, "endpoint": "/api/v3/etf-info"}


def etf_holdings(ticker: str) -> dict:
    """Holdings breakdown with weights."""
    data = _get(f"/api/v3/etf-holder/{ticker}")
    return {"data": data, "source": SOURCE_NAME, "endpoint": f"/api/v3/etf-holder/{ticker}"}


def etf_sector_weights(ticker: str) -> dict:
    data = _get(f"/api/v3/etf-sector-weightings/{ticker}")
    return {"data": data, "source": SOURCE_NAME, "endpoint": f"/api/v3/etf-sector-weightings/{ticker}"}


def etf_country_weights(ticker: str) -> dict:
    data = _get(f"/api/v3/etf-country-weightings/{ticker}")
    return {"data": data, "source": SOURCE_NAME, "endpoint": f"/api/v3/etf-country-weightings/{ticker}"}


def company_key_metrics(ticker: str) -> dict:
    """Revenue/EBITDA and related figures for a top holding (equity valuation, Section 6)."""
    data = _get(f"/api/v3/key-metrics/{ticker}", params={"limit": 5})
    return {"data": data, "source": SOURCE_NAME, "endpoint": f"/api/v3/key-metrics/{ticker}"}


def company_income_statement(ticker: str) -> dict:
    data = _get(f"/api/v3/income-statement/{ticker}", params={"limit": 5})
    return {"data": data, "source": SOURCE_NAME, "endpoint": f"/api/v3/income-statement/{ticker}"}


def historical_prices(ticker: str, days: int = 30) -> dict:
    data = _get(f"/api/v3/historical-price-full/{ticker}", params={"timeseries": days})
    return {"data": data.get("historical", []), "source": SOURCE_NAME,
            "endpoint": f"/api/v3/historical-price-full/{ticker}"}


def commodity_quote(symbol: str) -> dict:
    """e.g. symbol='GCUSD' for gold futures-equivalent spot."""
    data = _get(f"/api/v3/quote/{symbol}")
    row = data[0] if data else {}
    return {"data": row, "source": SOURCE_NAME, "endpoint": f"/api/v3/quote/{symbol}"}
