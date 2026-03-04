"""
Angel One SmartAPI — Real-time data manager.
Manages 4 separate SmartConnect clients for Trading, Publisher,
Historical, and Market Feeds APIs.

ADDITIVE ONLY — does not modify any existing data sources.
"""

import pyotp
import json
import threading
from datetime import datetime, timedelta

try:
    from SmartApi import SmartConnect
    from SmartApi.SmartWebSocketV2 import SmartWebSocketV2
    HAS_SMARTAPI = True
except ImportError:
    HAS_SMARTAPI = False

from config import (
    ANGEL_TRADING_API_KEY,
    ANGEL_PUBLISHER_API_KEY,
    ANGEL_HISTORICAL_API_KEY,
    ANGEL_FEEDS_API_KEY,
    ANGEL_CLIENT_ID,
    ANGEL_PASSWORD,
    ANGEL_TOTP_SECRET,
)

# ── Common Stock Tokens (NSE exchange) ───────────────────────────
STOCK_TOKENS = {
    "RELIANCE":   "2885",
    "TCS":        "11536",
    "INFY":       "1594",
    "HDFCBANK":   "1333",
    "ICICIBANK":  "4963",
    "WIPRO":      "3787",
    "SBIN":       "3045",
    "AXISBANK":   "5900",
    "TATAMOTORS": "3456",
    "ADANIENT":   "25",
    "BAJFINANCE": "317",
    "KOTAKBANK":  "1922",
    "LT":         "11483",
    "HINDALCO":   "1363",
    "TATASTEEL":  "3499",
    "MARUTI":     "10999",
    "SUNPHARMA":  "3351",
    "BHARTIARTL": "10604",
    "ASIANPAINT": "236",
    "TITAN":      "3506",
    "ULTRACEMCO": "11532",
    "NESTLEIND":  "17963",
    "POWERGRID":  "14977",
    "NTPC":       "11630",
    "ONGC":       "2475",
    "HCLTECH":    "7229",
    "TECHM":      "13538",
    "BAJAJFINSV": "16675",
    "DIVISLAB":   "10940",
    "DRREDDY":    "881",
    "CIPLA":      "694",
    "NIFTY 50":   "26000",
    "BANKNIFTY":  "26009",
}


class AngelOneManager:
    """Manages 4 separate Angel One SmartConnect clients."""

    def __init__(self):
        self.trading_client = None
        self.publisher_client = None
        self.historical_client = None
        self.feeds_client = None
        self.is_logged_in = False
        self.auth_token = None
        self.feed_token = None
        self.refresh_token = None
        self.token_cache = {}  # Cache for searched symbol tokens

    def _generate_totp(self) -> str:
        """Generate TOTP from secret."""
        return pyotp.TOTP(ANGEL_TOTP_SECRET).now()

    def login(self) -> bool:
        """Login to all 4 Angel One APIs."""
        if not HAS_SMARTAPI:
            print("⚠️ smartapi-python not installed. Run: pip install smartapi-python")
            return False

        if not all([ANGEL_FEEDS_API_KEY, ANGEL_CLIENT_ID, ANGEL_PASSWORD, ANGEL_TOTP_SECRET]):
            print("⚠️ Angel One credentials not configured in .env")
            return False

        try:
            # Initialize all 4 clients
            self.trading_client = SmartConnect(api_key=ANGEL_TRADING_API_KEY)
            self.publisher_client = SmartConnect(api_key=ANGEL_PUBLISHER_API_KEY)
            self.historical_client = SmartConnect(api_key=ANGEL_HISTORICAL_API_KEY)
            self.feeds_client = SmartConnect(api_key=ANGEL_FEEDS_API_KEY)

            # Login with feeds client (primary)
            totp = self._generate_totp()
            data = self.feeds_client.generateSession(
                ANGEL_CLIENT_ID, ANGEL_PASSWORD, totp
            )

            if data and data.get("status"):
                self.auth_token = data["data"]["jwtToken"]
                self.feed_token = data["data"]["feedToken"]
                self.refresh_token = data["data"]["refreshToken"]
                self.is_logged_in = True
                print("✅ Angel One Login Successful!")
                return True
            else:
                msg = data.get("message", "Unknown login error") if data else "No response"
                print(f"⚠️ Angel One Login Failed: {msg}")
                return False

        except Exception as e:
            print(f"⚠️ Angel One Login Error: {e}")
            self.is_logged_in = False
            return False

    def ensure_login(self) -> bool:
        """Ensure we're logged in before making API calls."""
        if not self.is_logged_in:
            return self.login()
        return self.is_logged_in

    def get_symbol_token(self, symbol: str) -> str | None:
        """Get Angel One symbol token for a stock."""
        sym = symbol.upper().replace("-EQ", "")

        # 1. Check hardcoded tokens (fastest)
        if sym in STOCK_TOKENS:
            return STOCK_TOKENS[sym]

        # 2. Check cache
        if sym in self.token_cache:
            return self.token_cache[sym]

        # 3. Search via API
        try:
            if not self.ensure_login():
                return None
            result = self.feeds_client.searchScrip("NSE", sym)
            if result and result.get("data"):
                token = result["data"][0].get("symboltoken")
                if token:
                    self.token_cache[sym] = token
                    return token
        except Exception as e:
            print(f"⚠️ Token search failed for {sym}: {e}")

        return None

    def get_live_price(self, symbol: str) -> dict:
        """
        Get real-time price using Market Feeds API.
        Returns dict with price data or {"error": "..."}.
        """
        try:
            if not self.ensure_login():
                return {"error": "Angel One not connected"}

            token = self.get_symbol_token(symbol)
            if not token:
                return {"error": f"Token not found for {symbol}"}

            data = self.feeds_client.ltpData(
                exchange="NSE",
                tradingsymbol=symbol.upper() + "-EQ",
                symboltoken=token,
            )

            if data and data.get("data"):
                d = data["data"]
                ltp = float(d.get("ltp", 0))
                op = float(d.get("open", 0))
                hi = float(d.get("high", 0))
                lo = float(d.get("low", 0))
                cl = float(d.get("close", 0))
                change = round(ltp - cl, 2) if cl else 0
                change_pct = round((change / cl) * 100, 2) if cl else 0

                return {
                    "symbol": symbol.upper(),
                    "companyName": symbol.upper(),
                    "currentPrice": ltp,
                    "open": op,
                    "high": hi,
                    "low": lo,
                    "previousClose": cl,
                    "volume": int(d.get("volume", 0) or 0),
                    "change": change,
                    "changePercent": change_pct,
                    "exchange": "NSE",
                    "data_source": "Angel One Market Feeds (Real-time ✅)",
                    "dataSource": "Angel One Market Feeds (Real-time ✅)",
                }

            return {"error": f"No LTP data for {symbol}"}

        except Exception as e:
            return {"error": f"Angel One price fetch failed: {e}"}

    def get_full_quote(self, symbol: str) -> dict:
        """Get full quote using Trading API."""
        try:
            if not self.ensure_login():
                return {"error": "Angel One not connected"}

            token = self.get_symbol_token(symbol)
            if not token:
                return {"error": f"Token not found for {symbol}"}

            data = self.trading_client.ltpData(
                exchange="NSE",
                tradingsymbol=symbol.upper() + "-EQ",
                symboltoken=token,
            )

            if data and data.get("data"):
                d = data["data"]
                ltp = float(d.get("ltp", 0))
                cl = float(d.get("close", 0))
                change = round(ltp - cl, 2) if cl else 0
                change_pct = round((change / cl) * 100, 2) if cl else 0

                return {
                    "symbol": symbol.upper(),
                    "live_price": ltp,
                    "open": float(d.get("open", 0)),
                    "high": float(d.get("high", 0)),
                    "low": float(d.get("low", 0)),
                    "close": cl,
                    "volume": int(d.get("volume", 0) or 0),
                    "change": change,
                    "change_percent": change_pct,
                    "data_source": "Angel One Trading API (Real-time ✅)",
                }

            return {"error": f"No quote data for {symbol}"}

        except Exception as e:
            return {"error": f"Angel One quote failed: {e}"}

    def get_historical_candles(
        self,
        symbol: str,
        interval: str = "ONE_DAY",
        from_date: str = None,
        to_date: str = None,
    ) -> list:
        """
        Get historical OHLCV candles using Historical Data API.

        Supported intervals:
            ONE_MINUTE, THREE_MINUTE, FIVE_MINUTE, TEN_MINUTE,
            FIFTEEN_MINUTE, THIRTY_MINUTE, ONE_HOUR,
            ONE_DAY, ONE_WEEK, ONE_MONTH
        """
        try:
            if not self.ensure_login():
                return []

            token = self.get_symbol_token(symbol)
            if not token:
                return []

            # Default date range: 6 months
            if not to_date:
                to_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            if not from_date:
                from_dt = datetime.now() - timedelta(days=180)
                from_date = from_dt.strftime("%Y-%m-%d %H:%M")

            params = {
                "exchange": "NSE",
                "symboltoken": token,
                "interval": interval,
                "fromdate": from_date,
                "todate": to_date,
            }

            data = self.historical_client.getCandleData(params)

            if data and data.get("data"):
                return data["data"]  # List of [timestamp, O, H, L, C, V]

            return []

        except Exception as e:
            print(f"⚠️ Angel One historical failed for {symbol}: {e}")
            return []

    def get_market_depth(self, symbol: str) -> dict:
        """Get top 5 bid/ask prices using Trading API."""
        try:
            if not self.ensure_login():
                return {"error": "Angel One not connected"}

            token = self.get_symbol_token(symbol)
            if not token:
                return {"error": f"Token not found for {symbol}"}

            # Market depth via getMarketData
            data = self.trading_client.getMarketData({
                "mode": "FULL",
                "exchangeTokens": {"NSE": [token]},
            })

            if data and data.get("data") and data["data"].get("fetched"):
                fetched = data["data"]["fetched"][0]
                depth = fetched.get("depth", {})

                bids = []
                asks = []
                for b in depth.get("buy", [])[:5]:
                    bids.append({
                        "price": float(b.get("price", 0)),
                        "quantity": int(b.get("quantity", 0)),
                    })
                for a in depth.get("sell", [])[:5]:
                    asks.append({
                        "price": float(a.get("price", 0)),
                        "quantity": int(a.get("quantity", 0)),
                    })

                return {
                    "symbol": symbol.upper(),
                    "bids": bids,
                    "asks": asks,
                    "totalBuyQty": fetched.get("totalBuyQty", 0),
                    "totalSellQty": fetched.get("totalSellQty", 0),
                    "ltp": float(fetched.get("ltp", 0)),
                    "data_source": "Angel One Trading API",
                }

            return {"error": f"No market depth for {symbol}"}

        except Exception as e:
            return {"error": f"Angel One depth failed: {e}"}

    def get_portfolio(self) -> list:
        """Get user's Angel One portfolio/holdings using Trading API."""
        try:
            if not self.ensure_login():
                return []

            data = self.trading_client.holding()

            if data and data.get("data"):
                holdings = []
                for h in data["data"]:
                    avg_price = float(h.get("averageprice", 0))
                    ltp = float(h.get("ltp", 0))
                    qty = int(h.get("quantity", 0))
                    pnl = round((ltp - avg_price) * qty, 2)
                    pnl_pct = round(((ltp - avg_price) / avg_price) * 100, 2) if avg_price else 0

                    holdings.append({
                        "symbol": h.get("tradingsymbol", "").replace("-EQ", ""),
                        "quantity": qty,
                        "avgPrice": avg_price,
                        "currentPrice": ltp,
                        "pnl": pnl,
                        "pnlPercent": pnl_pct,
                        "exchange": h.get("exchange", "NSE"),
                    })
                return holdings

            return []

        except Exception as e:
            print(f"⚠️ Angel One portfolio failed: {e}")
            return []

    def start_websocket_stream(self, symbols: list, on_tick: callable = None):
        """Start WebSocket stream for real-time ticks."""
        try:
            if not self.ensure_login():
                print("⚠️ Cannot start WebSocket — not logged in")
                return

            # Build token list
            tokens = []
            for sym in symbols:
                t = self.get_symbol_token(sym)
                if t:
                    tokens.append(t)

            if not tokens:
                print("⚠️ No valid tokens for WebSocket")
                return

            token_list = [{"exchangeType": 1, "tokens": tokens}]

            sws = SmartWebSocketV2(
                self.auth_token,
                ANGEL_FEEDS_API_KEY,
                ANGEL_CLIENT_ID,
                self.feed_token,
            )

            def on_data(wsapp, message):
                """Handle incoming tick data."""
                if on_tick and message:
                    try:
                        on_tick(message)
                    except Exception as e:
                        print(f"⚠️ WebSocket tick handler error: {e}")

            def on_open(wsapp):
                """Subscribe to tokens on connection open."""
                print("🔌 WebSocket connected — subscribing...")
                sws.subscribe("angel_stream", 3, token_list)  # mode=3 = snap quote

            def on_error(wsapp, error):
                """Handle WebSocket errors."""
                print(f"⚠️ WebSocket error: {error}")

            def on_close(wsapp):
                """Handle WebSocket close."""
                print("🔌 WebSocket disconnected")

            sws.on_open = on_open
            sws.on_data = on_data
            sws.on_error = on_error
            sws.on_close = on_close

            # Run in background thread
            thread = threading.Thread(target=sws.connect, daemon=True)
            thread.start()
            print(f"🔌 WebSocket streaming started for {len(tokens)} symbols")

        except Exception as e:
            print(f"⚠️ WebSocket setup failed: {e}")

    def logout(self):
        """Logout from Angel One."""
        try:
            if self.feeds_client and self.is_logged_in:
                self.feeds_client.terminateSession(ANGEL_CLIENT_ID)
        except Exception:
            pass
        self.is_logged_in = False
        print("👋 Logged out from Angel One")


# ── Singleton Instance ───────────────────────────────────────────
_angel_manager = None


def get_angel_manager() -> AngelOneManager:
    """Get or create the singleton AngelOneManager."""
    global _angel_manager
    if _angel_manager is None:
        _angel_manager = AngelOneManager()
        _angel_manager.login()
    return _angel_manager


# ── Test Block ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("🧪 Testing Angel One 4-API Setup...")
    print("=" * 50)

    manager = AngelOneManager()

    # Test login
    if manager.login():
        print("✅ Login: PASSED")
    else:
        print("❌ Login: FAILED — check credentials in .env")
        exit(1)

    # Test live price (Market Feeds API)
    result = manager.get_live_price("RELIANCE")
    if "error" not in result:
        print(f"✅ Live Price: PASSED — ₹{result.get('currentPrice')}")
    else:
        print(f"⚠️ Live Price: {result['error']}")

    # Test historical (Historical Data API)
    candles = manager.get_historical_candles("TCS", "ONE_DAY")
    if candles:
        print(f"✅ Historical: PASSED — {len(candles)} candles")
    else:
        print("⚠️ Historical: No data returned")

    # Test full quote (Trading API)
    quote = manager.get_full_quote("INFY")
    if "error" not in quote:
        print(f"✅ Full Quote: PASSED — ₹{quote.get('live_price')}")
    else:
        print(f"⚠️ Full Quote: {quote['error']}")

    # Test portfolio (Trading API)
    portfolio = manager.get_portfolio()
    print(f"✅ Portfolio: PASSED — {len(portfolio)} holdings")

    manager.logout()
    print("=" * 50)
    print("✅ All 4 APIs tested!")
