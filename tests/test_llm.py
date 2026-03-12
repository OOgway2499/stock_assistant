"""
Test Groq LLM — response quality, tool calling, disclaimer, timing.
Each test has 45s timeout since LLM calls are slow.
"""

import sys
import os
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGroqLLM:
    """Test Groq LLM responses via ask_assistant."""

    @pytest.mark.timeout(45)
    def test_simple_stock_price_query(self):
        from llm.grok_agent import ask_assistant
        response = ask_assistant("What is the current price of TCS?")
        assert response is not None
        assert len(response) > 50
        assert "TCS" in response.upper() or "Tata" in response
        print(f"   ✅ LLM answered TCS price query")
        print(f"   📝 {response[:200]}...")

    @pytest.mark.timeout(45)
    def test_technical_analysis_query(self):
        from llm.grok_agent import ask_assistant
        response = ask_assistant("Show me RSI and MACD for Reliance")
        assert response is not None
        assert len(response) > 100
        assert "RSI" in response.upper() or "rsi" in response.lower()
        print("   ✅ LLM answered technical query")

    @pytest.mark.timeout(45)
    def test_market_overview_query(self):
        from llm.grok_agent import ask_assistant
        response = ask_assistant("How is the market today? Show Nifty and top gainers")
        assert response is not None
        assert len(response) > 100
        assert "nifty" in response.lower() or "market" in response.lower()
        print("   ✅ LLM answered market overview query")

    @pytest.mark.timeout(45)
    def test_fundamental_query(self):
        from llm.grok_agent import ask_assistant
        response = ask_assistant("What is the PE ratio of HDFC Bank?")
        assert response is not None
        assert "PE" in response.upper() or "ratio" in response.lower() or "HDFC" in response.upper()
        print("   ✅ LLM answered fundamental query")

    @pytest.mark.timeout(45)
    def test_news_query(self):
        from llm.grok_agent import ask_assistant
        response = ask_assistant("What is the latest news on Infosys?")
        assert response is not None
        assert len(response) > 100
        assert "Infosys" in response or "INFY" in response or "infosys" in response.lower()
        print("   ✅ LLM answered news query")

    @pytest.mark.timeout(45)
    def test_disclaimer_present(self):
        """
        Verify LLM response contains SEBI compliance disclaimer.
        Accepts many variations since LLM may word it differently.
        """
        from llm.grok_agent import ask_assistant
        response = ask_assistant("Analyse TCS stock for me")
        assert response is not None
        assert len(response) > 50

        response_lower = response.lower()

        disclaimer_variations = [
            "not financial advice",
            "not a financial advice",
            "financial advice",
            "not investment advice",
            "educational purpose",
            "educational purposes",
            "sebi",
            "sebi-registered",
            "registered advisor",
            "investment advisor",
            "consult a",
            "before investing",
            "before making",
            "⚠️",
            "disclaimer",
            "not a recommendation",
            "do your own research",
            "past performance",
        ]

        has_disclaimer = any(v in response_lower for v in disclaimer_variations)
        has_warning = "⚠️" in response

        assert has_disclaimer or has_warning, (
            f"\n❌ No disclaimer found!\n"
            f"Response preview: {response[:400]}\n"
            f"Fix: Update SYSTEM_PROMPT in grok_agent.py"
        )
        print("   ✅ SEBI disclaimer present in response")

    @pytest.mark.timeout(45)
    def test_response_time(self):
        from llm.grok_agent import ask_assistant
        start = time.time()
        response = ask_assistant("Price of Reliance?")
        elapsed = round(time.time() - start, 2)
        assert response is not None
        assert elapsed < 30, f"Response took {elapsed}s (max 30s)"
        print(f"   ✅ Response time = {elapsed}s")

    @pytest.mark.timeout(60)
    def test_conversation_history(self):
        from llm.grok_agent import ask_assistant
        resp1 = ask_assistant("What is TCS price?")
        assert resp1 is not None
        history = [
            {"role": "user", "content": "What is TCS price?"},
            {"role": "assistant", "content": resp1},
        ]
        resp2 = ask_assistant("What about Infosys?", history)
        assert resp2 is not None
        assert "infosys" in resp2.lower() or "INFY" in resp2 or "Infosys" in resp2
        print("   ✅ Conversation history works")
