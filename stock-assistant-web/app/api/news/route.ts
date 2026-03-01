/**
 * GET /api/news?query=Infosys — Google News RSS search.
 */
import { NextRequest, NextResponse } from "next/server";
import { getNews } from "@/lib/newsData";

export async function GET(req: NextRequest) {
    try {
        const query = new URL(req.url).searchParams.get("query") || "Indian stock market";
        const articles = await getNews(query);
        return NextResponse.json({ articles });
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return NextResponse.json({ error: msg }, { status: 500 });
    }
}
