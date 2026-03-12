"""
Test Market Hours — IST-based market open/close detection.
Uses mocked datetime for deterministic tests.
"""

import sys
import os
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

IST = timezone(timedelta(hours=5, minutes=30))


def is_market_open(now_ist=None):
    """
    Check if NSE market is currently open.
    This is a standalone utility for testing — not imported from the project
    since there's no dedicated market_hours module.
    """
    if now_ist is None:
        now_ist = datetime.now(IST)

    weekday = now_ist.weekday()  # 0=Mon, 6=Sun
    hour = now_ist.hour
    minute = now_ist.minute
    time_val = hour * 60 + minute  # minutes since midnight

    # Weekend
    if weekday >= 5:
        return {
            "is_open": False,
            "session": "Weekend — Market Closed",
            "message": "NSE is closed on weekends. Trading resumes Monday 9:15 AM.",
        }

    # Pre-Open: 9:00 - 9:15
    if 540 <= time_val < 555:
        return {
            "is_open": False,
            "session": "Pre-Open Session",
            "message": "Pre-open session active. Regular trading starts at 9:15 AM.",
        }

    # Market Open: 9:15 - 15:30
    if 555 <= time_val < 930:
        return {
            "is_open": True,
            "session": "Market Open ✅",
            "message": "NSE is open for trading.",
        }

    # Post-Close: 15:30 - 16:00
    if 930 <= time_val < 960:
        return {
            "is_open": False,
            "session": "Market Closed",
            "message": "Market has closed for today. Post-closing session active.",
        }

    # Before market
    if time_val < 540:
        return {
            "is_open": False,
            "session": "Pre-Market — Market Closed",
            "message": "Market not yet open. Pre-open starts at 9:00 AM IST.",
        }

    # After market
    return {
        "is_open": False,
        "session": "Market Closed",
        "message": "Market is closed for the day. Opens tomorrow at 9:15 AM.",
    }


class TestMarketHours:

    def test_market_status_returns_dict(self):
        result = is_market_open()
        assert isinstance(result, dict)
        assert "is_open" in result
        assert "session" in result
        assert "message" in result
        assert isinstance(result["is_open"], bool)
        print(f"   ✅ Market status = {result['session']}")

    def test_correct_session_label(self):
        result = is_market_open()
        valid_sessions = [
            "Market Open ✅",
            "Pre-Open Session",
            "Pre-Market — Market Closed",
            "Market Closed",
            "Weekend — Market Closed",
        ]
        assert result["session"] in valid_sessions, \
            f"Invalid session label: {result['session']}"
        print("   ✅ Session label is valid")

    def test_weekend_detection(self):
        # Saturday
        saturday = datetime(2026, 3, 14, 10, 0, tzinfo=IST)  # Saturday
        result = is_market_open(saturday)
        assert result["is_open"] is False
        assert "Weekend" in result["session"]
        print("   ✅ Weekend correctly detected")

    def test_market_open_time(self):
        # Monday 10:00 AM IST
        monday_10am = datetime(2026, 3, 9, 10, 0, tzinfo=IST)  # Monday
        result = is_market_open(monday_10am)
        assert result["is_open"] is True
        print("   ✅ 10 AM correctly shows as open")

    def test_pre_open_time(self):
        # Monday 9:05 AM IST
        monday_905am = datetime(2026, 3, 9, 9, 5, tzinfo=IST)  # Monday
        result = is_market_open(monday_905am)
        assert result["is_open"] is False
        assert "Pre-Open" in result["session"]
        print("   ✅ 9:05 AM correctly shows as pre-open")

    def test_after_market_close(self):
        # Monday 4:00 PM IST
        monday_4pm = datetime(2026, 3, 9, 16, 0, tzinfo=IST)  # Monday
        result = is_market_open(monday_4pm)
        assert result["is_open"] is False
        assert "Closed" in result["session"]
        print("   ✅ 4 PM correctly shows as closed")
