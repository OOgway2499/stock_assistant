"""
Technical Analysis Tool — RSI, MACD, SMA, EMA, Bollinger Bands, ATR.
Uses pandas_ta for indicator calculation with human-readable signals.
"""

import pandas as pd
from data_sources import yfinance_data

# Try to import pandas_ta; fall back gracefully
try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False


def get_technicals(symbol: str, period: str = "3mo") -> dict:
    """
    Calculate technical indicators for a stock and return human-readable signals.

    Args:
        symbol: NSE stock symbol
        period: lookback period — 1mo, 3mo, 6mo, 1y (default 3mo)

    Returns:
        dict with indicator values and plain-English signals
    """
    try:
        df = None

        # PRIMARY: Angel One Historical API
        try:
            from data_sources.angel_realtime import get_angel_manager
            manager = get_angel_manager()
            if manager.is_logged_in:
                candles = manager.get_historical_candles(symbol, "ONE_DAY")
                if candles and len(candles) > 50:
                    df = pd.DataFrame(
                        candles,
                        columns=["timestamp", "open", "high", "low", "close", "volume"],
                    )
                    df.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
                    df["Date"] = pd.to_datetime(df["Date"])
                    df.set_index("Date", inplace=True)
                    print(f"📊 Using Angel One historical data for {symbol} ({len(df)} candles)")
        except Exception as e:
            print(f"⚠️ Angel One historical failed → using yfinance: {e}")
            df = None

        # FALLBACK: yfinance (existing code — unchanged)
        if df is None:
            df = yfinance_data.get_stock_history(symbol, period=period, interval="1d")

        if isinstance(df, dict) and "error" in df:
            return df
        if df is None or df.empty:
            return {"error": f"No historical data for {symbol}"}

        if not HAS_PANDAS_TA:
            return {"error": "pandas_ta not installed. Run: pip install pandas-ta"}

        # 2. Calculate indicators
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.sma(length=200, append=True)
        df.ta.ema(length=9, append=True)
        df.ta.ema(length=21, append=True)
        df.ta.bbands(length=20, std=2, append=True)
        df.ta.atr(length=14, append=True)

        # 3. Get latest values
        latest = df.iloc[-1]
        close = round(float(latest["Close"]), 2)

        def safe(col):
            """Safely extract and round a column value."""
            for c in df.columns:
                if col.lower() in c.lower():
                    val = latest.get(c)
                    if pd.notna(val):
                        return round(float(val), 2)
            return None

        rsi = safe("RSI_14")
        macd = safe("MACD_12_26_9")
        macd_signal = safe("MACDs_12_26_9")
        macd_hist = safe("MACDh_12_26_9")
        sma20 = safe("SMA_20")
        sma50 = safe("SMA_50")
        sma200 = safe("SMA_200")
        ema9 = safe("EMA_9")
        ema21 = safe("EMA_21")
        bbl = safe("BBL_20_2")
        bbm = safe("BBM_20_2")
        bbu = safe("BBU_20_2")
        atr = safe("ATR")

        # 4. Human-readable signals
        # RSI signal
        if rsi is not None:
            if rsi > 70:
                rsi_signal = "🔴 Overbought — stock may pullback soon"
            elif rsi > 60:
                rsi_signal = "🟡 Mildly overbought — watch carefully"
            elif rsi > 40:
                rsi_signal = "⚪ Neutral zone — no strong signal"
            elif rsi > 30:
                rsi_signal = "🟡 Mildly oversold — possible bounce"
            else:
                rsi_signal = "🟢 Oversold — possible buying opportunity"
        else:
            rsi_signal = "⚪ RSI data not available"

        # Trend signal
        if sma50 is not None and sma200 is not None:
            if close > sma50 > sma200:
                trend_signal = "📈 Strong Uptrend"
            elif close > sma50:
                trend_signal = "📈 Uptrend"
            elif close < sma50 < sma200:
                trend_signal = "📉 Strong Downtrend"
            elif close < sma50:
                trend_signal = "📉 Downtrend"
            else:
                trend_signal = "⚪ Sideways"
        else:
            trend_signal = "⚪ Not enough data for trend signal"

        # MACD signal
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                macd_text = "🟢 Bullish momentum"
            else:
                macd_text = "🔴 Bearish momentum"
        else:
            macd_text = "⚪ MACD data not available"

        return {
            "symbol": symbol.upper(),
            "current_price": close,
            "period": period,
            "indicators": {
                "RSI_14": rsi,
                "MACD": macd,
                "MACD_Signal": macd_signal,
                "MACD_Histogram": macd_hist,
                "SMA_20": sma20,
                "SMA_50": sma50,
                "SMA_200": sma200,
                "EMA_9": ema9,
                "EMA_21": ema21,
                "Bollinger_Lower": bbl,
                "Bollinger_Mid": bbm,
                "Bollinger_Upper": bbu,
                "ATR_14": atr,
            },
            "signals": {
                "rsi_signal": rsi_signal,
                "trend_signal": trend_signal,
                "macd_signal": macd_text,
            },
            "data_source": "yfinance + pandas_ta",
        }

    except Exception as e:
        print(f"⚠️ [technicals.get_technicals] Error: {e}")
        return {"error": f"Technical analysis failed for {symbol}: {str(e)}"}
