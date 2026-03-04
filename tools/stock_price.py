"""
Stock Price Tool — Wraps yfinance data for the LLM agent.
Provides current prices and multi-stock comparison.
"""

from data_sources import yfinance_data


def get_stock_price(symbol: str) -> dict:
    """
    Get current stock price with market timing context.

    Data source priority:
    1. Angel One Market Feeds API → real-time (0 delay) ✅
    2. yfinance → fallback (15 min delay) ⚠️

    Args:
        symbol: NSE stock symbol (e.g. RELIANCE, TCS)

    Returns:
        dict with price data and source info
    """
    # PRIMARY: Angel One real-time
    try:
        from data_sources.angel_realtime import get_angel_manager
        manager = get_angel_manager()
        if manager.is_logged_in:
            result = manager.get_live_price(symbol)
            if result and "error" not in result:
                return result
    except Exception as e:
        print(f"⚠️ Angel One failed → using yfinance: {e}")

    # FALLBACK: yfinance (existing code — unchanged)
    try:
        data = yfinance_data.get_stock_price(symbol)
        data["data_source"] = "yfinance (15 min delayed)"
        return data

    except Exception as e:
        print(f"⚠️ [stock_price.get_stock_price] Error: {e}")
        return {"error": f"Could not fetch price for {symbol}: {str(e)}"}


def compare_stocks(symbols: str) -> list:
    """
    Compare prices of multiple stocks side by side.

    Args:
        symbols: comma-separated stock names, e.g. "TCS,INFY,WIPRO"

    Returns:
        list of price dicts for each stock
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        results = []
        for sym in symbol_list:
            results.append(get_stock_price(sym))
        return results

    except Exception as e:
        print(f"⚠️ [stock_price.compare_stocks] Error: {e}")
        return [{"error": f"Comparison failed: {str(e)}"}]
