"""
Fundamentals Tool — PE, EPS, Market Cap, Debt, ROE with valuation signals.
"""

from data_sources import yfinance_data


def get_fundamentals_tool(symbol: str) -> dict:
    """
    Get fundamental analysis for a stock with valuation and health signals.

    Args:
        symbol: NSE stock symbol

    Returns:
        dict with fundamentals and human-readable signals
    """
    try:
        data = yfinance_data.get_fundamentals(symbol)

        if "error" in data:
            return data

        # ── PE Ratio Valuation Signal ────────────────────────────
        pe = data.get("pe_ratio")
        if pe is not None:
            if pe < 10:
                pe_signal = "🟢 Very undervalued (or declining business)"
            elif pe < 15:
                pe_signal = "🟢 Potentially undervalued"
            elif pe < 25:
                pe_signal = "⚪ Fairly valued"
            elif pe < 40:
                pe_signal = "🟡 Slightly overvalued"
            else:
                pe_signal = "🔴 Highly overvalued"
        else:
            pe_signal = "⚪ PE data not available"

        # ── Debt-to-Equity Signal ────────────────────────────────
        de = data.get("debt_to_equity")
        if de is not None:
            # yfinance returns D/E as a percentage (e.g. 50 = 0.5x)
            de_ratio = de / 100 if de > 5 else de  # Normalize
            if de_ratio < 0.5:
                debt_signal = "🟢 Low debt — financially strong"
            elif de_ratio < 1.0:
                debt_signal = "🟡 Moderate debt"
            else:
                debt_signal = "🔴 High debt — risk factor"
        else:
            debt_signal = "⚪ Debt data not available"

        # ── ROE Signal ───────────────────────────────────────────
        roe = data.get("roe")
        if roe is not None:
            roe_pct = roe * 100 if roe < 1 else roe  # Normalize
            if roe_pct > 20:
                roe_signal = "🟢 Excellent returns"
            elif roe_pct > 10:
                roe_signal = "🟡 Good returns"
            else:
                roe_signal = "🔴 Low returns"
        else:
            roe_signal = "⚪ ROE data not available"

        # ── Build response ───────────────────────────────────────
        data["signals"] = {
            "pe_signal": pe_signal,
            "debt_signal": debt_signal,
            "roe_signal": roe_signal,
        }

        return data

    except Exception as e:
        print(f"⚠️ [fundamentals.get_fundamentals_tool] Error: {e}")
        return {"error": f"Fundamental analysis failed for {symbol}: {str(e)}"}
