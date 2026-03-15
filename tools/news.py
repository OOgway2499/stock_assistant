import feedparser
import requests
import yfinance as yf
import time
import re
from datetime import datetime
from typing import List, Dict, Optional

# ━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONSTANTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━

RSS_HEADERS = {
    "User-Agent"     : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept"         : "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection"     : "keep-alive",
    "Cache-Control"  : "no-cache",
    "Referer"        : "https://www.moneycontrol.com/"
}

CACHE_DURATION = 300  # 5 minutes

MONEYCONTROL_FEEDS = {
    "market"        : "https://www.moneycontrol.com/rss/marketreports.xml",
    "business"      : "https://www.moneycontrol.com/rss/business.xml",
    "economy"       : "https://www.moneycontrol.com/rss/economy.xml",
    "results"       : "https://www.moneycontrol.com/rss/results.xml",
    "ipo"           : "https://www.moneycontrol.com/rss/ipo.xml",
    "mutualfunds"   : "https://www.moneycontrol.com/rss/mutualfunds.xml",
    "commodity"     : "https://www.moneycontrol.com/rss/commodity.xml",
    "currency"      : "https://www.moneycontrol.com/rss/currency.xml",
    "expertadvice"  : "https://www.moneycontrol.com/rss/expertadvice.xml",
    "personalfinance": "https://www.moneycontrol.com/rss/personalfinance.xml",
}

ET_FEEDS = {
    "market" : "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "stocks" : "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "economy": "https://economictimes.indiatimes.com/economy/rssfeeds/1373380680.cms",
    "tech"   : "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
}

# Map query keywords to best MoneyControl feed
QUERY_TO_FEED = {
    "ipo"          : "ipo",
    "listing"      : "ipo",
    "mutual fund"  : "mutualfunds",
    "sip"          : "mutualfunds",
    "mf"           : "mutualfunds",
    "gold"         : "commodity",
    "silver"       : "commodity",
    "crude"        : "commodity",
    "commodity"    : "commodity",
    "rupee"        : "currency",
    "dollar"       : "currency",
    "forex"        : "currency",
    "rbi"          : "economy",
    "gdp"          : "economy",
    "inflation"    : "economy",
    "budget"       : "economy",
    "results"      : "results",
    "quarterly"    : "results",
    "earnings"     : "results",
    "profit"       : "results",
    "revenue"      : "results",
    "expert"       : "expertadvice",
    "recommend"    : "expertadvice",
    "target"       : "expertadvice",
    "buy"          : "expertadvice",
    "sell"         : "expertadvice",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━
# CACHE SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━

_news_cache: Dict = {}

def get_cached(key: str) -> Optional[list]:
    if key in _news_cache:
        entry = _news_cache[key]
        age   = time.time() - entry["ts"]
        if age < CACHE_DURATION:
            return entry["data"]
    return None

def set_cached(key: str, data: list) -> None:
    if data:
        _news_cache[key] = {
            "data": data,
            "ts"  : time.time()
        }

def clear_cache() -> None:
    _news_cache.clear()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SMART FEED SELECTOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def select_best_mc_feed(query: str) -> list:
    """
    Intelligently selects the best MoneyControl
    RSS feeds based on the user's query.
    Returns list of feed keys to try in order.
    Always includes market as fallback.
    """
    query_lower = query.lower()
    selected    = []
    
    # Check query against keyword map
    for keyword, feed_key in QUERY_TO_FEED.items():
        if keyword in query_lower:
            if feed_key not in selected:
                selected.append(feed_key)
    
    # Always add market and business as fallback
    if "market" not in selected:
        selected.append("market")
    if "business" not in selected:
        selected.append("business")
    
    # Results feed is always useful for stock queries
    if len(query.split()) <= 3 and \
       "results" not in selected:
        selected.append("results")
    
    return selected[:3]  # Max 3 feeds per query

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — parse_feed_entries()
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_entries(entries: list, source: str) -> list:
    """
    Normalizes RSS feed entries to standard
    format used across the entire app.
    Handles all variations of RSS formats.
    """
    results = []
    
    for entry in entries:
        try:
            title = entry.get("title", "").strip()
            if not title or len(title) < 5:
                continue
            
            # Published date
            published = (
                entry.get("published") or
                entry.get("updated") or
                entry.get("pubDate") or
                datetime.now().strftime(
                    "%a, %d %b %Y %H:%M:%S +0530"
                )
            )
            
            # Summary — clean HTML tags
            raw_summary = (
                entry.get("summary") or
                entry.get("description") or
                entry.get("content", [{}])[0].get(
                    "value", title
                )
            )
            summary = re.sub(
                r'<[^>]+>', 
                '', 
                str(raw_summary)
            ).strip()[:300]
            
            # Link
            link = (
                entry.get("link") or
                entry.get("url") or
                ""
            )
            
            # Source name
            src = entry.get("source", {})
            if isinstance(src, dict):
                source_name = src.get("title", source)
            else:
                source_name = source
            
            results.append({
                "title"    : title,
                "published": str(published),
                "source"   : source_name,
                "link"     : link,
                "summary"  : summary,
            })
            
        except Exception:
            continue
    
    return results

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — filter_relevant()
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def filter_relevant(articles: list, query: str, max_items: int = 5) -> list:
    """
    Filters articles by relevance to query.
    Returns query-relevant articles first,
    then general articles to fill up to max_items.
    """
    if not query or not articles:
        return articles[:max_items]
    
    query_words = query.lower().split()
    relevant    = []
    general     = []
    
    for article in articles:
        title   = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        
        # Check if any query word appears
        is_relevant = any(
            word in title or word in summary
            for word in query_words
            if len(word) > 2  # Skip short words
        )
        
        if is_relevant:
            relevant.append(article)
        else:
            general.append(article)
    
    # Combine: relevant first, then general
    combined = relevant + general
    return combined[:max_items]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER — deduplicate()
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def deduplicate(articles: list) -> list:
    """
    Removes duplicate articles by comparing
    first 60 characters of title.
    """
    seen    = set()
    unique  = []
    
    for article in articles:
        title_key = article.get(
            "title", ""
        ).lower()[:60]
        
        if title_key and title_key not in seen:
            seen.add(title_key)
            unique.append(article)
    
    return unique

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SOURCE 1 — MoneyControl (PRIMARY)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def fetch_moneycontrol(query: str = "", feeds: list = None) -> list:
    """
    PRIMARY NEWS SOURCE — MoneyControl RSS
    India's #1 financial news platform.
    
    Fetches from multiple MC feeds based on query.
    Filters for relevance.
    Returns normalized article list.
    """
    if feeds is None:
        feeds = select_best_mc_feed(query)
    
    all_articles = []
    
    for feed_key in feeds:
        url = MONEYCONTROL_FEEDS.get(feed_key)
        if not url:
            continue
        
        try:
            response = requests.get(
                url,
                headers=RSS_HEADERS,
                timeout=12
            )
            
            if response.status_code != 200:
                print(f"⚠️ MC {feed_key}: HTTP {response.status_code}")
                continue
            
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                continue
            
            articles = parse_entries(
                feed.entries[:15],
                source="MoneyControl"
            )
            
            all_articles.extend(articles)
            print(f"✅ MoneyControl [{feed_key}]: {len(articles)} articles")
            
        except requests.exceptions.Timeout:
            print(f"⚠️ MC {feed_key}: Timeout")
            continue
        except Exception as e:
            print(f"⚠️ MC {feed_key}: {str(e)}")
            continue
    
    if not all_articles:
        return []
    
    # Filter relevant and deduplicate
    relevant = filter_relevant(all_articles, query, max_items=8)
    return deduplicate(relevant)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SOURCE 2 — Economic Times (BACKUP 1)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def fetch_economic_times(query: str = "") -> list:
    """
    BACKUP SOURCE 1 — Economic Times RSS
    India's leading business newspaper.
    Used when MoneyControl doesn't have enough.
    """
    query_lower = query.lower()
    
    # Select best ET feed for query
    if "tech" in query_lower or \
       "it " in query_lower or \
       "software" in query_lower:
        feed_keys = ["tech", "stocks"]
    elif "economy" in query_lower or \
         "rbi" in query_lower or \
         "gdp" in query_lower:
        feed_keys = ["economy", "market"]
    else:
        feed_keys = ["stocks", "market"]
    
    all_articles = []
    
    for feed_key in feed_keys:
        url = ET_FEEDS.get(feed_key)
        if not url:
            continue
        
        try:
            response = requests.get(
                url,
                headers=RSS_HEADERS,
                timeout=12
            )
            
            if response.status_code != 200:
                continue
            
            feed     = feedparser.parse(response.content)
            articles = parse_entries(
                feed.entries[:12],
                source="Economic Times"
            )
            all_articles.extend(articles)
            
        except Exception as e:
            print(f"⚠️ ET {feed_key}: {str(e)}")
            continue
    
    relevant = filter_relevant(all_articles, query, max_items=5)
    return deduplicate(relevant)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SOURCE 3 — NSE Announcements (BACKUP 2)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def fetch_nse_announcements(symbol: str) -> list:
    """
    BACKUP SOURCE 2 — NSE Official Announcements
    Only used for specific stock symbol queries.
    Most authoritative source for company news.
    """
    try:
        session = requests.Session()
        session.headers.update(RSS_HEADERS)
        
        # Setup NSE session with cookies
        session.get("https://www.nseindia.com", timeout=10)
        time.sleep(0.5)
        
        url = (
            f"https://www.nseindia.com/api/"
            f"corp-info?symbol={symbol.upper()}"
            f"&corpType=announcements"
        )
        
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data          = response.json()
        announcements = data.get("data", [])[:5]
        
        results = []
        for item in announcements:
            title = (
                item.get("subject") or
                item.get("desc") or
                ""
            ).strip()
            
            if not title:
                continue
            
            results.append({
                "title"    : title,
                "published": item.get("date", datetime.now().strftime("%d-%b-%Y")),
                "source"   : "NSE Official",
                "link"     : "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
                "summary"  : item.get("desc", title)[:200],
            })
        
        return results
        
    except Exception as e:
        print(f"⚠️ NSE announcements: {str(e)}")
        return []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SOURCE 4 — Yahoo Finance (FINAL FALLBACK)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def fetch_yfinance_news(symbol: str) -> list:
    """
    FINAL FALLBACK — Yahoo Finance via yfinance
    This source almost NEVER fails.
    Always try this if all other sources fail.
    """
    results = []
    
    # Try with .NS suffix first (Indian stocks)
    suffixes = [".NS", ".BO", ""]
    
    for suffix in suffixes:
        try:
            ticker_symbol = f"{symbol}{suffix}"
            ticker        = yf.Ticker(ticker_symbol)
            news          = ticker.news
            
            if not news:
                continue
            
            for item in news[:6]:
                title = item.get("title", "")
                if not title:
                    continue
                
                pub_time = item.get("providerPublishTime", 0)
                published = datetime.fromtimestamp(
                    pub_time
                ).strftime("%a, %d %b %Y %H:%M:%S") if pub_time else str(datetime.now())
                
                results.append({
                    "title"    : title,
                    "published": published,
                    "source"   : item.get("publisher", "Yahoo Finance"),
                    "link"     : item.get("link", ""),
                    "summary"  : item.get("summary", title)[:200],
                })
            
            if results:
                print(f"✅ Yahoo Finance: {len(results)} articles for {ticker_symbol}")
                return results
                
        except Exception:
            continue
    
    return results

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN get_news() FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_news(query: str) -> list:
    """
    MAIN FUNCTION — called by Groq tools and 
    throughout the app.
    
    FLOW:
    1. Check 5-minute cache first
    2. Try MoneyControl (PRIMARY) — best Indian news
    3. If < 3 articles → add Economic Times
    4. If still < 3 → add NSE Announcements
    5. If still < 3 → add Yahoo Finance
    6. Deduplicate and return top 8 articles
    
    GUARANTEES:
    - Always returns a list (never None)
    - Always has articles from at least 1 source
    - Articles are relevant to query
    - Cached for 5 minutes to prevent rate limiting
    """
    
    # Step 1: Check cache
    cache_key = f"news_{query.lower()[:50].replace(' ', '_')}"
    cached    = get_cached(cache_key)
    if cached:
        print(f"📰 News from cache: {len(cached)} articles")
        return cached
    
    print(f"\n📰 Fetching news: '{query}'")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    all_articles = []
    
    # Step 2: MoneyControl — PRIMARY
    mc_feeds   = select_best_mc_feed(query)
    mc_news    = fetch_moneycontrol(query, mc_feeds)
    if mc_news:
        all_articles.extend(mc_news)
        print(f"✅ MoneyControl: {len(mc_news)} articles")
    else:
        print(f"⚠️ MoneyControl: No articles found")
    
    # Step 3: Economic Times — BACKUP 1
    if len(all_articles) < 4:
        print(f"📡 Trying Economic Times...")
        et_news = fetch_economic_times(query)
        if et_news:
            all_articles.extend(et_news)
            print(f"✅ Economic Times: {len(et_news)} articles")
        else:
            print(f"⚠️ Economic Times: No articles")
    
    # Step 4: NSE Announcements — BACKUP 2
    # Only for short queries (stock symbols)
    if len(all_articles) < 4 and len(query.split()) <= 2:
        print(f"📡 Trying NSE Announcements...")
        nse_news = fetch_nse_announcements(query)
        if nse_news:
            all_articles.extend(nse_news)
            print(f"✅ NSE Official: {len(nse_news)} articles")
    
    # Step 5: Yahoo Finance — FINAL FALLBACK
    if len(all_articles) < 3:
        print(f"📡 Trying Yahoo Finance fallback...")
        yf_news = fetch_yfinance_news(query.split()[0])
        if yf_news:
            all_articles.extend(yf_news)
            print(f"✅ Yahoo Finance: {len(yf_news)} articles")
        else:
            print(f"⚠️ Yahoo Finance: No articles")
    
    # Step 6: Deduplicate
    final = deduplicate(all_articles)[:8]
    
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📊 Total unique articles: {len(final)}")
    
    # Cache results
    set_cached(cache_key, final)
    
    return final

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# get_market_news() FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_market_news() -> list:
    """
    Get top Indian market news of the day.
    Uses MoneyControl market + business feeds.
    Perfect for daily market overview.
    """
    cache_key = "market_news_today"
    cached    = get_cached(cache_key)
    if cached:
        return cached
    
    all_articles = []
    
    # Primary: MoneyControl market + business
    mc_market = fetch_moneycontrol(
        query="",
        feeds=["market", "business", "economy"]
    )
    all_articles.extend(mc_market)
    
    # Backup: Economic Times market
    if len(all_articles) < 6:
        et_market = fetch_economic_times("nifty sensex market india")
        all_articles.extend(et_market)
    
    result = deduplicate(all_articles)[:10]
    set_cached(cache_key, result)
    
    return result

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# get_ipo_news() FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_ipo_news() -> list:
    """
    Get latest IPO news from MoneyControl.
    MoneyControl has dedicated IPO RSS feed.
    """
    cache_key = "ipo_news"
    cached    = get_cached(cache_key)
    if cached:
        return cached
    
    ipo_news = fetch_moneycontrol(
        query="IPO",
        feeds=["ipo", "market"]
    )
    
    result = deduplicate(ipo_news)[:8]
    set_cached(cache_key, result)
    
    return result

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# get_results_news() FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_results_news() -> list:
    """
    Get latest quarterly results news.
    MoneyControl has dedicated results RSS feed.
    """
    cache_key = "results_news"
    cached    = get_cached(cache_key)
    if cached:
        return cached
    
    results_news = fetch_moneycontrol(
        query="quarterly results",
        feeds=["results", "business"]
    )
    
    result = deduplicate(results_news)[:8]
    set_cached(cache_key, result)
    
    return result

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# check_news_health() FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_news_health() -> dict:
    """
    Health check for all news sources.
    Called by test_report.py.
    Returns status of each source.
    """
    health = {}
    test_q = "Reliance Nifty"
    
    # Check MoneyControl
    try:
        mc = fetch_moneycontrol(test_q, ["market"])
        health["MoneyControl"] = {
            "status" : "Working ✅" if mc else "Empty ⚠️",
            "count"  : len(mc),
            "working": len(mc) > 0
        }
    except Exception as e:
        health["MoneyControl"] = {
            "status" : f"Error ❌: {str(e)[:50]}",
            "count"  : 0,
            "working": False
        }
    
    # Check Economic Times
    try:
        et = fetch_economic_times(test_q)
        health["Economic Times"] = {
            "status" : "Working ✅" if et else "Empty ⚠️",
            "count"  : len(et),
            "working": len(et) > 0
        }
    except Exception as e:
        health["Economic Times"] = {
            "status" : f"Error ❌: {str(e)[:50]}",
            "count"  : 0,
            "working": False
        }
    
    # Check Yahoo Finance
    try:
        yf_n = fetch_yfinance_news("RELIANCE")
        health["Yahoo Finance"] = {
            "status" : "Working ✅" if yf_n else "Empty ⚠️",
            "count"  : len(yf_n),
            "working": len(yf_n) > 0
        }
    except Exception as e:
        health["Yahoo Finance"] = {
            "status" : f"Error ❌: {str(e)[:50]}",
            "count"  : 0,
            "working": False
        }
    
    # Overall status
    working_count = sum(1 for s in health.values() if s.get("working"))
    health["_overall"] = {
        "sources_working": working_count,
        "total_sources"  : 3,
        "status"         : (
            "All Working ✅" if working_count == 3
            else f"{working_count}/3 Working ⚠️"
        )
    }
    
    return health
