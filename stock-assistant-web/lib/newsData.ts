/**
 * News Data — Fetches from Google News RSS, parses XML.
 */
import { XMLParser } from "fast-xml-parser";

interface RssItem {
    title?: string;
    pubDate?: string;
    link?: string;
    description?: string;
    source?: string | { "#text"?: string };
}

export async function getNews(query: string) {
    try {
        const encoded = encodeURIComponent(`${query} NSE India stock`);
        const url = `https://news.google.com/rss/search?q=${encoded}&hl=en-IN&gl=IN&ceid=IN:en`;

        const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
        const xml = await res.text();

        const parser = new XMLParser({ ignoreAttributes: false });
        const parsed = parser.parse(xml);

        let items: RssItem[] =
            parsed?.rss?.channel?.item || [];
        if (!Array.isArray(items)) items = [items];

        return items.slice(0, 6).map((item: RssItem) => ({
            title: item.title || "",
            published: item.pubDate || "",
            source:
                typeof item.source === "object"
                    ? item.source?.["#text"] || "Unknown"
                    : item.source || "Unknown",
            link: item.link || "",
            summary: (item.description || "").slice(0, 150),
        }));
    } catch {
        // Fallback — try without stock qualifier
        try {
            const encoded = encodeURIComponent(query);
            const url = `https://news.google.com/rss/search?q=${encoded}&hl=en-IN&gl=IN&ceid=IN:en`;
            const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
            const xml = await res.text();
            const parser = new XMLParser({ ignoreAttributes: false });
            const parsed = parser.parse(xml);

            let items: RssItem[] =
                parsed?.rss?.channel?.item || [];
            if (!Array.isArray(items)) items = [items];

            return items.slice(0, 6).map((item: RssItem) => ({
                title: item.title || "",
                published: item.pubDate || "",
                source:
                    typeof item.source === "object"
                        ? item.source?.["#text"] || "Unknown"
                        : item.source || "Unknown",
                link: item.link || "",
                summary: (item.description || "").slice(0, 150),
            }));
        } catch {
            return [];
        }
    }
}
