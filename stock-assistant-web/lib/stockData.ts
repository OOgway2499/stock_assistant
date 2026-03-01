/**
 * Stock Data Functions — Uses yahoo-finance2 (server-side).
 * Replaces Python yfinance with equivalent npm package.
 */
/* eslint-disable @typescript-eslint/no-explicit-any */

import yahooFinance from "yahoo-finance2";

/**
 * Get current stock price for an NSE/BSE stock.
 */
export async function getStockPrice(symbol: string) {
    try {
        const suffixes = [".NS", ".BO"];
        for (const suffix of suffixes) {
            try {
                const quote: any = await yahooFinance.quote(
                    symbol.toUpperCase() + suffix
                );
                if (!quote || !quote.regularMarketPrice) continue;

                const currentPrice = quote.regularMarketPrice;
                const previousClose = quote.regularMarketPreviousClose ?? 0;
                const change = +(currentPrice - previousClose).toFixed(2);
                const changePercent = previousClose
                    ? +((change / previousClose) * 100).toFixed(2)
                    : 0;

                return {
                    symbol: symbol.toUpperCase(),
                    companyName: quote.longName || quote.shortName || symbol,
                    currentPrice,
                    open: quote.regularMarketOpen ?? 0,
                    high: quote.regularMarketDayHigh ?? 0,
                    low: quote.regularMarketDayLow ?? 0,
                    previousClose,
                    volume: quote.regularMarketVolume ?? 0,
                    change,
                    changePercent,
                    exchange: suffix === ".NS" ? "NSE" : "BSE",
                    dataSource: "Yahoo Finance (15 min delayed)",
                };
            } catch {
                continue;
            }
        }
        return { error: `No data found for ${symbol}` };
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { error: `Stock data unavailable: ${msg}` };
    }
}

/**
 * Get historical OHLCV data.
 */
export async function getStockHistory(
    symbol: string,
    period: string = "3mo"
) {
    try {
        const now = new Date();
        const startDate = new Date();

        const periodMap: Record<string, number> = {
            "1mo": 30,
            "3mo": 90,
            "6mo": 180,
            "1y": 365,
            "2y": 730,
        };
        startDate.setDate(now.getDate() - (periodMap[period] || 90));

        const result: any[] = await yahooFinance.historical(
            symbol.toUpperCase() + ".NS",
            { period1: startDate, period2: now, interval: "1d" }
        );

        if (!result || result.length === 0) {
            return { error: `No historical data for ${symbol}` };
        }

        return result.map((r: any) => ({
            date: new Date(r.date).toISOString().split("T")[0],
            open: r.open,
            high: r.high,
            low: r.low,
            close: r.close,
            volume: r.volume,
        }));
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { error: `History not available: ${msg}` };
    }
}

/**
 * Get fundamental data for a stock.
 */
export async function getFundamentals(symbol: string) {
    try {
        const ticker = symbol.toUpperCase() + ".NS";
        const result: any = await yahooFinance.quoteSummary(ticker, {
            modules: [
                "summaryDetail",
                "defaultKeyStatistics",
                "financialData",
                "assetProfile",
            ],
        });

        const sd = result.summaryDetail || {};
        const ks = result.defaultKeyStatistics || {};
        const fd = result.financialData || {};
        const ap = result.assetProfile || {};

        const pe = sd.trailingPE ?? null;
        const de = fd.debtToEquity ?? null;
        const roe = fd.returnOnEquity ?? null;

        // PE signal
        let peSignal = "⚪ PE data not available";
        if (pe !== null) {
            if (pe < 10) peSignal = "🟢 Very undervalued (or declining business)";
            else if (pe < 15) peSignal = "🟢 Potentially undervalued";
            else if (pe < 25) peSignal = "⚪ Fairly valued";
            else if (pe < 40) peSignal = "🟡 Slightly overvalued";
            else peSignal = "🔴 Highly overvalued";
        }

        // Debt signal
        let debtSignal = "⚪ Debt data not available";
        if (de !== null) {
            const ratio = de > 5 ? de / 100 : de;
            if (ratio < 0.5) debtSignal = "🟢 Low debt — financially strong";
            else if (ratio < 1.0) debtSignal = "🟡 Moderate debt";
            else debtSignal = "🔴 High debt — risk factor";
        }

        // ROE signal
        let roeSignal = "⚪ ROE data not available";
        if (roe !== null) {
            const pct = roe < 1 ? roe * 100 : roe;
            if (pct > 20) roeSignal = "🟢 Excellent returns";
            else if (pct > 10) roeSignal = "🟡 Good returns";
            else roeSignal = "🔴 Low returns";
        }

        const marketCap = sd.marketCap ?? 0;

        return {
            symbol: symbol.toUpperCase(),
            companyName: ap.longName || symbol,
            sector: ap.sector || "N/A",
            industry: ap.industry || "N/A",
            currentPrice: fd.currentPrice ?? 0,
            marketCap,
            marketCapCrores: +(marketCap / 10_000_000).toFixed(2),
            peRatio: pe,
            forwardPE: ks.forwardPE ?? null,
            pbRatio: sd.priceToBook ?? null,
            eps: ks.trailingEps ?? null,
            dividendYield: sd.dividendYield ?? null,
            week52High: sd.fiftyTwoWeekHigh ?? 0,
            week52Low: sd.fiftyTwoWeekLow ?? 0,
            debtToEquity: de,
            roe,
            revenueGrowth: fd.revenueGrowth ?? null,
            profitMargins: fd.profitMargins ?? null,
            peSignal,
            debtSignal,
            roeSignal,
            dataSource: "Yahoo Finance",
        };
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { error: `Fundamentals not available: ${msg}` };
    }
}

// ── Technical indicator helpers ─────────────────────────────────

function calcSMA(data: number[], period: number): number | null {
    if (data.length < period) return null;
    const slice = data.slice(-period);
    return +(slice.reduce((a, b) => a + b, 0) / period).toFixed(2);
}

function calcEMA(data: number[], period: number): number[] {
    const k = 2 / (period + 1);
    const ema: number[] = [data[0]];
    for (let i = 1; i < data.length; i++) {
        ema.push(data[i] * k + ema[i - 1] * (1 - k));
    }
    return ema;
}

function calcRSI(closes: number[], period: number = 14): number | null {
    if (closes.length < period + 1) return null;
    let gains = 0,
        losses = 0;
    for (let i = 1; i <= period; i++) {
        const diff = closes[i] - closes[i - 1];
        if (diff > 0) gains += diff;
        else losses += Math.abs(diff);
    }
    let avgGain = gains / period;
    let avgLoss = losses / period;

    for (let i = period + 1; i < closes.length; i++) {
        const diff = closes[i] - closes[i - 1];
        avgGain = (avgGain * (period - 1) + (diff > 0 ? diff : 0)) / period;
        avgLoss =
            (avgLoss * (period - 1) + (diff < 0 ? Math.abs(diff) : 0)) / period;
    }

    if (avgLoss === 0) return 100;
    const rs = avgGain / avgLoss;
    return +(100 - 100 / (1 + rs)).toFixed(2);
}

/**
 * Calculate technical indicators for a stock.
 */
export async function getTechnicals(
    symbol: string,
    period: string = "6mo"
) {
    try {
        const history = await getStockHistory(symbol, period);
        if ("error" in history) return history;
        if (!Array.isArray(history) || history.length < 20) {
            return { error: `Not enough data for technical analysis of ${symbol}` };
        }

        const closes = history.map((h: any) => h.close);
        const currentPrice = closes[closes.length - 1];

        // RSI
        const rsi = calcRSI(closes, 14);
        let rsiSignal = "⚪ RSI data not available";
        if (rsi !== null) {
            if (rsi > 70) rsiSignal = "🔴 Overbought — stock may pullback soon";
            else if (rsi > 60) rsiSignal = "🟡 Mildly overbought — watch carefully";
            else if (rsi > 40) rsiSignal = "⚪ Neutral zone — no strong signal";
            else if (rsi > 30) rsiSignal = "🟡 Mildly oversold — possible bounce";
            else rsiSignal = "🟢 Oversold — possible buying opportunity";
        }

        // SMAs
        const sma20 = calcSMA(closes, 20);
        const sma50 = calcSMA(closes, 50);
        const sma200 = calcSMA(closes, 200);

        // Trend
        let trend = "⚪ Not enough data for trend";
        if (sma50 !== null && sma200 !== null) {
            if (currentPrice > sma50 && sma50 > sma200) trend = "📈 Strong Uptrend";
            else if (currentPrice > sma50) trend = "📈 Uptrend";
            else if (currentPrice < sma50 && sma50 < sma200)
                trend = "📉 Strong Downtrend";
            else if (currentPrice < sma50) trend = "📉 Downtrend";
            else trend = "⚪ Sideways";
        }

        // MACD
        const ema12 = calcEMA(closes, 12);
        const ema26 = calcEMA(closes, 26);
        const macdLine = ema12.map((v, i) => v - ema26[i]);
        const signalLine = calcEMA(macdLine.slice(26), 9);
        const macd = +(macdLine[macdLine.length - 1] ?? 0).toFixed(2);
        const macdSig = +(signalLine[signalLine.length - 1] ?? 0).toFixed(2);

        let macdSignal = "⚪ MACD data not available";
        if (macd && macdSig) {
            macdSignal =
                macd > macdSig ? "🟢 Bullish momentum" : "🔴 Bearish momentum";
        }

        // Bollinger Bands
        const bb = calcSMA(closes, 20);
        let bbUpper: number | null = null;
        let bbLower: number | null = null;
        if (bb !== null && closes.length >= 20) {
            const slice = closes.slice(-20);
            const std = Math.sqrt(
                slice.reduce((sum: number, v: number) => sum + (v - bb) ** 2, 0) / 20
            );
            bbUpper = +(bb + 2 * std).toFixed(2);
            bbLower = +(bb - 2 * std).toFixed(2);
        }

        return {
            symbol: symbol.toUpperCase(),
            currentPrice: +currentPrice.toFixed(2),
            indicators: {
                RSI_14: rsi,
                MACD: macd,
                MACD_Signal: macdSig,
                SMA_20: sma20,
                SMA_50: sma50,
                SMA_200: sma200,
                Bollinger_Upper: bbUpper,
                Bollinger_Lower: bbLower,
            },
            signals: {
                rsiSignal,
                trend,
                macdSignal,
            },
            dataSource: "Yahoo Finance",
        };
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return { error: `Technical analysis failed: ${msg}` };
    }
}
