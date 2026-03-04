/**
 * GET /api/angel — Angel One SmartAPI routes.
 * Handles: price, historical, portfolio, depth, status, ticker.
 * All credentials server-side only.
 */
/* eslint-disable @typescript-eslint/no-explicit-any */

import { NextRequest, NextResponse } from "next/server";
import {
    getAngelLivePrice,
    getAngelHistorical,
    getAngelPortfolio,
    getAngelMarketDepth,
    getAngelStatus,
    getAngelMultiplePrices,
} from "@/lib/angelOne";

export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const type = searchParams.get("type") || "status";
        const symbol = searchParams.get("symbol") || "";

        switch (type) {
            case "price": {
                if (!symbol) {
                    return NextResponse.json({ error: "symbol required" }, { status: 400 });
                }
                const price = await getAngelLivePrice(symbol);
                if (price) return NextResponse.json(price);
                return NextResponse.json({ error: "Price not available" }, { status: 404 });
            }

            case "historical": {
                if (!symbol) {
                    return NextResponse.json({ error: "symbol required" }, { status: 400 });
                }
                const interval = searchParams.get("interval") || "ONE_DAY";
                const from = searchParams.get("from") || undefined;
                const to = searchParams.get("to") || undefined;
                const candles = await getAngelHistorical(symbol, interval, from, to);
                if (candles) return NextResponse.json({ data: candles });
                return NextResponse.json({ error: "Historical data not available" }, { status: 404 });
            }

            case "portfolio": {
                const holdings = await getAngelPortfolio();
                if (holdings) return NextResponse.json({ holdings });
                return NextResponse.json({ holdings: [], error: "Portfolio not available" });
            }

            case "depth": {
                if (!symbol) {
                    return NextResponse.json({ error: "symbol required" }, { status: 400 });
                }
                const depth = await getAngelMarketDepth(symbol);
                if (depth) return NextResponse.json(depth);
                return NextResponse.json({ error: "Depth not available" }, { status: 404 });
            }

            case "ticker": {
                const symbols = (searchParams.get("symbols") || "RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK,SBIN,WIPRO,AXISBANK")
                    .split(",")
                    .map((s) => s.trim());
                const prices = await getAngelMultiplePrices(symbols);
                if (prices) return NextResponse.json({ prices, isRealtime: true });
                return NextResponse.json({ prices: [], isRealtime: false });
            }

            case "status":
            default: {
                const status = await getAngelStatus();
                return NextResponse.json(status);
            }
        }
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return NextResponse.json({ error: msg }, { status: 500 });
    }
}
