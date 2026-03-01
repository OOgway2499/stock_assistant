/**
 * NSE India Data — Fetches from NSE's public API.
 * Requires session cookie setup (initial fetch to homepage).
 */

const NSE_HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    Accept: "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    Referer: "https://www.nseindia.com",
};

/**
 * Create a fetch call with NSE cookies.
 * First hits the homepage, then the actual API.
 */
async function nseFetch(url: string): Promise<Response> {
    // Get cookies from homepage
    await fetch("https://www.nseindia.com", {
        headers: NSE_HEADERS,
        signal: AbortSignal.timeout(10000),
    }).catch(() => { });

    return fetch(url, {
        headers: NSE_HEADERS,
        signal: AbortSignal.timeout(10000),
    });
}

/**
 * Get all NSE indices data.
 */
export async function getAllIndices() {
    try {
        const res = await nseFetch("https://www.nseindia.com/api/allIndices");
        if (!res.ok) throw new Error(`NSE API returned ${res.status}`);
        return await res.json();
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { error: `NSE indices unavailable: ${msg}` };
    }
}

/**
 * Get specific indices by name.
 */
export async function getIndices(names: string[]) {
    try {
        const data = await getAllIndices();
        if (data.error) return data;

        const targets = names.map((n) => n.toUpperCase());
        interface IndexRecord {
            index?: string;
            last?: number;
            variation?: number;
            percentChange?: number;
            open?: number;
            high?: number;
            low?: number;
            previousClose?: number;
            yearHigh?: number;
            yearLow?: number;
        }
        const indices = (data.data || [])
            .filter((d: IndexRecord) => targets.includes((d.index || "").toUpperCase()))
            .map((d: IndexRecord) => ({
                name: d.index,
                lastPrice: d.last,
                change: d.variation,
                pChange: d.percentChange,
                open: d.open,
                high: d.high,
                low: d.low,
                previousClose: d.previousClose,
                yearHigh: d.yearHigh,
                yearLow: d.yearLow,
            }));

        return indices;
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { error: `NSE data unavailable: ${msg}` };
    }
}

/**
 * Get top gainers.
 */
export async function getTopGainers() {
    try {
        const res = await nseFetch(
            "https://www.nseindia.com/api/live-analysis-variations?index=gainers"
        );
        if (!res.ok) throw new Error(`NSE API returned ${res.status}`);
        const data = await res.json();

        interface StockRecord {
            symbol?: string;
            meta?: { companyName?: string };
            lastPrice?: number;
            change?: number;
            pChange?: number;
        }
        const stocks = data.NIFTY || data.data || [];
        return stocks.slice(0, 10).map((s: StockRecord) => ({
            symbol: s.symbol,
            companyName: s.meta?.companyName || s.symbol,
            lastPrice: s.lastPrice,
            change: s.change,
            pChange: s.pChange,
        }));
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { error: `Gainers unavailable: ${msg}` };
    }
}

/**
 * Get top losers.
 */
export async function getTopLosers() {
    try {
        const res = await nseFetch(
            "https://www.nseindia.com/api/live-analysis-variations?index=losers"
        );
        if (!res.ok) throw new Error(`NSE API returned ${res.status}`);
        const data = await res.json();

        interface StockRecord {
            symbol?: string;
            meta?: { companyName?: string };
            lastPrice?: number;
            change?: number;
            pChange?: number;
        }
        const stocks = data.NIFTY || data.data || [];
        return stocks.slice(0, 10).map((s: StockRecord) => ({
            symbol: s.symbol,
            companyName: s.meta?.companyName || s.symbol,
            lastPrice: s.lastPrice,
            change: s.change,
            pChange: s.pChange,
        }));
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { error: `Losers unavailable: ${msg}` };
    }
}

/**
 * Get market status (open/closed).
 */
export async function getMarketStatus() {
    try {
        const res = await nseFetch("https://www.nseindia.com/api/marketStatus");
        if (!res.ok) throw new Error(`NSE API returned ${res.status}`);
        const data = await res.json();

        interface MarketState {
            market?: string;
            marketStatus?: string;
            tradeDate?: string;
        }
        const states = (data.marketState || []).map((m: MarketState) => ({
            market: m.market,
            status: m.marketStatus,
            tradeDate: m.tradeDate,
        }));

        const capitalMarket = states.find(
            (s: { market?: string }) => s.market === "Capital Market"
        );
        return {
            statuses: states,
            isOpen: capitalMarket?.status?.toLowerCase().includes("open") ?? false,
        };
    } catch {
        return { statuses: [], isOpen: false, error: "Market status unavailable" };
    }
}

/**
 * Get comprehensive market overview.
 */
export async function getMarketOverview() {
    try {
        const [indices, gainers, losers, status] = await Promise.all([
            getIndices([
                "NIFTY 50",
                "NIFTY BANK",
                "NIFTY IT",
                "NIFTY PHARMA",
                "NIFTY AUTO",
                "NIFTY FMCG",
                "NIFTY METAL",
                "NIFTY ENERGY",
            ]),
            getTopGainers(),
            getTopLosers(),
            getMarketStatus(),
        ]);

        return {
            indices: Array.isArray(indices) ? indices : [],
            gainers: Array.isArray(gainers) ? gainers : [],
            losers: Array.isArray(losers) ? losers : [],
            marketStatus: status.isOpen ? "open" : "closed",
            lastUpdated: new Date().toISOString(),
        };
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { error: `Market overview unavailable: ${msg}` };
    }
}
