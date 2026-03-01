"use client";
import type { MarketIndex } from "@/types";

interface Props {
    indices: MarketIndex[];
}

export default function SectorPerformance({ indices }: Props) {
    const sectors = indices.filter((i) =>
        [
            "NIFTY IT",
            "NIFTY BANK",
            "NIFTY PHARMA",
            "NIFTY FMCG",
            "NIFTY AUTO",
            "NIFTY METAL",
            "NIFTY ENERGY",
        ].includes(i.name)
    );

    if (sectors.length === 0) return null;

    return (
        <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                Sectors
            </h3>
            <div className="space-y-1">
                {sectors.map((s) => {
                    const isUp = (s.pChange ?? 0) >= 0;
                    const label = s.name.replace("NIFTY ", "");
                    // Width proportional to absolute change (max ~3%)
                    const barW = Math.min(Math.abs(s.pChange ?? 0) * 30, 100);
                    return (
                        <div
                            key={s.name}
                            className="flex items-center gap-2 rounded-lg px-3 py-1.5 hover:bg-white/5 transition-all"
                        >
                            <span className="w-14 text-xs text-gray-400 shrink-0">
                                {label}
                            </span>
                            <div className="flex-1 h-1.5 rounded-full bg-gray-800 overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all duration-700 ${isUp ? "bg-green-500" : "bg-red-500"
                                        }`}
                                    style={{ width: `${barW}%` }}
                                />
                            </div>
                            <span
                                className={`w-14 text-xs font-semibold text-right ${isUp ? "text-green-400" : "text-red-400"
                                    }`}
                            >
                                {isUp ? "+" : ""}
                                {s.pChange?.toFixed(2)}%
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
