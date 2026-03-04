"use client";
import { useState, useEffect } from "react";
import { X } from "lucide-react";

interface DepthLevel {
    price: number;
    quantity: number;
}

interface DepthData {
    symbol: string;
    ltp: number;
    bids: DepthLevel[];
    asks: DepthLevel[];
    totalBuyQty: number;
    totalSellQty: number;
}

interface Props {
    symbol: string | null;
    onClose: () => void;
}

export default function MarketDepth({ symbol, onClose }: Props) {
    const [depth, setDepth] = useState<DepthData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!symbol) return;

        const fetchDepth = async () => {
            setLoading(true);
            setError(null);
            try {
                const res = await fetch(
                    `/api/angel?type=depth&symbol=${encodeURIComponent(symbol)}`,
                    { signal: AbortSignal.timeout(8000) }
                );
                const data = await res.json();
                if (data.error) {
                    setError(data.error);
                } else {
                    setDepth(data);
                }
            } catch {
                setError("Market depth not available");
            } finally {
                setLoading(false);
            }
        };

        fetchDepth();
        const interval = setInterval(fetchDepth, 10000);
        return () => clearInterval(interval);
    }, [symbol]);

    if (!symbol) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className="glass-card w-full max-w-md mx-4 p-4">
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                    <div>
                        <h3 className="text-sm font-bold">{symbol} — Market Depth</h3>
                        {depth?.ltp && (
                            <span className="text-xs text-gray-400">LTP: ₹{depth.ltp.toLocaleString("en-IN")}</span>
                        )}
                    </div>
                    <button onClick={onClose} className="p-1 text-gray-400 hover:text-white transition">
                        <X className="h-4 w-4" />
                    </button>
                </div>

                {loading && !depth ? (
                    <div className="py-8 text-center text-sm text-gray-500">Loading depth...</div>
                ) : error ? (
                    <div className="py-8 text-center text-sm text-gray-500">{error}</div>
                ) : depth ? (
                    <>
                        {/* Bid / Ask Table */}
                        <div className="grid grid-cols-2 gap-2">
                            {/* Bids */}
                            <div>
                                <div className="mb-1 flex justify-between text-[10px] font-medium text-gray-500 px-1">
                                    <span>Buy Qty</span>
                                    <span>Bid Price</span>
                                </div>
                                {depth.bids.map((b, i) => {
                                    const maxQty = Math.max(...depth.bids.map((x) => x.quantity), 1);
                                    const barW = (b.quantity / maxQty) * 100;
                                    return (
                                        <div key={i} className="relative mb-0.5 rounded px-2 py-1 text-xs">
                                            <div
                                                className="absolute inset-0 rounded bg-green-500/10"
                                                style={{ width: `${barW}%` }}
                                            />
                                            <div className="relative flex justify-between">
                                                <span className="text-gray-300">{b.quantity.toLocaleString()}</span>
                                                <span className="font-medium text-green-400">₹{b.price.toFixed(2)}</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Asks */}
                            <div>
                                <div className="mb-1 flex justify-between text-[10px] font-medium text-gray-500 px-1">
                                    <span>Ask Price</span>
                                    <span>Sell Qty</span>
                                </div>
                                {depth.asks.map((a, i) => {
                                    const maxQty = Math.max(...depth.asks.map((x) => x.quantity), 1);
                                    const barW = (a.quantity / maxQty) * 100;
                                    return (
                                        <div key={i} className="relative mb-0.5 rounded px-2 py-1 text-xs">
                                            <div
                                                className="absolute inset-0 right-0 rounded bg-red-500/10"
                                                style={{ width: `${barW}%`, marginLeft: "auto" }}
                                            />
                                            <div className="relative flex justify-between">
                                                <span className="font-medium text-red-400">₹{a.price.toFixed(2)}</span>
                                                <span className="text-gray-300">{a.quantity.toLocaleString()}</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Totals */}
                        <div className="mt-3 flex justify-between border-t border-gray-800 pt-2 text-[10px]">
                            <span className="text-green-400">
                                Buy Qty: {depth.totalBuyQty?.toLocaleString()}
                            </span>
                            <span className="text-red-400">
                                Sell Qty: {depth.totalSellQty?.toLocaleString()}
                            </span>
                        </div>
                    </>
                ) : (
                    <div className="py-8 text-center text-sm text-gray-500">
                        Angel One not connected — depth requires real-time API
                    </div>
                )}
            </div>
        </div>
    );
}
