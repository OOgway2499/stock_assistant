"""
yfinance Data Source — Free stock data with zero API keys.
Provides prices, history, fundamentals, and search for NSE/BSE stocks.
Data has ~15 minute delay from live market.
"""

import yfinance as yf


def get_stock_price(symbol: str) -> dict:
    """
    Get current stock price and key metrics for an NSE/BSE stock.

    Args:
        symbol: NSE stock symbol (e.g. RELIANCE, TCS, INFY)

    Returns:
        dict with price data or {"error": ...} on failure
    """
    try:
        # Try NSE first, then BSE as fallback
        for suffix in [".NS", ".BO"]:
            ticker = yf.Ticker(symbol.upper() + suffix)
            info = ticker.info

            # Skip if no valid data
            if not info or info.get("regularMarketPrice") is None:
                continue

            current_price = info.get("regularMarketPrice") or info.get("currentPrice")
            previous_close = info.get("regularMarketPreviousClose") or info.get("previousClose")

            change = None
            change_percent = None
            if current_price and previous_close:
                change = round(current_price - previous_close, 2)
                change_percent = round((change / previous_close) * 100, 2)

            return {
                "symbol": symbol.upper(),
                "exchange": "NSE" if suffix == ".NS" else "BSE",
                "company_name": info.get("longName") or info.get("shortName", symbol),
                "current_price": current_price,
                "open": info.get("regularMarketOpen") or info.get("open"),
                "day_high": info.get("regularMarketDayHigh") or info.get("dayHigh"),
                "day_low": info.get("regularMarketDayLow") or info.get("dayLow"),
                "previous_close": previous_close,
                "volume": info.get("regularMarketVolume") or info.get("volume"),
                "change": change,
                "change_percent": change_percent,
                "data_source": "yfinance (15 min delayed)",
            }

        return {"error": f"No data found for {symbol}. Check the symbol and try again."}

    except Exception as e:
        print(f"⚠️ [get_stock_price] Error: {e}")
        return {"error": f"Data not available for {symbol}: {str(e)}"}


def get_stock_history(symbol: str, period: str = "3mo", interval: str = "1d"):
    """
    Get historical OHLCV data for a stock.

    Args:
        symbol:   NSE stock symbol
        period:   1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
        interval: 1m, 5m, 15m, 1h, 1d, 1wk, 1mo

    Returns:
        pandas DataFrame with OHLCV columns, or {"error": ...}
    """
    try:
        for suffix in [".NS", ".BO"]:
            ticker = yf.Ticker(symbol.upper() + suffix)
            df = ticker.history(period=period, interval=interval)

            if df is not None and not df.empty:
                return df

        return {"error": f"No historical data found for {symbol}"}

    except Exception as e:
        print(f"⚠️ [get_stock_history] Error: {e}")
        return {"error": f"History not available for {symbol}: {str(e)}"}


def get_fundamentals(symbol: str) -> dict:
    """
    Get fundamental data for a stock — PE, EPS, market cap, etc.

    Args:
        symbol: NSE stock symbol

    Returns:
        dict with fundamental metrics or {"error": ...}
    """
    try:
        for suffix in [".NS", ".BO"]:
            ticker = yf.Ticker(symbol.upper() + suffix)
            info = ticker.info

            if not info or info.get("regularMarketPrice") is None:
                continue

            market_cap = info.get("marketCap")
            market_cap_crores = round(market_cap / 10_000_000, 2) if market_cap else None

            return {
                "symbol": symbol.upper(),
                "company_name": info.get("longName") or info.get("shortName", symbol),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "current_price": info.get("regularMarketPrice") or info.get("currentPrice"),
                "market_cap": market_cap,
                "market_cap_crores": market_cap_crores,
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "eps": info.get("trailingEps"),
                "dividend_yield": info.get("dividendYield"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
                "debt_to_equity": info.get("debtToEquity"),
                "roe": info.get("returnOnEquity"),
                "revenue_growth": info.get("revenueGrowth"),
                "profit_margins": info.get("profitMargins"),
                "beta": info.get("beta"),
                "data_source": "yfinance",
            }

        return {"error": f"No fundamental data found for {symbol}"}

    except Exception as e:
        print(f"⚠️ [get_fundamentals] Error: {e}")
        return {"error": f"Fundamentals not available for {symbol}: {str(e)}"}


def get_multiple_stocks(symbols: list) -> list:
    """
    Get prices for multiple stocks at once.

    Args:
        symbols: list of NSE stock symbols

    Returns:
        list of price dicts
    """
    results = []
    for symbol in symbols:
        results.append(get_stock_price(symbol.strip()))
    return results


def search_stock(query: str) -> dict:
    """
    Search for Indian stocks by name or keyword.

    Args:
        query: company name or partial symbol

    Returns:
        dict with matching stocks or {"error": ...}
    """
    try:
        search = yf.Search(query)
        quotes = search.quotes if hasattr(search, "quotes") else []

        # Filter for Indian exchanges
        indian_stocks = [
            q for q in quotes
            if q.get("exchange", "") in ("NSI", "NSE", "BOM", "BSE", "IN")
            or q.get("exchDisp", "") in ("NSE", "BSE")
        ]

        if not indian_stocks:
            # Return all results if no Indian filter matches
            indian_stocks = quotes[:5]

        results = []
        for q in indian_stocks[:5]:
            results.append({
                "symbol": q.get("symbol", ""),
                "name": q.get("longname") or q.get("shortname", ""),
                "exchange": q.get("exchDisp", q.get("exchange", "")),
                "type": q.get("quoteType", ""),
            })

        return {"results": results, "count": len(results)}

    except Exception as e:
        print(f"⚠️ [search_stock] Error: {e}")
        return {"error": f"Search failed: {str(e)}"}
