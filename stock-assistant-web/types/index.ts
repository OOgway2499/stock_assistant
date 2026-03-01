// ── Message Types ───────────────────────────────────────────────

export interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    toolsUsed?: string[];
}

// ── Stock Types ─────────────────────────────────────────────────

export interface StockPrice {
    symbol: string;
    companyName: string;
    currentPrice: number;
    change: number;
    changePercent: number;
    volume: number;
    high: number;
    low: number;
    open: number;
    previousClose: number;
    dataSource: string;
}

export interface TechnicalData {
    symbol: string;
    currentPrice: number;
    rsi: number | null;
    rsiSignal: string;
    macd: number | null;
    macdSignalLine: number | null;
    macdSignal: string;
    sma20: number | null;
    sma50: number | null;
    sma200: number | null;
    trend: string;
    bbUpper: number | null;
    bbLower: number | null;
}

export interface FundamentalData {
    symbol: string;
    companyName: string;
    sector: string;
    industry: string;
    currentPrice: number;
    marketCap: number;
    marketCapCrores: number;
    peRatio: number | null;
    pbRatio: number | null;
    eps: number | null;
    dividendYield: number | null;
    week52High: number;
    week52Low: number;
    debtToEquity: number | null;
    roe: number | null;
    revenueGrowth: number | null;
    profitMargins: number | null;
    peSignal: string;
    debtSignal: string;
    roeSignal: string;
}

// ── Market Types ────────────────────────────────────────────────

export interface MarketIndex {
    name: string;
    lastPrice: number;
    change: number;
    pChange: number;
    high: number;
    low: number;
    previousClose: number;
    yearHigh?: number;
    yearLow?: number;
}

export interface GainerLoser {
    symbol: string;
    companyName: string;
    lastPrice: number;
    change: number;
    pChange: number;
}

export interface MarketOverview {
    indices: MarketIndex[];
    gainers: GainerLoser[];
    losers: GainerLoser[];
    marketStatus: string;
    lastUpdated: string;
}

// ── News Types ──────────────────────────────────────────────────

export interface NewsArticle {
    title: string;
    published: string;
    source: string;
    link: string;
    summary: string;
}

// ── API Response Types ──────────────────────────────────────────

export interface ApiResponse<T> {
    data?: T;
    error?: string;
}

export interface ChatResponse {
    response: string;
    toolsUsed: string[];
}
