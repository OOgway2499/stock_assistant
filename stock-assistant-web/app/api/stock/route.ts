/**
 * GET /api/stock?symbol=RELIANCE&type=price|technicals|fundamentals
 */
import { NextRequest, NextResponse } from "next/server";
import { getStockPrice, getTechnicals, getFundamentals } from "@/lib/stockData";

export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const symbol = searchParams.get("symbol");
        const type = searchParams.get("type") || "price";

        if (!symbol) {
            return NextResponse.json({ error: "Symbol is required" }, { status: 400 });
        }

        let data;

        switch (type) {
            case "technicals":
                data = await getTechnicals(symbol, searchParams.get("period") || "6mo");
                break;
            case "fundamentals":
                data = await getFundamentals(symbol);
                break;
            case "price":
            default:
                data = await getStockPrice(symbol);
                break;
        }

        return NextResponse.json(data);
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return NextResponse.json({ error: msg }, { status: 500 });
    }
}
