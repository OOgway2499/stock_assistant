/**
 * GET /api/market — NSE market overview with 60s cache.
 */
import { NextResponse } from "next/server";
import { getMarketOverview } from "@/lib/nseData";

export const revalidate = 60; // Cache for 60 seconds

export async function GET() {
    try {
        const data = await getMarketOverview();
        return NextResponse.json(data);
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return NextResponse.json({ error: msg }, { status: 500 });
    }
}
