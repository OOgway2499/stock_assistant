"""
SEBI-Compliant Topic Guard — Core filtering engine.
Ensures the assistant ONLY responds to Indian capital markets queries.
Designed per SEBI guidelines for AI-powered financial information tools.
"""


# ── ALLOWED TOPICS ───────────────────────────────────────────────
ALLOWED_TOPICS = [
    # Indian Stock Exchanges
    "nse", "bse", "national stock exchange",
    "bombay stock exchange", "mcx", "ncdex",
    "equity", "stock", "share", "listing",
    "demat", "trading account", "broker", "broking",

    # Indian Market Indices
    "nifty", "nifty 50", "sensex", "bank nifty",
    "nifty it", "nifty pharma", "nifty auto",
    "nifty fmcg", "nifty metal", "nifty realty",
    "nifty midcap", "nifty smallcap", "nifty next50",
    "india vix", "vix", "index", "indices",

    # Stock Actions
    "buy", "sell", "trade", "invest", "investment",
    "price", "quote", "rate", "value", "valuation",
    "market cap", "capitalisation", "capitalization",
    "portfolio", "holdings", "position", "exposure",

    # Technical Analysis
    "rsi", "macd", "moving average", "sma", "ema",
    "bollinger", "atr", "adx", "stochastic",
    "fibonacci", "pivot", "support", "resistance",
    "trend", "trendline", "breakout", "breakdown",
    "bullish", "bearish", "sideways", "consolidation",
    "volume", "delivery", "overbought", "oversold",
    "divergence", "crossover", "golden cross",
    "death cross", "candlestick", "pattern",
    "technical analysis", "chart", "indicator",
    "momentum", "oscillator", "signal",

    # Fundamental Analysis
    "pe ratio", "pb ratio", "ps ratio", "peg ratio",
    "eps", "earnings per share", "revenue", "profit",
    "net profit", "gross profit", "ebitda", "ebit",
    "operating profit", "pat", "pbt", "roce", "roe",
    "debt", "debt to equity", "current ratio",
    "quick ratio", "working capital", "cash flow",
    "balance sheet", "income statement", "p&l",
    "profit and loss", "annual report", "quarterly",
    "results", "earnings", "guidance", "forecast",
    "fundamental", "intrinsic value", "book value",
    "face value", "nav", "net asset value",
    "promoter holding", "fii", "dii", "institutional",
    "pledging", "shareholding pattern",

    # Corporate Actions
    "dividend", "bonus", "split", "rights issue",
    "buyback", "open offer", "merger", "acquisition",
    "demerger", "spin off", "ipo", "fpo", "sme ipo",
    "offer for sale", "ofs", "grey market", "gmp",
    "allotment", "listing gain", "subscription",

    # Derivatives & F&O
    "futures", "options", "f&o", "derivatives",
    "call option", "put option", "strike price",
    "expiry", "lot size", "open interest", "oi",
    "premium", "intrinsic", "time value", "theta",
    "delta", "gamma", "vega", "greeks", "hedging",
    "collar", "straddle", "strangle", "spread",
    "covered call", "cash and carry", "arbitrage",

    # Popular Indian Stocks
    "reliance", "ril", "tcs", "infosys", "infy",
    "hdfc", "icici", "sbi", "kotak", "axis bank",
    "wipro", "hcl", "tech mahindra", "ltimindtree",
    "bajaj finance", "bajaj finserv", "bajajfinsv",
    "adani", "adanient", "adaniports", "adanigreen",
    "tatamotors", "tata steel", "tatasteel", "tata",
    "maruti", "hero motocorp", "bajaj auto", "tvs",
    "sun pharma", "cipla", "drreddy", "divis",
    "asian paints", "berger", "pidilite", "nestle",
    "hindustan unilever", "hul", "dabur", "marico",
    "titan", "tanishq", "kalyan jewellers",
    "zomato", "swiggy", "paytm", "nykaa", "policybazaar",
    "irctc", "rvnl", "irfc", "hal", "bel", "bhel",
    "ongc", "coal india", "ntpc", "power grid",
    "indusind", "yes bank", "federal bank", "bandhan",
    "dmart", "avenue supermarts",
    "l&t", "larsen", "siemens", "abb india",
    "ultratech", "ambuja", "acc", "shree cement",
    "bhartiartl", "airtel", "vodafone", "jio",

    # Sectors
    "banking", "financial services", "nbfc",
    "information technology", "it sector",
    "pharmaceutical", "pharma", "healthcare",
    "fast moving consumer goods", "fmcg",
    "automobile", "auto sector", "ev sector", "electric vehicle",
    "real estate", "realty", "reit",
    "infrastructure", "capital goods", "defence",
    "energy", "power", "renewable", "solar", "wind",
    "oil and gas", "petroleum", "refinery",
    "telecom", "communication", "media",
    "chemical", "specialty chemical", "agrochemical",
    "metal", "steel", "aluminium", "copper",
    "textiles", "garments", "logistics",
    "aviation", "hotel", "hospitality",
    "retail", "consumption", "consumer",

    # Mutual Funds & ETFs
    "mutual fund", "sip", "lumpsum", "nav",
    "equity fund", "debt fund", "hybrid fund",
    "large cap fund", "mid cap fund", "small cap fund",
    "index fund", "etf", "gold etf", "sectoral fund",
    "amc", "asset management", "fund manager",
    "expense ratio", "exit load", "folio",
    "amfi", "sebi registered", "distributor",

    # Economy & Macro
    "rbi", "reserve bank", "repo rate", "reverse repo",
    "crr", "slr", "monetary policy", "mpc",
    "inflation", "cpi", "wpi", "iip", "gdp",
    "fiscal deficit", "current account", "trade deficit",
    "rupee", "dollar", "forex", "currency",
    "us fed", "federal reserve", "interest rate",
    "crude oil", "brent", "wti", "gold", "silver",
    "commodity", "budget", "fiscal policy",
    "economic survey", "union budget",
    "foreign reserve", "fdi", "fpi",

    # Regulators & Compliance
    "sebi", "securities", "exchange board",
    "irdai", "pfrda", "pension",
    "depositories", "nsdl", "cdsl",
    "circuit breaker", "upper circuit", "lower circuit",
    "t plus 1", "settlement", "clearing",
    "surveillance", "insider trading", "bulk deal",
    "block deal", "sqr", "sast",

    # General Finance Terms
    "return", "cagr", "xirr", "alpha", "beta",
    "sharpe ratio", "standard deviation", "volatility",
    "correlation", "diversification", "asset allocation",
    "rebalancing", "tax", "ltcg", "stcg", "itr",
    "grandfathering", "indexation", "surcharge",
    "wealth", "financial planning", "retirement",
    "goal based investing", "risk appetite",
    "stop loss", "target price", "analyst",
    "research report", "brokerage", "margin",
    "pledge", "loan against shares", "mtf",
]


# ── BLOCKED TOPICS ───────────────────────────────────────────────
BLOCKED_TOPICS = [
    # Health & Medicine
    "dengue", "malaria", "covid", "corona", "virus",
    "disease", "illness", "symptom", "medicine",
    "doctor", "hospital", "surgery", "treatment",
    "vaccine", "tablet", "capsule", "injection",
    "fever", "headache", "diabetes", "cancer",
    "blood pressure", "cholesterol", "obesity",
    "ayurveda", "homeopathy", "diet plan",
    "nutrition", "vitamin", "protein", "calorie",

    # Sports & Entertainment
    "cricket", "football", "tennis", "badminton",
    "kabaddi", "hockey", "basketball", "volleyball",
    "ipl", "world cup", "champions league",
    "match", "score", "wicket", "goal",
    "player", "team", "tournament", "stadium",
    "movie", "film", "actor", "actress", "director",
    "bollywood", "hollywood", "tollywood",
    "web series", "netflix", "amazon prime",
    "ott platform", "song", "music", "album",
    "celebrity", "gossip", "entertainment",

    # Food & Cooking
    "recipe", "cooking", "biryani", "curry", "dal",
    "roti", "rice", "pizza", "burger", "pasta",
    "restaurant", "cafe", "food delivery",
    "ingredients", "spices", "masala",

    # Travel & Tourism
    "travel", "tourism", "holiday", "vacation",
    "hotel booking", "flight ticket", "visa",
    "passport", "destination", "itinerary",
    "tourist", "sightseeing", "beach", "mountain",

    # Relationships & Personal
    "relationship", "love", "marriage", "divorce",
    "dating", "breakup", "boyfriend", "girlfriend",
    "family", "parenting", "children", "baby",
    "personal advice", "life advice",

    # General Technology
    "coding", "programming", "python tutorial",
    "javascript tutorial", "html", "css",
    "machine learning tutorial", "data science",
    "app development", "web development",
    "gaming", "video game", "playstation", "xbox",

    # Academic Subjects
    "history", "geography", "science experiment",
    "biology lesson", "physics formula",
    "chemistry equation", "mathematics problem",
    "trigonometry", "calculus", "algebra",
    "literature", "grammar", "essay writing",

    # Religious & Social
    "religion", "god", "temple", "church", "mosque",
    "prayer", "festival", "astrology", "horoscope",
    "vastu", "numerology", "tarot",

    # Politics (Non-Market)
    "election", "political party", "politician",
    "chief minister", "prime minister",
    "parliament", "assembly", "vote",
    "manifesto", "rally", "protest",

    # General Knowledge / Geography
    "capital of", "continent", "country",
    "photosynthesis", "ecosystem", "evolution",
    "planet", "solar system", "universe",
    "dinosaur", "archaeology", "fossil",

    # Famous Personalities (Non-Finance)
    "virat kohli", "sachin tendulkar", "dhoni",
    "shahrukh khan", "amitabh", "modi speech",
]


# ── GUARD FUNCTIONS ──────────────────────────────────────────────

def is_market_related(query: str) -> dict:
    """
    Check if a query is related to Indian capital markets.

    Logic:
    1. Check ALLOWED_TOPICS first → allow (finance keywords take priority)
    2. Check BLOCKED_TOPICS → refuse
    3. Short queries (1-2 words) → allow (could be stock symbols)
    4. Ambiguous long queries → allow (let LLM system prompt handle)
    """
    lower = query.lower().strip()

    # Check allowed topics FIRST — finance keywords always take priority
    for keyword in ALLOWED_TOPICS:
        if keyword in lower:
            return {
                "allowed": True,
                "matched": keyword,
                "reason": "Market related query",
            }

    # Check blocked topics (only if no allowed keyword matched)
    for keyword in BLOCKED_TOPICS:
        if keyword in lower:
            return {
                "allowed": False,
                "matched": keyword,
                "reason": "Off-topic query",
            }

    # Short queries (1-2 words) — could be stock symbols like TCS, INFY
    if len(lower.split()) <= 2:
        return {
            "allowed": True,
            "reason": "Short query — possible stock symbol",
        }

    # Default: allow ambiguous — let LLM system prompt handle
    return {
        "allowed": True,
        "reason": "Ambiguous — LLM will handle",
    }


def get_refusal_message() -> str:
    """Return the standard SEBI-compliant refusal message."""
    return """📊 I am exclusively designed for Indian Stock Market analysis and cannot help with that topic.

As a SEBI-compliant financial assistant, my scope is strictly limited to capital markets.

✅ Here is what I can help you with:

📈 **MARKET DATA**
• Live NSE/BSE stock prices
• Nifty 50, Sensex, Bank Nifty levels
• Top gainers and losers today
• Sector performance

🔢 **TECHNICAL ANALYSIS**
• RSI, MACD, Moving Averages
• Support and resistance levels
• Trend analysis and signals
• Bollinger Bands, ATR

💰 **FUNDAMENTAL ANALYSIS**
• PE ratio, EPS, Revenue growth
• Debt levels, ROE, ROCE
• Quarterly results analysis
• Promoter holding changes

📰 **MARKET INTELLIGENCE**
• Stock-specific news
• IPO analysis and GMP
• Corporate actions — dividend, bonus, split
• FII/DII activity

🏦 **FINANCIAL EDUCATION**
• How to read financial statements
• Understanding derivatives (F&O)
• Mutual funds and ETF analysis
• Risk management concepts

Please ask me anything related to Indian stock markets! 🇮🇳

⚠️ Disclaimer: This assistant provides market information for educational purposes only. It does not constitute financial advice. Please consult a SEBI-registered investment advisor before making any investment decisions."""


def get_scope_reminder() -> str:
    """Short version for chat UI placeholder."""
    return "Ask me about NSE/BSE stocks, Nifty, technical analysis, fundamentals, IPOs, mutual funds or market news..."
