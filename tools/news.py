"""
News Tool — Fetches stock and market news from Google News RSS.
Free, no API key required.
"""

import feedparser
from urllib.parse import quote_plus


def get_news(query: str) -> list:
    """
    Search Google News RSS for stock-related articles.

    Args:
        query: search term, e.g. "Infosys results", "Nifty today"

    Returns:
        list of news article dicts or empty list
    """
    try:
        # Primary search with Indian stock context
        encoded = quote_plus(f"{query} NSE India stock")
        url = (
            f"https://news.google.com/rss/search?"
            f"q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
        )
        feed = feedparser.parse(url)

        # Fallback — try without stock qualifier
        if not feed.entries:
            encoded = quote_plus(query)
            url = (
                f"https://news.google.com/rss/search?"
                f"q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
            )
            feed = feedparser.parse(url)

        articles = []
        for entry in feed.entries[:6]:
            summary = entry.get("summary", "")
            if len(summary) > 150:
                summary = summary[:150] + "..."

            articles.append({
                "title": entry.get("title", ""),
                "published": entry.get("published", ""),
                "source": entry.get("source", {}).get("title", "Unknown"),
                "summary": summary,
                "link": entry.get("link", ""),
            })

        return articles

    except Exception as e:
        print(f"⚠️ [news.get_news] Error: {e}")
        return []


def get_market_news() -> list:
    """
    Get general Indian stock market news.

    Returns:
        list of top 8 market news articles
    """
    try:
        encoded = quote_plus("Indian stock market NSE BSE today")
        url = (
            f"https://news.google.com/rss/search?"
            f"q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
        )
        feed = feedparser.parse(url)

        articles = []
        for entry in feed.entries[:8]:
            summary = entry.get("summary", "")
            if len(summary) > 150:
                summary = summary[:150] + "..."

            articles.append({
                "title": entry.get("title", ""),
                "published": entry.get("published", ""),
                "source": entry.get("source", {}).get("title", "Unknown"),
                "summary": summary,
                "link": entry.get("link", ""),
            })

        return articles

    except Exception as e:
        print(f"⚠️ [news.get_market_news] Error: {e}")
        return []
