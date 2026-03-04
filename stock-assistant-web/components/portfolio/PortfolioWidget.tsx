"use client";
import { useState, useEffect } from "react";
import { Briefcase, RefreshCw } from "lucide-react";

interface Holding {
    symbol: string;
    quantity: number;
    avgPrice: number;
    currentPrice: number;
    pnl: number;
    pnlPercent: number;
}

export default function PortfolioWidget() {
    const [holdings, setHoldings] = useState<Holding[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [fetched, setFetched] = useState(false);

    const fetchPortfolio = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch("/api/angel?type=portfolio", {
                signal: AbortSignal.timeout(10000),
            });
            const data = await res.json();
            if (data.holdings && Array.isArray(data.holdings)) {
                setHoldings(data.holdings);
            } else if (data.error) {
                setError(data.error);
            }
        } catch {
            setError("Portfolio unavailable");
        } finally {
            setLoading(false);
            setFetched(true);
        }
    };

    useEffect(() => {
        // Only fetch once on mount — user can refresh manually
        fetchPortfolio();
    }, []);

    // Don't show if no portfolio data and no error
    if (fetched && holdings.length === 0 && !error) return null;

    const totalPnl = holdings.reduce((sum, h) => sum + h.pnl, 0);
    const totalValue = holdings.reduce((sum, h) => sum + h.currentPrice * h.quantity, 0);

    return (
        <div className="glass-card p-3">
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <Briefcase className="h-3.5 w-3.5 text-purple-400" />
                    <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                        Portfolio
                    </h3>
                </div>
                <button
                    onClick={fetchPortfolio}
                    disabled={loading}
                    className="p-1 text-gray-500 hover:text-white transition disabled:opacity-30"
                >
                    <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
                </button>
            </div>

            {loading && holdings.length === 0 ? (
                <div className="py-3 text-center text-xs text-gray-500">Loading portfolio...</div>
            ) : error ? (
                <div className="py-3 text-center text-xs text-gray-500">{error}</div>
            ) : holdings.length > 0 ? (
                <>
                    {/* Holdings list */}
                    <div className="space-y-1 max-h-48 overflow-y-auto">
                        {holdings.map((h) => {
                            const isUp = h.pnl >= 0;
                            return (
                                <div key={h.symbol} className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-white/5">
                                    <div>
                                        <span className="text-xs font-medium">{h.symbol}</span>
                                        <span className="ml-1.5 text-[10px] text-gray-500">
                                            {h.quantity} @ ₹{h.avgPrice.toFixed(0)}
                                        </span>
                                    </div>
                                    <div className="text-right">
                                        <span className="block text-xs text-gray-300">
                                            ₹{h.currentPrice.toFixed(2)}
                                        </span>
                                        <span className={`block text-[10px] font-semibold ${isUp ? "text-green-400" : "text-red-400"}`}>
                                            {isUp ? "+" : ""}₹{h.pnl.toFixed(0)} ({isUp ? "+" : ""}{h.pnlPercent.toFixed(1)}%)
                                        </span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Total */}
                    <div className="mt-2 flex justify-between border-t border-gray-800 pt-2 text-xs">
                        <span className="text-gray-400">
                            Value: ₹{totalValue.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                        </span>
                        <span className={`font-semibold ${totalPnl >= 0 ? "text-green-400" : "text-red-400"}`}>
                            P&L: {totalPnl >= 0 ? "+" : ""}₹{totalPnl.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                        </span>
                    </div>
                </>
            ) : null}
        </div>
    );
}
