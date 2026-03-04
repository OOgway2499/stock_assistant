/**
 * Angel One SmartAPI Client — Server-side only.
 * Handles TOTP generation, login, and API calls via REST.
 * Uses Node.js crypto for TOTP (no external package needed).
 */

import crypto from "crypto";

// ── Stock Token Map (same as Python backend) ────────────────────
const STOCK_TOKENS: Record<string, string> = {
    RELIANCE: "2885",
    TCS: "11536",
    INFY: "1594",
    HDFCBANK: "1333",
    ICICIBANK: "4963",
    WIPRO: "3787",
    SBIN: "3045",
    AXISBANK: "5900",
    TATAMOTORS: "3456",
    ADANIENT: "25",
    BAJFINANCE: "317",
    KOTAKBANK: "1922",
    LT: "11483",
    HINDALCO: "1363",
    TATASTEEL: "3499",
    MARUTI: "10999",
    SUNPHARMA: "3351",
    BHARTIARTL: "10604",
    ASIANPAINT: "236",
    TITAN: "3506",
    ULTRACEMCO: "11532",
    NESTLEIND: "17963",
    POWERGRID: "14977",
    NTPC: "11630",
    ONGC: "2475",
    HCLTECH: "7229",
    TECHM: "13538",
    BAJAJFINSV: "16675",
    DIVISLAB: "10940",
    DRREDDY: "881",
    CIPLA: "694",
};

const ANGEL_BASE_URL = "https://apiconnect.angelbroking.com";

// ── TOTP Generation (RFC 6238) ──────────────────────────────────

function generateTOTP(secret: string): string {
    // Decode base32 secret
    const base32Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
    let bits = "";
    for (const c of secret.toUpperCase()) {
        const idx = base32Chars.indexOf(c);
        if (idx === -1) continue;
        bits += idx.toString(2).padStart(5, "0");
    }
    const keyBytes = Buffer.alloc(Math.floor(bits.length / 8));
    for (let i = 0; i < keyBytes.length; i++) {
        keyBytes[i] = parseInt(bits.slice(i * 8, i * 8 + 8), 2);
    }

    // Time-based counter (30-second step)
    const timeStep = Math.floor(Date.now() / 1000 / 30);
    const timeBuffer = Buffer.alloc(8);
    timeBuffer.writeBigUInt64BE(BigInt(timeStep));

    // HMAC-SHA1
    const hmac = crypto.createHmac("sha1", keyBytes).update(timeBuffer).digest();

    // Dynamic truncation
    const offset = hmac[hmac.length - 1] & 0x0f;
    const code =
        ((hmac[offset] & 0x7f) << 24) |
        ((hmac[offset + 1] & 0xff) << 16) |
        ((hmac[offset + 2] & 0xff) << 8) |
        (hmac[offset + 3] & 0xff);

    return (code % 1000000).toString().padStart(6, "0");
}

// ── Token Cache ─────────────────────────────────────────────────

interface TokenCache {
    jwtToken: string;
    feedToken: string;
    refreshToken: string;
    expiresAt: number; // timestamp ms
}

let cachedToken: TokenCache | null = null;

// ── Login ───────────────────────────────────────────────────────

async function loginAngelOne(
    apiKey: string
): Promise<TokenCache | null> {
    // Return cached token if still valid (15 min TTL)
    if (cachedToken && Date.now() < cachedToken.expiresAt) {
        return cachedToken;
    }

    const totpSecret = process.env.ANGEL_TOTP_SECRET;
    const clientId = process.env.ANGEL_CLIENT_ID;
    const password = process.env.ANGEL_PASSWORD;

    if (!totpSecret || !clientId || !password || !apiKey) {
        return null;
    }

    try {
        const totp = generateTOTP(totpSecret);

        const res = await fetch(
            `${ANGEL_BASE_URL}/rest/auth/angelbroking/user/v1/loginByPassword`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                    "X-UserType": "USER",
                    "X-SourceID": "WEB",
                    "X-ClientLocalIP": "127.0.0.1",
                    "X-ClientPublicIP": "127.0.0.1",
                    "X-MACAddress": "00:00:00:00:00:00",
                    "X-PrivateKey": apiKey,
                },
                body: JSON.stringify({
                    clientcode: clientId,
                    password: password,
                    totp: totp,
                }),
                signal: AbortSignal.timeout(10000),
            }
        );

        const data = await res.json();

        if (data.status && data.data) {
            cachedToken = {
                jwtToken: data.data.jwtToken,
                feedToken: data.data.feedToken,
                refreshToken: data.data.refreshToken,
                expiresAt: Date.now() + 15 * 60 * 1000, // 15 min
            };
            return cachedToken;
        }

        console.warn("[angelOne] Login failed:", data.message);
        return null;
    } catch (e) {
        console.warn("[angelOne] Login error:", e);
        return null;
    }
}

// ── Authenticated API Call ──────────────────────────────────────

async function angelFetch(
    path: string,
    apiKey: string,
    body?: Record<string, unknown>
): Promise<unknown> {
    const token = await loginAngelOne(apiKey);
    if (!token) return null;

    const res = await fetch(`${ANGEL_BASE_URL}${path}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: `Bearer ${token.jwtToken}`,
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "127.0.0.1",
            "X-ClientPublicIP": "127.0.0.1",
            "X-MACAddress": "00:00:00:00:00:00",
            "X-PrivateKey": apiKey,
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: AbortSignal.timeout(10000),
    });

    return res.json();
}

// ── Public API Functions ────────────────────────────────────────

function getToken(symbol: string): string | null {
    return STOCK_TOKENS[symbol.toUpperCase()] || null;
}

/**
 * Get live price from Angel One.
 */
export async function getAngelLivePrice(symbol: string) {
    try {
        const apiKey = process.env.ANGEL_FEEDS_API_KEY;
        if (!apiKey) return null;

        const token = getToken(symbol);
        if (!token) return null;

        const data: any = await angelFetch(
            "/rest/secure/angelbroking/market/v1/quote/",
            apiKey,
            {
                mode: "LTP",
                exchangeTokens: { NSE: [token] },
            }
        );

        if (data?.data?.fetched?.[0]) {
            const d = data.data.fetched[0];
            const ltp = d.ltp || 0;
            const close = d.close || 0;
            const change = +(ltp - close).toFixed(2);
            const changePct = close ? +((change / close) * 100).toFixed(2) : 0;

            return {
                symbol: symbol.toUpperCase(),
                companyName: symbol.toUpperCase(),
                currentPrice: ltp,
                open: d.open || 0,
                high: d.high || 0,
                low: d.low || 0,
                previousClose: close,
                volume: d.tradeVolume || 0,
                change,
                changePercent: changePct,
                exchange: "NSE",
                dataSource: "Angel One (Real-time ✅)",
            };
        }

        return null;
    } catch {
        return null;
    }
}

/**
 * Get historical candles from Angel One.
 */
export async function getAngelHistorical(
    symbol: string,
    interval: string = "ONE_DAY",
    fromDate?: string,
    toDate?: string
) {
    try {
        const apiKey = process.env.ANGEL_HISTORICAL_API_KEY;
        if (!apiKey) return null;

        const token = getToken(symbol);
        if (!token) return null;

        const now = new Date();
        const from = fromDate || new Date(now.getTime() - 180 * 24 * 60 * 60 * 1000)
            .toISOString().slice(0, 16).replace("T", " ");
        const to = toDate || now.toISOString().slice(0, 16).replace("T", " ");

        const data: any = await angelFetch(
            "/rest/secure/angelbroking/apiservice/v1/candleData",
            apiKey,
            {
                exchange: "NSE",
                symboltoken: token,
                interval,
                fromdate: from,
                todate: to,
            }
        );

        if (data?.data && Array.isArray(data.data)) {
            return data.data; // [[timestamp, O, H, L, C, V], ...]
        }

        return null;
    } catch {
        return null;
    }
}

/**
 * Get portfolio holdings from Angel One.
 */
export async function getAngelPortfolio() {
    try {
        const apiKey = process.env.ANGEL_TRADING_API_KEY;
        if (!apiKey) return null;

        const loginToken = await loginAngelOne(apiKey);
        if (!loginToken) return null;

        const res = await fetch(
            `${ANGEL_BASE_URL}/rest/secure/angelbroking/portfolio/v1/getHolding`,
            {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${loginToken.jwtToken}`,
                    "Content-Type": "application/json",
                    Accept: "application/json",
                    "X-UserType": "USER",
                    "X-SourceID": "WEB",
                    "X-ClientLocalIP": "127.0.0.1",
                    "X-ClientPublicIP": "127.0.0.1",
                    "X-MACAddress": "00:00:00:00:00:00",
                    "X-PrivateKey": apiKey,
                },
                signal: AbortSignal.timeout(10000),
            }
        );

        const data = await res.json();

        if (data?.data && Array.isArray(data.data)) {
            return data.data.map((h: any) => {
                const avg = parseFloat(h.averageprice || "0");
                const ltp = parseFloat(h.ltp || "0");
                const qty = parseInt(h.quantity || "0");
                const pnl = +((ltp - avg) * qty).toFixed(2);
                const pnlPct = avg ? +(((ltp - avg) / avg) * 100).toFixed(2) : 0;

                return {
                    symbol: (h.tradingsymbol || "").replace("-EQ", ""),
                    quantity: qty,
                    avgPrice: avg,
                    currentPrice: ltp,
                    pnl,
                    pnlPercent: pnlPct,
                    exchange: h.exchange || "NSE",
                };
            });
        }

        return null;
    } catch {
        return null;
    }
}

/**
 * Get market depth (top 5 bid/ask) from Angel One.
 */
export async function getAngelMarketDepth(symbol: string) {
    try {
        const apiKey = process.env.ANGEL_TRADING_API_KEY;
        if (!apiKey) return null;

        const token = getToken(symbol);
        if (!token) return null;

        const data: any = await angelFetch(
            "/rest/secure/angelbroking/market/v1/quote/",
            apiKey,
            {
                mode: "FULL",
                exchangeTokens: { NSE: [token] },
            }
        );

        if (data?.data?.fetched?.[0]) {
            const d = data.data.fetched[0];
            const depth = d.depth || {};

            return {
                symbol: symbol.toUpperCase(),
                ltp: d.ltp || 0,
                bids: (depth.buy || []).slice(0, 5).map((b: any) => ({
                    price: b.price || 0,
                    quantity: b.quantity || 0,
                })),
                asks: (depth.sell || []).slice(0, 5).map((a: any) => ({
                    price: a.price || 0,
                    quantity: a.quantity || 0,
                })),
                totalBuyQty: d.totBuyQuan || 0,
                totalSellQty: d.totSellQuan || 0,
                dataSource: "Angel One",
            };
        }

        return null;
    } catch {
        return null;
    }
}

/**
 * Check if Angel One is configured and reachable.
 */
export async function getAngelStatus() {
    const keys = {
        trading: !!process.env.ANGEL_TRADING_API_KEY,
        publisher: !!process.env.ANGEL_PUBLISHER_API_KEY,
        historical: !!process.env.ANGEL_HISTORICAL_API_KEY,
        feeds: !!process.env.ANGEL_FEEDS_API_KEY,
    };

    const hasCredentials =
        !!process.env.ANGEL_CLIENT_ID &&
        !!process.env.ANGEL_PASSWORD &&
        !!process.env.ANGEL_TOTP_SECRET;

    let isConnected = false;
    if (hasCredentials && keys.feeds) {
        try {
            const token = await loginAngelOne(process.env.ANGEL_FEEDS_API_KEY!);
            isConnected = !!token;
        } catch {
            isConnected = false;
        }
    }

    return {
        configured: hasCredentials,
        isConnected,
        apis: keys,
    };
}

/**
 * Get multiple live prices at once (for ticker).
 */
export async function getAngelMultiplePrices(symbols: string[]) {
    try {
        const apiKey = process.env.ANGEL_FEEDS_API_KEY;
        if (!apiKey) return null;

        const tokens: string[] = [];
        const symbolMap: Record<string, string> = {};

        for (const sym of symbols) {
            const t = getToken(sym);
            if (t) {
                tokens.push(t);
                symbolMap[t] = sym.toUpperCase();
            }
        }

        if (tokens.length === 0) return null;

        const data: any = await angelFetch(
            "/rest/secure/angelbroking/market/v1/quote/",
            apiKey,
            {
                mode: "OHLC",
                exchangeTokens: { NSE: tokens },
            }
        );

        if (data?.data?.fetched) {
            return data.data.fetched.map((d: any) => {
                const ltp = d.ltp || 0;
                const close = d.close || 0;
                const change = +(ltp - close).toFixed(2);
                const changePct = close ? +((change / close) * 100).toFixed(2) : 0;

                return {
                    symbol: symbolMap[d.symbolToken] || d.tradingSymbol || "?",
                    currentPrice: ltp,
                    change,
                    changePercent: changePct,
                    isRealtime: true,
                };
            });
        }

        return null;
    } catch {
        return null;
    }
}
