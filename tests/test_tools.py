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

    def test_moneycontrol_is_primary_source(self):
        """
        Verify MoneyControl is the primary 
        news source and returns articles
        """
        from tools.news import fetch_moneycontrol
        result = fetch_moneycontrol(
            "Reliance TCS Nifty",
            ["market"]
        )
        assert isinstance(result, list)
        assert len(result) > 0, (
            "MoneyControl returned no articles!\n"
            "Check internet connection or\n"
            "MC RSS feed URL has changed"
        )
        assert result[0].get("source") == "MoneyControl"
        print(f"✅ MoneyControl PRIMARY: {len(result)} articles")
        print(f"   Latest: {result[0]['title'][:60]}")

    def test_get_news_returns_articles(self):
        """
        Main news function must always return 
        articles from at least one source
        """
        from tools.news import get_news
        result = get_news("Reliance Industries NSE")
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0, (
            "get_news() returned empty list!\n"
            "All 4 sources failed — check internet"
        )
        
        sources = set(a.get("source", "") for a in result)
        print(f"✅ get_news: {len(result)} articles")
        print(f"   Sources: {sources}")
        print(f"   Top: {result[0]['title'][:60]}")

    def test_news_has_required_fields(self):
        """
        Every article must have all required fields
        """
        from tools.news import get_news
        result = get_news("TCS quarterly results")
        
        assert len(result) > 0
        
        for article in result:
            assert "title"     in article, "Missing 'title' field"
            assert "published" in article, "Missing 'published' field"
            assert "source"    in article, "Missing 'source' field"
            assert "link"      in article, "Missing 'link' field"
            assert "summary"   in article, "Missing 'summary' field"
            assert len(article["title"]) > 5, "Title too short"
        
        print(f"✅ All fields present in {len(result)} articles")

    def test_news_no_google_news(self):
        """
        Verify Google News is completely removed.
        No article should have Google as source.
        """
        from tools.news import get_news
        result = get_news("Nifty market today")
        
        for article in result:
            source = article.get("source", "").lower()
            assert "google" not in source, (
                f"Google News still present!\n"
                f"Found source: {article['source']}\n"
                f"Remove Google News completely"
            )
        
        print(f"✅ Google News: Completely removed ✅")

    def test_market_news_moneycontrol(self):
        """
        Market news must use MoneyControl feeds
        """
        from tools.news import get_market_news
        result = get_market_news()
        
        assert isinstance(result, list)
        assert len(result) >= 3, (
            f"Market news has only {len(result)} "
            f"articles — expected at least 3"
        )
        
        # Check MoneyControl is in sources
        sources = [a.get("source", "") for a in result]
        has_mc = any(
            "MoneyControl" in s or "Economic Times" in s
            for s in sources
        )
        assert has_mc, (
            "Market news not from expected sources!\n"
            f"Sources found: {set(sources)}"
        )
        
        print(f"✅ Market news: {len(result)} articles")

    def test_ipo_news(self):
        """
        IPO news from MoneyControl IPO feed
        """
        from tools.news import get_ipo_news
        result = get_ipo_news()
        
        assert isinstance(result, list)
        print(f"✅ IPO news: {len(result)} articles")
        if result:
            print(f"   Latest: {result[0]['title'][:60]}")

    def test_results_news(self):
        """
        Quarterly results news from MoneyControl
        """
        from tools.news import get_results_news
        result = get_results_news()
        
        assert isinstance(result, list)
        print(f"✅ Results news: {len(result)} articles")

    def test_news_caching_works(self):
        """
        Same query twice should return cached result.
        Second call must be faster than first.
        """
        from tools.news import get_news, clear_cache
        import time
        
        clear_cache()
        
        query = "HDFC Bank NSE"
        
        # First call — hits the sources
        start1 = time.time()
        result1 = get_news(query)
        time1   = time.time() - start1
        
        # Second call — should use cache
        start2 = time.time()
        result2 = get_news(query)
        time2   = time.time() - start2
        
        assert result1 == result2, "Cache returned different results!"
        assert time2 < time1, "Cache not working — second call slower!"
        
        print(f"✅ Cache working correctly")
        print(f"   First call : {time1:.2f}s")
        print(f"   Cached call: {time2:.3f}s (faster ✅)")

    def test_news_deduplication(self):
        """
        No duplicate articles in results
        """
        from tools.news import get_news
        result = get_news("Infosys TCS Wipro IT stocks")
        
        titles = [a["title"][:50].lower() for a in result]
        unique_titles = set(titles)
        
        assert len(titles) == len(unique_titles), (
            f"Duplicate articles found!\n"
            f"Total: {len(titles)}, Unique: {len(unique_titles)}"
        )
        
        print(f"✅ No duplicates in {len(result)} articles")

    def test_news_for_different_queries(self):
        """
        Test news works for all query types
        """
        from tools.news import get_news
        
        test_queries = {
            "stock symbol"   : "TCS",
            "index query"    : "Nifty 50 market",
            "results query"  : "quarterly results",
            "IPO query"      : "upcoming IPO",
            "economy query"  : "RBI repo rate",
        }
        
        for query_type, query in test_queries.items():
            result = get_news(query)
            assert isinstance(result, list), f"get_news failed for {query_type}"
            assert len(result) > 0, f"No news for {query_type}: '{query}'"
            source = result[0].get("source", "?")
            print(f"✅ {query_type}: {len(result)} articles from {source}")


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
