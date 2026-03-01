"use client";
import { useState } from "react";
import type { GainerLoser } from "@/types";

interface Props {
    gainers: GainerLoser[];
    losers: GainerLoser[];
    onStockClick?: (symbol: string) => void;
}

export default function GainersLosers({ gainers, losers, onStockClick }: Props) {
    const [tab, setTab] = useState<"gainers" | "losers">("gainers");
    const items = tab === "gainers" ? gainers : losers;

    return (
        <div className="space-y-3">
            {/* Tab bar */}
            <div className="flex gap-1 rounded-lg bg-[#1a1f2e] p-1">
                <button
                    onClick={() => setTab("gainers")}
                    className={`flex-1 rounded-md px-3 py-1.5 text-xs font-medium transition-all ${tab === "gainers"
                            ? "bg-green-500/20 text-green-400"
                            : "text-gray-500 hover:text-gray-300"
                        }`}
                >
                    ▲ Top Gainers
                </button>
                <button
                    onClick={() => setTab("losers")}
                    className={`flex-1 rounded-md px-3 py-1.5 text-xs font-medium transition-all ${tab === "losers"
                            ? "bg-red-500/20 text-red-400"
                            : "text-gray-500 hover:text-gray-300"
                        }`}
                >
                    ▼ Top Losers
                </button>
            </div>

            {/* Table */}
            <div className="space-y-1">
                {items && items.length > 0 ? (
                    items.slice(0, 5).map((stock) => {
                        const isUp = (stock.pChange ?? 0) >= 0;
                        return (
                            <button
                                key={stock.symbol}
                                onClick={() => onStockClick?.(stock.symbol)}
                                className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-left transition-all hover:bg-white/5"
                            >
                                <div>
                                    <span className="text-sm font-medium">{stock.symbol}</span>
                                    <span className="ml-2 text-xs text-gray-500">
                                        ₹{stock.lastPrice?.toLocaleString("en-IN")}
                                    </span>
                                </div>
                                <span
                                    className={`text-xs font-semibold ${isUp ? "text-green-400" : "text-red-400"
                                        }`}
                                >
                                    {isUp ? "+" : ""}
                                    {stock.pChange?.toFixed(2)}%
                                </span>
                            </button>
                        );
                    })
                ) : (
                    <div className="py-4 text-center text-xs text-gray-500">
                        No data available
                    </div>
                )}
            </div>
        </div>
    );
}
