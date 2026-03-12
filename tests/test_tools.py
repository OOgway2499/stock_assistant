"""
Test Tools — stock price, technicals, fundamentals, news, indices.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════
# TEST: Stock Price Tool
# ═══════════════════════════════════════════════════════════════

class TestStockPriceTool:

    @pytest.mark.timeout(30)
    def test_price_returns_dict(self):
        from tools.stock_price import get_stock_price
        result = get_stock_price("RELIANCE")
        assert isinstance(result, dict)
        assert "error" not in result
        assert "symbol" in result
        assert "current_price" in result
        assert "data_source" in result
        print("   ✅ Stock price tool returns correct format")

    @pytest.mark.timeout(30)
    def test_price_data_source_label(self):
        from tools.stock_price import get_stock_price
        result = get_stock_price("TCS")
        assert "error" not in result
        assert "data_source" in result
        assert result["data_source"] != ""
        print(f"   ✅ Data source = {result['data_source']}")

    @pytest.mark.timeout(60)
    def test_compare_stocks(self):
        from tools.stock_price import compare_stocks
        result = compare_stocks("TCS,INFY,WIPRO")
        assert isinstance(result, list)
        assert len(result) == 3
        for item in result:
            assert "current_price" in item or "error" in item
        print("   ✅ Compare stocks returns 3 results")


# ═══════════════════════════════════════════════════════════════
# TEST: Technicals Tool
# ═══════════════════════════════════════════════════════════════

class TestTechnicalsTool:

    @pytest.mark.timeout(30)
    def test_technicals_returns_rsi(self):
        from tools.technicals import get_technicals
        result = get_technicals("RELIANCE")
        assert "error" not in result, f"Error: {result.get('error')}"
        rsi = result.get("indicators", {}).get("RSI_14")
        assert rsi is not None, "RSI not found"
        assert 0 <= rsi <= 100
        print(f"   ✅ Reliance RSI = {rsi}")

    @pytest.mark.timeout(30)
    def test_technicals_returns_macd(self):
        from tools.technicals import get_technicals
        result = get_technicals("TCS")
        assert "error" not in result, f"Error: {result.get('error')}"
        indicators = result.get("indicators", {})
        assert indicators.get("MACD") is not None, "MACD not found"
        print(f"   ✅ TCS MACD = {indicators['MACD']}")

    @pytest.mark.timeout(30)
    def test_technicals_returns_trend(self):
        from tools.technicals import get_technicals
        result = get_technicals("INFY")
        assert "error" not in result, f"Error: {result.get('error')}"
        signals = result.get("signals", {})
        trend = signals.get("trend_signal", "")
        assert trend != "", "Trend signal empty"
        print(f"   ✅ INFY Trend = {trend}")

    @pytest.mark.timeout(30)
    def test_technicals_signals(self):
        from tools.technicals import get_technicals
        result = get_technicals("HDFCBANK")
        assert "error" not in result, f"Error: {result.get('error')}"
        signals = result.get("signals", {})
        indicators = result.get("indicators", {})
        assert "rsi_signal" in signals
        assert indicators.get("SMA_20") is not None
        print("   ✅ All technical signals present")


# ═══════════════════════════════════════════════════════════════
# TEST: Fundamentals Tool
# ═══════════════════════════════════════════════════════════════

class TestFundamentalsTool:

    @pytest.mark.timeout(30)
    def test_fundamentals_pe_ratio(self):
        from tools.fundamentals import get_fundamentals_tool
        result = get_fundamentals_tool("TCS")
        assert "error" not in result, f"Error: {result.get('error')}"
        pe = result.get("pe_ratio")
        signals = result.get("signals", {})
        print(f"   ✅ TCS PE = {pe} → {signals.get('pe_signal', 'N/A')}")

    @pytest.mark.timeout(30)
    def test_fundamentals_market_cap(self):
        from tools.fundamentals import get_fundamentals_tool
        result = get_fundamentals_tool("RELIANCE")
        assert "error" not in result, f"Error: {result.get('error')}"
        cap = result.get("market_cap_crores")
        assert cap is not None and cap > 0
        print(f"   ✅ Reliance Market Cap = ₹{cap} Cr")

    @pytest.mark.timeout(30)
    def test_fundamentals_signals(self):
        from tools.fundamentals import get_fundamentals_tool
        result = get_fundamentals_tool("HDFCBANK")
        assert "error" not in result, f"Error: {result.get('error')}"
        signals = result.get("signals", {})
        assert "debt_signal" in signals
        assert "roe_signal" in signals
        print("   ✅ All fundamental signals present")


# ═══════════════════════════════════════════════════════════════
# TEST: News Tool
# ═══════════════════════════════════════════════════════════════

class TestNewsTool:

    @pytest.mark.timeout(30)
    def test_news_returns_list(self):
        from tools.news import get_news
        result = get_news("Reliance Industries")
        assert isinstance(result, list)
        assert len(result) > 0
        print(f"   ✅ {len(result)} news articles fetched")

    @pytest.mark.timeout(30)
    def test_news_has_required_fields(self):
        from tools.news import get_news
        result = get_news("TCS quarterly results")
        assert len(result) > 0
        first = result[0]
        assert "title" in first
        assert "published" in first
        assert "source" in first
        assert "link" in first
        print(f"   ✅ Latest news: {first['title'][:60]}...")

    @pytest.mark.timeout(30)
    def test_market_news(self):
        from tools.news import get_market_news
        result = get_market_news()
        assert isinstance(result, list)
        assert len(result) >= 3
        print(f"   ✅ Market news: {len(result)} articles")


# ═══════════════════════════════════════════════════════════════
# TEST: Indices Tools
# ═══════════════════════════════════════════════════════════════

class TestIndicesTools:

    @pytest.mark.timeout(30)
    def test_market_overview(self):
        from tools.indices import get_market_overview
        result = get_market_overview()
        assert "error" not in result, f"Error: {result.get('error')}"
        assert "nifty_50" in result
        nifty = result["nifty_50"]
        if isinstance(nifty, dict) and "error" not in nifty:
            print(f"   ✅ Nifty 50 = {nifty.get('last_price')}")
        else:
            print("   ✅ Market overview returned (NSE may be rate-limiting)")
        if isinstance(result.get("top_gainers"), list) and len(result["top_gainers"]) > 0:
            print(f"   ✅ Top gainer = {result['top_gainers'][0].get('symbol')}")

    @pytest.mark.timeout(30)
    def test_sector_performance(self):
        from tools.indices import get_nifty_sectors
        result = get_nifty_sectors()
        assert "error" not in result, f"Error: {result.get('error')}"
        # Count actual sector keys (exclude data_source)
        sector_keys = [k for k in result.keys() if k != "data_source"]
        assert len(sector_keys) >= 5
        print(f"   ✅ {len(sector_keys)} sectors fetched")
