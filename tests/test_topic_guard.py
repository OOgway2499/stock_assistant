"""
Test Topic Guard — SEBI compliance filtering.
25 tests: 10 must be blocked, 15 must be allowed.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.topic_guard import is_market_related, get_refusal_message, get_scope_reminder


class TestTopicGuardBlocked:
    """These queries MUST be blocked (allowed=False)."""

    BLOCKED_QUERIES = [
        "What is dengue fever?",
        "How to make chicken biryani?",
        "Who won IPL 2024?",
        "Suggest me a good movie",
        "What is photosynthesis?",
        "Help me with Python coding tutorial",
        "What is the capital of France?",
        "Give me a pasta recipe",
        "What is malaria treatment?",
        "Who is Virat Kohli?",
    ]

    @pytest.mark.parametrize("query", BLOCKED_QUERIES)
    def test_blocked_query(self, query):
        result = is_market_related(query)
        assert result["allowed"] is False, \
            f"Should be BLOCKED but was allowed: '{query}' (matched: {result.get('matched')})"
        print(f"   ✅ BLOCKED: \"{query}\"")


class TestTopicGuardAllowed:
    """These queries MUST be allowed (allowed=True)."""

    ALLOWED_QUERIES = [
        "Price of Reliance today",
        "What is RSI indicator?",
        "How is Nifty 50 performing?",
        "Explain PE ratio",
        "TCS",
        "INFY",
        "Top gainers on NSE today",
        "Is HDFC Bank bullish?",
        "Explain what is an IPO",
        "What is RBI repo rate effect on stocks?",
        "How to read candlestick charts?",
        "Difference between futures and options?",
        "What is SIP investment?",
        "Show me sector performance",
        "Nifty Bank today",
    ]

    @pytest.mark.parametrize("query", ALLOWED_QUERIES)
    def test_allowed_query(self, query):
        result = is_market_related(query)
        assert result["allowed"] is True, \
            f"Should be ALLOWED but was blocked: '{query}' (matched: {result.get('matched')})"
        print(f"   ✅ ALLOWED: \"{query}\"")


class TestTopicGuardFunctions:
    """Test helper functions."""

    def test_refusal_message_not_empty(self):
        msg = get_refusal_message()
        assert len(msg) > 100
        assert "SEBI" in msg or "capital markets" in msg.lower()
        assert "⚠️" in msg
        print("   ✅ Refusal message is complete and contains disclaimer")

    def test_scope_reminder_not_empty(self):
        msg = get_scope_reminder()
        assert len(msg) > 20
        assert "NSE" in msg or "stock" in msg.lower()
        print("   ✅ Scope reminder is set")

    def test_short_query_allowed(self):
        result = is_market_related("ZOMATO")
        assert result["allowed"] is True
        assert "short" in result.get("reason", "").lower() or "Market" in result.get("reason", "")
        print("   ✅ Short query 'ZOMATO' allowed (possible stock symbol)")

    def test_ambiguous_long_query_allowed(self):
        result = is_market_related("Can you tell me something interesting about the world economy today")
        assert result["allowed"] is True
        print("   ✅ Ambiguous long query allowed (LLM will handle)")
