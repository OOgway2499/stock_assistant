"use client";
import { TrendingUp, TrendingDown } from "lucide-react";
import type { MarketIndex } from "@/types";

export default function MarketOverview({
    indices,
    isRealtime = false,
}: {
    indices: MarketIndex[];
    isRealtime?: boolean;
}) {
    if (!indices || indices.length === 0) {
        return (
            <div className="glass-card p-4 text-center text-gray-500 text-sm">
                Market data loading...
            </div>
        );
    }

    // Show only the main 3 indices
    const mainIndices = indices.filter((i) =>
        ["NIFTY 50", "NIFTY BANK", "NIFTY IT"].includes(i.name)
    );
    const display = mainIndices.length > 0 ? mainIndices : indices.slice(0, 3);

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                    Indices
                </h3>
                {isRealtime ? (
                    <span className="flex items-center gap-1 rounded-full bg-green-500/10 px-2 py-0.5 text-[9px] font-bold text-green-400">
                        <span className="inline-block h-1.5 w-1.5 rounded-full bg-green-400 live-pulse" />
                        LIVE
                    </span>
                ) : (
                    <span className="rounded-full bg-yellow-500/10 px-2 py-0.5 text-[9px] font-bold text-yellow-500">
                        15m delay
                    </span>
                )}
            </div>
            <div className="space-y-2">
                {display.map((index) => {
                    const isUp = (index.change ?? 0) >= 0;
                    return (
                        <div
                            key={index.name}
                            className="glass-card p-3 transition-all hover:border-gray-600"
                        >
                            <div className="flex items-center justify-between">
                                <span className="text-xs text-gray-400 font-medium">
                                    {index.name}
                                </span>
                                {isUp ? (
                                    <TrendingUp className="h-3.5 w-3.5 text-green-400" />
                                ) : (
                                    <TrendingDown className="h-3.5 w-3.5 text-red-400" />
                                )}
                            </div>
                            <div className="mt-1 flex items-baseline gap-2">
                                <span className="text-lg font-bold">
                                    {index.lastPrice?.toLocaleString("en-IN")}
                                </span>
                                <span
                                    className={`text-xs font-semibold ${isUp ? "text-green-400" : "text-red-400"
                                        }`}
                                >
                                    {isUp ? "▲" : "▼"}{" "}
                                    {Math.abs(index.change ?? 0).toFixed(2)} (
                                    {Math.abs(index.pChange ?? 0).toFixed(2)}%)
                                </span>
                            </div>
                            <div className="mt-1 flex gap-3 text-[10px] text-gray-500">
                                <span>H: {index.high?.toLocaleString("en-IN")}</span>
                                <span>L: {index.low?.toLocaleString("en-IN")}</span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
