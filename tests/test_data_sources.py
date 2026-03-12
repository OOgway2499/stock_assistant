"""
Test Data Sources — yfinance, NSE India, Angel One.
Each test is independent with 30s timeout.
"""

import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════
# TEST: yfinance
# ═══════════════════════════════════════════════════════════════

class TestYfinance:
    """Test yfinance data source — free, 15 min delayed."""

    @pytest.mark.timeout(30)
    def test_get_known_stock_price(self):
        from data_sources.yfinance_data import get_stock_price
        result = get_stock_price("RELIANCE")
        assert "error" not in result, f"Error: {result.get('error')}"
        assert result["current_price"] is not None
        assert result["current_price"] > 0
        assert isinstance(result["current_price"], (int, float))
        assert "symbol" in result
        print(f"   ✅ Reliance price = ₹{result['current_price']}")

    @pytest.mark.timeout(30)
    def test_get_tcs_price(self):
        from data_sources.yfinance_data import get_stock_price
        result = get_stock_price("TCS")
        assert "error" not in result, f"Error: {result.get('error')}"
        assert result["current_price"] > 0
        print(f"   ✅ TCS price = ₹{result['current_price']}")

    @pytest.mark.timeout(30)
    def test_get_invalid_stock(self):
        from data_sources.yfinance_data import get_stock_price
        result = get_stock_price("INVALIDSYMBOL123XYZ")
        assert "error" in result
        print("   ✅ Invalid stock handled correctly")

    @pytest.mark.timeout(30)
    def test_historical_data(self):
        from data_sources.yfinance_data import get_stock_history
        result = get_stock_history("INFY", period="1mo", interval="1d")
        assert not isinstance(result, dict) or "error" not in result, \
            f"Error: {result.get('error') if isinstance(result, dict) else 'N/A'}"
        assert hasattr(result, '__len__') and len(result) > 10
        assert "Close" in result.columns
        assert "Volume" in result.columns
        print(f"   ✅ Historical data: {len(result)} rows returned")

    @pytest.mark.timeout(30)
    def test_fundamentals(self):
        from data_sources.yfinance_data import get_fundamentals
        result = get_fundamentals("TCS")
        assert "error" not in result, f"Error: {result.get('error')}"
        assert result.get("pe_ratio") is not None or result.get("market_cap") is not None
        print(f"   ✅ TCS PE Ratio = {result.get('pe_ratio')}")
        print(f"   ✅ TCS Market Cap = ₹{result.get('market_cap_crores')} Cr")

    @pytest.mark.timeout(60)
    def test_multiple_stocks(self):
        from data_sources.yfinance_data import get_stock_price
        stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN"]
        for sym in stocks:
            result = get_stock_price(sym)
            assert "error" not in result, f"Error for {sym}: {result.get('error')}"
            assert result["current_price"] > 0
            print(f"   ✅ {sym} = ₹{result['current_price']}")


# ═══════════════════════════════════════════════════════════════
# TEST: NSE India
# ═══════════════════════════════════════════════════════════════

class TestNSEIndia:
    """Test NSE India public API — free, real-time."""

    @pytest.mark.timeout(30)
    def test_nse_connection(self):
        from data_sources.nse_data import get_nifty50
        result = get_nifty50()
        assert "error" not in result, f"Error: {result.get('error')}"
        assert result.get("last_price") is not None
        assert result["last_price"] > 0
        print(f"   ✅ Nifty 50 = {result['last_price']}")

    @pytest.mark.timeout(45)
    def test_top_gainers(self):
        from data_sources.nse_data import get_top_gainers
        result = get_top_gainers()

        # Must return a list — never None or dict
        assert result is not None, "get_top_gainers returned None"
        assert isinstance(result, list), f"Expected list, got {type(result)}"

        if len(result) > 0:
            first = result[0]
            symbol = first.get("symbol", first.get("tradingSymbol", "Unknown"))
            change = first.get("percent_change", first.get("pChange", 0))
            print(f"   ✅ Top gainer = {symbol} +{change}%")
            print(f"   Source: {first.get('source', 'NSE')}")
        else:
            print("   ⚠️ No gainers data — market may be closed (acceptable)")

        print(f"   ✅ test_top_gainers: PASSED ({len(result)} items)")

    @pytest.mark.timeout(45)
    def test_top_losers(self):
        from data_sources.nse_data import get_top_losers
        result = get_top_losers()

        assert result is not None, "get_top_losers returned None"
        assert isinstance(result, list), f"Expected list, got {type(result)}"

        if len(result) > 0:
            first = result[0]
            symbol = first.get("symbol", first.get("tradingSymbol", "Unknown"))
            change = first.get("percent_change", first.get("pChange", 0))
            print(f"   ✅ Top loser = {symbol} {change}%")
        else:
            print("   ⚠️ No losers data — market may be closed (acceptable)")

        print(f"   ✅ test_top_losers: PASSED ({len(result)} items)")

    @pytest.mark.timeout(30)
    def test_market_status(self):
        from data_sources.nse_data import get_market_status
        result = get_market_status()
        assert "error" not in result, f"Error: {result.get('error')}"
        print("   ✅ Market status fetched successfully")

    @pytest.mark.timeout(30)
    def test_all_indices(self):
        from data_sources.nse_data import get_all_indices
        result = get_all_indices()
        assert "error" not in result, f"Error: {result.get('error')}"
        data_list = result.get("data", [])
        assert len(data_list) > 5
        print(f"   ✅ {len(data_list)} indices fetched")


# ═══════════════════════════════════════════════════════════════
# TEST: Angel One
# ═══════════════════════════════════════════════════════════════

class TestAngelOne:
    """Test Angel One SmartAPI — skipped if not configured."""

    def _is_configured(self):
        api_key = os.getenv("ANGEL_FEEDS_API_KEY") or os.getenv("ANGEL_API_KEY", "")
        totp = os.getenv("ANGEL_TOTP_SECRET", "")
        mpin = os.getenv("ANGEL_PASSWORD", "")
        client = os.getenv("ANGEL_CLIENT_ID", "")

        placeholders = ("your_", "paste_", "enter_", "xxx", "")
        if any(api_key.lower().startswith(p) for p in placeholders if p):
            return False
        if any(totp.lower().startswith(p) for p in placeholders if p):
            return False
        return bool(api_key and totp and mpin and client)

    @pytest.mark.timeout(30)
    def test_angel_login(self):
        if not self._is_configured():
            pytest.skip(
                "Angel One not configured — "
                "set ANGEL_FEEDS_API_KEY, ANGEL_TOTP_SECRET, "
                "ANGEL_PASSWORD, ANGEL_CLIENT_ID in .env"
            )

        from data_sources.angel_realtime import AngelOneManager
        manager = AngelOneManager()
        result = manager.login()

        if result:
            assert manager.is_logged_in is True
            assert manager.auth_token is not None
            print("   ✅ Angel One Login Successful")
            manager.logout()
        else:
            error = getattr(manager, "login_error", "Unknown error")
            pytest.fail(
                f"Angel One login failed: {error}\n"
                "Fixes:\n"
                "1. Re-enable TOTP in Angel One app\n"
                "2. Verify ANGEL_PASSWORD is 4-digit MPIN\n"
                "3. Recreate app on smartapi.angelbroking.com"
            )

    @pytest.mark.timeout(30)
    def test_angel_live_price(self):
        if not self._is_configured():
            pytest.skip("Angel One not configured")

        from data_sources.angel_realtime import get_angel_manager
        manager = get_angel_manager()
        if not manager.is_logged_in:
            pytest.skip("Angel One not logged in")
        result = manager.get_live_price("RELIANCE")
        assert result is not None
        assert "error" not in result
        print(f"   ✅ Reliance Live = ₹{result.get('currentPrice', result.get('ltp'))}")

    @pytest.mark.timeout(30)
    def test_angel_historical(self):
        if not self._is_configured():
            pytest.skip("Angel One not configured")

        from data_sources.angel_realtime import get_angel_manager
        manager = get_angel_manager()
        if not manager.is_logged_in:
            pytest.skip("Angel One not logged in")
        candles = manager.get_historical_candles("TCS", "ONE_DAY")
        assert candles is not None
        assert len(candles) > 20
        print(f"   ✅ Angel One historical: {len(candles)} candles")

    @pytest.mark.timeout(30)
    def test_angel_fallback(self):
        """Even if Angel One fails, yfinance fallback should work."""
        from tools.stock_price import get_stock_price
        result = get_stock_price("RELIANCE")
        assert result is not None
        assert "error" not in result
        assert result.get("current_price", 0) > 0
        print(f"   ✅ Fallback works — ₹{result['current_price']} via {result.get('data_source')}")
