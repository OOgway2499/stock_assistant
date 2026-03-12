"""
NSE India Data Source — Free, real-time data from NSE public API.
No API key or registration required.
Provides indices, gainers, losers, option chains, and market status.

Includes yfinance fallback for gainers/losers when NSE blocks requests.
"""

import requests
import time
import yfinance as yf
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

# ── NSE Headers (mimic real browser) ────────────────────────────

NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.nseindia.com/",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


# ── Session Factory ─────────────────────────────────────────────

def create_nse_session() -> requests.Session:
    """
    Create a requests session with proper cookies for NSE India API.
    Steps: homepage → wait → market-data page → wait → ready.
    """
    session = requests.Session()
    session.headers.update(NSE_HEADERS)

    try:
        session.get("https://www.nseindia.com", timeout=15)
        time.sleep(1)
        session.get(
            "https://www.nseindia.com/market-data/live-equity-market",
            timeout=15,
        )
        time.sleep(0.5)
    except Exception:
        pass  # Cookies may still be partially set

    return session


def safe_nse_request(url: str) -> dict | list | None:
    """
    Make a request to NSE API with retry on 401/403.
    Returns parsed JSON or None on failure.
    """
    try:
        session = create_nse_session()
        response = session.get(url, timeout=15)

        if response.status_code == 200:
            return response.json()

        if response.status_code in (401, 403):
            # Retry once with fresh session
            time.sleep(2)
            session = create_nse_session()
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                return response.json()

        return None

    except Exception as e:
        print(f"⚠️ [safe_nse_request] {url}: {e}")
        return None


# ─── Index Data ──────────────────────────────────────────────────


def get_all_indices() -> dict:
    """Fetch all NSE indices data."""
    try:
        data = safe_nse_request("https://www.nseindia.com/api/allIndices")
        if data is None:
            return {"error": "NSE indices data unavailable"}
        return data
    except Exception as e:
        print(f"⚠️ [get_all_indices] Error: {e}")
        return {"error": f"NSE data unavailable: {str(e)}"}


def get_nifty50() -> dict:
    """Get NIFTY 50 index data."""
    try:
        data = get_all_indices()
        if "error" in data:
            return data

        for index in data.get("data", []):
            if index.get("index") == "NIFTY 50":
                return {
                    "index_name": "NIFTY 50",
                    "last_price": index.get("last"),
                    "change": index.get("variation"),
                    "percent_change": index.get("percentChange"),
                    "open": index.get("open"),
                    "high": index.get("high"),
                    "low": index.get("low"),
                    "previous_close": index.get("previousClose"),
                    "yearly_high": index.get("yearHigh"),
                    "yearly_low": index.get("yearLow"),
                    "data_source": "NSE India (real-time)",
                }

        return {"error": "NIFTY 50 data not found in response"}

    except Exception as e:
        print(f"⚠️ [get_nifty50] Error: {e}")
        return {"error": f"NSE data unavailable: {str(e)}"}


def get_index_data(index_name: str) -> dict:
    """Get data for a specific NSE index."""
    try:
        data = get_all_indices()
        if "error" in data:
            return data

        target = index_name.upper()
        for index in data.get("data", []):
            if index.get("index", "").upper() == target:
                return {
                    "index_name": index.get("index"),
                    "last_price": index.get("last"),
                    "change": index.get("variation"),
                    "percent_change": index.get("percentChange"),
                    "open": index.get("open"),
                    "high": index.get("high"),
                    "low": index.get("low"),
                    "previous_close": index.get("previousClose"),
                    "yearly_high": index.get("yearHigh"),
                    "yearly_low": index.get("yearLow"),
                    "data_source": "NSE India (real-time)",
                }

        return {"error": f"Index '{index_name}' not found"}

    except Exception as e:
        print(f"⚠️ [get_index_data] Error: {e}")
        return {"error": f"NSE data unavailable: {str(e)}"}


# ─── Gainers / Losers ───────────────────────────────────────────


def _parse_nse_list(data) -> list:
    """Parse NSE response which can come in multiple formats."""
    if data is None:
        return []

    # Format A: direct list
    if isinstance(data, list):
        return data[:10]

    # Format B/C: dict with various keys
    if isinstance(data, dict):
        if "error" in data:
            return []

        # Try known keys first
        for key in ("NIFTY", "data", "BANKNIFTY", "FO"):
            val = data.get(key)
            if isinstance(val, list) and len(val) > 0:
                return val[:10]

        # Try any list value
        for key, val in data.items():
            if isinstance(val, list) and len(val) > 0:
                return val[:10]

    return []


def _normalize_stock_item(item: dict) -> dict:
    """Normalize NSE stock item to consistent keys."""
    return {
        "symbol": item.get("symbol", item.get("tradingSymbol", "")),
        "company": item.get("meta", {}).get("companyName", item.get("symbol", "")),
        "last_price": item.get("lastPrice", item.get("ltp", item.get("last", 0))),
        "change": item.get("change", 0),
        "percent_change": item.get("pChange", item.get("perChange",
                          item.get("percentChange", 0))),
    }


def _yfinance_fallback_gainers_losers(sort_ascending: bool = False) -> list:
    """
    Fallback: calculate gainers/losers from Nifty 50 stocks using yfinance.
    sort_ascending=False → gainers (biggest positive first)
    sort_ascending=True  → losers  (biggest negative first)
    """
    try:
        nifty50 = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
            "ICICIBANK.NS", "WIPRO.NS", "SBIN.NS", "AXISBANK.NS",
            "BAJFINANCE.NS", "KOTAKBANK.NS", "LT.NS", "TATAMOTORS.NS",
            "MARUTI.NS", "SUNPHARMA.NS", "BHARTIARTL.NS", "ASIANPAINT.NS",
            "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "POWERGRID.NS",
            "NTPC.NS", "ONGC.NS", "HCLTECH.NS", "TECHM.NS", "ADANIENT.NS",
        ]

        data = yf.download(nifty50, period="2d", interval="1d", progress=False)
        if data.empty:
            return []

        close = data["Close"]
        change_pct = close.pct_change().iloc[-1] * 100
        last_prices = close.iloc[-1]

        change_pct = change_pct.dropna().sort_values(ascending=sort_ascending)

        results = []
        for sym in change_pct.index[:10]:
            clean_sym = str(sym).replace(".NS", "")
            pct = round(float(change_pct[sym]), 2)
            price = round(float(last_prices[sym]), 2) if sym in last_prices.index else 0

            if sort_ascending and pct >= 0:
                continue  # Skip non-losers
            if not sort_ascending and pct <= 0:
                continue  # Skip non-gainers

            results.append({
                "symbol": clean_sym,
                "company": clean_sym,
                "last_price": price,
                "change": 0,
                "percent_change": pct,
                "source": "yfinance_fallback",
            })

        return results

    except Exception as e:
        print(f"⚠️ [yfinance_fallback] Error: {e}")
        return []


def get_top_gainers() -> list:
    """
    Get today's top gaining stocks on NSE.
    Falls back to yfinance if NSE API is blocked.
    Always returns a list — never None or dict.
    """
    try:
        # PRIMARY: NSE API
        data = safe_nse_request(
            "https://www.nseindia.com/api/live-analysis-variations?index=gainers"
        )
        items = _parse_nse_list(data)
        if items:
            return [_normalize_stock_item(i) for i in items]

        # FALLBACK: yfinance
        print("⚠️ NSE gainers blocked — using yfinance fallback")
        return _yfinance_fallback_gainers_losers(sort_ascending=False)

    except Exception as e:
        print(f"⚠️ [get_top_gainers] Error: {e}")
        return []


def get_top_losers() -> list:
    """
    Get today's top losing stocks on NSE.
    Falls back to yfinance if NSE API is blocked.
    Always returns a list — never None or dict.
    """
    try:
        # PRIMARY: NSE API
        data = safe_nse_request(
            "https://www.nseindia.com/api/live-analysis-variations?index=losers"
        )
        items = _parse_nse_list(data)
        if items:
            return [_normalize_stock_item(i) for i in items]

        # FALLBACK: yfinance
        print("⚠️ NSE losers blocked — using yfinance fallback")
        return _yfinance_fallback_gainers_losers(sort_ascending=True)

    except Exception as e:
        print(f"⚠️ [get_top_losers] Error: {e}")
        return []


# ─── Option Chain ────────────────────────────────────────────────


def get_option_chain(symbol: str) -> dict:
    """Get option chain data for a stock or index."""
    try:
        session = create_nse_session()
        indices = ["NIFTY", "BANKNIFTY", "NIFTY BANK", "FINNIFTY"]
        if symbol.upper() in indices:
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol.upper()}"
        else:
            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"

        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        records = data.get("records", {})
        filtered = data.get("filtered", {})

        return {
            "symbol": symbol.upper(),
            "expiry_dates": records.get("expiryDates", [])[:5],
            "strike_prices": records.get("strikePrices", [])[:20],
            "total_ce_oi": filtered.get("CE", {}).get("totOI"),
            "total_pe_oi": filtered.get("PE", {}).get("totOI"),
            "total_ce_volume": filtered.get("CE", {}).get("totVol"),
            "total_pe_volume": filtered.get("PE", {}).get("totVol"),
            "pcr": (
                round(filtered["PE"]["totOI"] / filtered["CE"]["totOI"], 2)
                if filtered.get("PE", {}).get("totOI") and filtered.get("CE", {}).get("totOI")
                else None
            ),
            "data_source": "NSE India (real-time)",
        }

    except Exception as e:
        print(f"⚠️ [get_option_chain] Error: {e}")
        return {"error": f"Option chain not available for {symbol}: {str(e)}"}


# ─── Market Status ───────────────────────────────────────────────


def get_market_status() -> dict:
    """Check whether the NSE market is currently open or closed."""
    try:
        data = safe_nse_request("https://www.nseindia.com/api/marketStatus")

        if data is not None:
            statuses = []
            for market in data.get("marketState", []):
                statuses.append({
                    "market": market.get("market"),
                    "status": market.get("marketStatus"),
                    "trade_date": market.get("tradeDate"),
                })
            return {"market_statuses": statuses}

        # Fallback: calculate from IST time
        now = datetime.now(IST)
        weekday = now.weekday()
        time_val = now.hour * 60 + now.minute

        if weekday >= 5:
            state = "Close"
            reason = "Weekend"
        elif 555 <= time_val <= 930:
            state = "Open"
            reason = "Regular trading"
        else:
            state = "Close"
            reason = "Outside market hours"

        return {
            "market_statuses": [{
                "market": "Capital Market",
                "status": state,
                "trade_date": now.strftime("%d-%b-%Y"),
            }],
            "source": "calculated_from_time",
        }

    except Exception as e:
        print(f"⚠️ [get_market_status] Error: {e}")
        return {"error": f"Market status unavailable: {str(e)}"}


# ─── 52-Week High / Low ─────────────────────────────────────────


def get_52week_high_low() -> dict:
    """Get stocks hitting 52-week highs today."""
    try:
        data = safe_nse_request(
            "https://www.nseindia.com/api/live-analysis-variations?index=new52high"
        )

        items = _parse_nse_list(data)
        results = [_normalize_stock_item(i) for i in items]

        return {"52_week_highs": results, "count": len(results)}

    except Exception as e:
        print(f"⚠️ [get_52week_high_low] Error: {e}")
        return {"error": f"52-week data unavailable: {str(e)}"}
