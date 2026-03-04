"""
Configuration module for Indian Stock Market AI Assistant.
Loads environment variables and defines constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── Grok LLM Configuration ──────────────────────────────────────
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROK_BASE_URL = "https://api.groq.com/openai/v1"
GROK_MODEL = "llama-3.3-70b-versatile"

# ── Validation ───────────────────────────────────────────────────
if not GROK_API_KEY or GROK_API_KEY == "your_grok_key_here":
    print("⚠️  WARNING: GROK_API_KEY not set in .env file!")
    print("   Get your free key from https://console.groq.com")
    print("   Then add it to .env → GROK_API_KEY=gsk_...")

# ── Angel One SmartAPI Configuration ─────────────────────────────
ANGEL_TRADING_API_KEY = os.getenv("ANGEL_TRADING_API_KEY", "")
ANGEL_PUBLISHER_API_KEY = os.getenv("ANGEL_PUBLISHER_API_KEY", "")
ANGEL_HISTORICAL_API_KEY = os.getenv("ANGEL_HISTORICAL_API_KEY", "")
ANGEL_FEEDS_API_KEY = os.getenv("ANGEL_FEEDS_API_KEY", "")
ANGEL_CLIENT_ID = os.getenv("ANGEL_CLIENT_ID", "")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD", "")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET", "")
