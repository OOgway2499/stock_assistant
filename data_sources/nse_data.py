"""
NSE India Data Source — Free, real-time data from NSE public API.
No API key or registration required.
Provides indices, gainers, losers, option chains, and market status.
"""

import requests


def create_nse_session() -> requests.Session:
    """
    Create a requests session with proper headers and cookies for NSE India API.
    NSE requires a valid session cookie before API calls will work.

    Returns:
        requests.Session with cookies set
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com",
    })

    # Hit the homepage to get session cookies
    try:
        session.get("https://www.nseindia.com", timeout=10)
    except Exception:
        pass  # Cookies may still be partially set

    return session


# ─── Index Data ──────────────────────────────────────────────────


def get_all_indices() -> dict:
    """
    Fetch all NSE indices data.

    Returns:
        dict with full indices response or {"error": ...}
    """
    try:
        session = create_nse_session()
        response = session.get(
            "https://www.nseindia.com/api/allIndices",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"⚠️ [get_all_indices] Error: {e}")
        return {"error": f"NSE data unavailable: {str(e)}"}


def get_nifty50() -> dict:
    """
    Get NIFTY 50 index data.

    Returns:
        dict with Nifty 50 metrics or {"error": ...}
    """
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
    """
    Get data for a specific NSE index.

    Args:
        index_name: e.g. "NIFTY BANK", "NIFTY IT", "NIFTY PHARMA"

    Returns:
        dict with index metrics or {"error": ...}
    """
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


def get_top_gainers() -> list:
    """
    Get today's top gaining stocks on NSE.

    Returns:
        list of top 10 gainers or {"error": ...}
    """
    try:
        session = create_nse_session()
        response = session.get(
            "https://www.nseindia.com/api/live-analysis-variations?index=gainers",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        gainers = []
        for stock in data.get("NIFTY", data.get("data", []))[:10]:
            gainers.append({
                "symbol": stock.get("symbol"),
                "company": stock.get("meta", {}).get("companyName", stock.get("symbol")),
                "last_price": stock.get("lastPrice"),
                "change": stock.get("change"),
                "percent_change": stock.get("pChange"),
            })

        return gainers if gainers else {"error": "No gainers data available"}

    except Exception as e:
        print(f"⚠️ [get_top_gainers] Error: {e}")
        return {"error": f"NSE data unavailable: {str(e)}"}


def get_top_losers() -> list:
    """
    Get today's top losing stocks on NSE.

    Returns:
        list of top 10 losers or {"error": ...}
    """
    try:
        session = create_nse_session()
        response = session.get(
            "https://www.nseindia.com/api/live-analysis-variations?index=losers",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        losers = []
        for stock in data.get("NIFTY", data.get("data", []))[:10]:
            losers.append({
                "symbol": stock.get("symbol"),
                "company": stock.get("meta", {}).get("companyName", stock.get("symbol")),
                "last_price": stock.get("lastPrice"),
                "change": stock.get("change"),
                "percent_change": stock.get("pChange"),
            })

        return losers if losers else {"error": "No losers data available"}

    except Exception as e:
        print(f"⚠️ [get_top_losers] Error: {e}")
        return {"error": f"NSE data unavailable: {str(e)}"}


# ─── Option Chain ────────────────────────────────────────────────


def get_option_chain(symbol: str) -> dict:
    """
    Get option chain data for a stock or index.

    Args:
        symbol: Stock symbol (e.g. RELIANCE) or index (NIFTY, BANKNIFTY)

    Returns:
        dict with option chain data or {"error": ...}
    """
    try:
        session = create_nse_session()

        # Use different endpoint for indices vs equities
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
    """
    Check whether the NSE market is currently open or closed.

    Returns:
        dict with market status or {"error": ...}
    """
    try:
        session = create_nse_session()
        response = session.get(
            "https://www.nseindia.com/api/marketStatus",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        statuses = []
        for market in data.get("marketState", []):
            statuses.append({
                "market": market.get("market"),
                "status": market.get("marketStatus"),
                "trade_date": market.get("tradeDate"),
            })

        return {"market_statuses": statuses}

    except Exception as e:
        print(f"⚠️ [get_market_status] Error: {e}")
        return {"error": f"Market status unavailable: {str(e)}"}


# ─── 52-Week High / Low ─────────────────────────────────────────


def get_52week_high_low() -> dict:
    """
    Get stocks hitting 52-week highs today.

    Returns:
        dict with stocks at 52-week highs or {"error": ...}
    """
    try:
        session = create_nse_session()
        response = session.get(
            "https://www.nseindia.com/api/live-analysis-variations?index=new52high",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for stock in data.get("data", [])[:15]:
            results.append({
                "symbol": stock.get("symbol"),
                "last_price": stock.get("lastPrice"),
                "change": stock.get("change"),
                "percent_change": stock.get("pChange"),
            })

        return {"52_week_highs": results, "count": len(results)}

    except Exception as e:
        print(f"⚠️ [get_52week_high_low] Error: {e}")
        return {"error": f"52-week data unavailable: {str(e)}"}
