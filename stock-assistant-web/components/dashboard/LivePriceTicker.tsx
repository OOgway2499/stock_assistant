"use client";
import { useState, useEffect } from "react";

interface TickerPrice {
    symbol: string;
    currentPrice: number;
    change: number;
    changePercent: number;
    isRealtime: boolean;
}

const TICKER_SYMBOLS = "RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK,SBIN,WIPRO,AXISBANK";

export default function LivePriceTicker() {
    const [prices, setPrices] = useState<TickerPrice[]>([]);
    const [isRealtime, setIsRealtime] = useState(false);

    useEffect(() => {
        const fetchTicker = async () => {
            try {
                // Try Angel One first
                const angelRes = await fetch(
                    `/api/angel?type=ticker&symbols=${TICKER_SYMBOLS}`,
                    { signal: AbortSignal.timeout(8000) }
                );
                const angelData = await angelRes.json();

                if (angelData.prices && angelData.prices.length > 0) {
                    setPrices(angelData.prices);
                    setIsRealtime(angelData.isRealtime);
                    return;
                }
            } catch {
                // Fallback below
            }

            // Fallback: fetch from /api/stock individually (first 4 only)
            try {
                const symbols = TICKER_SYMBOLS.split(",").slice(0, 4);
                const results = await Promise.all(
                    symbols.map(async (sym) => {
                        const res = await fetch(`/api/stock?symbol=${sym}&type=price`, {
                            signal: AbortSignal.timeout(8000),
                        });
                        return res.json();
                    })
                );
                setPrices(
                    results
                        .filter((r) => !r.error)
                        .map((r) => ({
                            symbol: r.symbol,
                            currentPrice: r.currentPrice,
                            change: r.change || 0,
                            changePercent: r.changePercent || 0,
                            isRealtime: false,
                        }))
                );
                setIsRealtime(false);
            } catch {
                // Silent fail — ticker is non-essential
            }
        };

        fetchTicker();
        const interval = setInterval(fetchTicker, isRealtime ? 10000 : 30000);
        return () => clearInterval(interval);
    }, [isRealtime]);

    if (prices.length === 0) return null;

    return (
        <div className="overflow-hidden border-b border-gray-800 bg-[#080c14]">
            <div className="flex items-center">
                {/* Live badge */}
                <div className="shrink-0 px-3 py-1.5 border-r border-gray-800">
                    {isRealtime ? (
                        <span className="flex items-center gap-1.5 text-[10px] font-semibold text-green-400">
                            <span className="inline-block h-1.5 w-1.5 rounded-full bg-green-400 live-pulse" />
                            LIVE
                        </span>
                    ) : (
                        <span className="flex items-center gap-1.5 text-[10px] font-semibold text-yellow-500">
                            <span className="inline-block h-1.5 w-1.5 rounded-full bg-yellow-500" />
                            DELAYED
                        </span>
                    )}
                </div>

                {/* Scrolling ticker */}
                <div className="flex-1 overflow-hidden">
                    <div className="animate-marquee flex gap-6 whitespace-nowrap py-1.5 px-2">
                        {[...prices, ...prices].map((p, i) => {
                            const isUp = p.change >= 0;
                            return (
                                <span key={`${p.symbol}-${i}`} className="inline-flex items-center gap-1.5 text-xs">
                                    <span className="font-semibold text-gray-300">{p.symbol}</span>
                                    <span className="text-gray-400">₹{p.currentPrice?.toLocaleString("en-IN")}</span>
                                    <span className={`font-semibold ${isUp ? "text-green-400" : "text-red-400"}`}>
                                        {isUp ? "▲" : "▼"} {Math.abs(p.changePercent || 0).toFixed(2)}%
                                    </span>
                                </span>
                            );
                        })}
                    </div>
                </div>
            </div>

            <style jsx>{`
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
        .animate-marquee:hover {
          animation-play-state: paused;
        }
      `}</style>
        </div>
    );
}
