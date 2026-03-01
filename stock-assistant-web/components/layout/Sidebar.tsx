"use client";
import { useState, useEffect } from "react";
import {
    BarChart3,
    TrendingUp,
    TrendingDown,
    Newspaper,
    Star,
    Plus,
    X,
} from "lucide-react";

const QUICK_ACTIONS = [
    { icon: BarChart3, label: "Market Overview", query: "How is the market doing today?" },
    { icon: TrendingUp, label: "Top Gainers", query: "What are today's top gainers on NSE?" },
    { icon: TrendingDown, label: "Top Losers", query: "What are today's top losers on NSE?" },
    { icon: Newspaper, label: "Market News", query: "Latest Indian stock market news" },
];

const POPULAR_STOCKS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "WIPRO",
    "ADANIENT",
    "TATAMOTORS",
];

interface Props {
    onQuery: (query: string) => void;
}

export default function Sidebar({ onQuery }: Props) {
    const [watchlist, setWatchlist] = useState<string[]>([]);
    const [newSymbol, setNewSymbol] = useState("");

    // Load watchlist from localStorage
    useEffect(() => {
        const saved = localStorage.getItem("stock-watchlist");
        if (saved) setWatchlist(JSON.parse(saved));
    }, []);

    // Save watchlist to localStorage
    useEffect(() => {
        localStorage.setItem("stock-watchlist", JSON.stringify(watchlist));
    }, [watchlist]);

    const addToWatchlist = () => {
        const sym = newSymbol.trim().toUpperCase();
        if (sym && !watchlist.includes(sym)) {
            setWatchlist((prev) => [...prev, sym]);
            setNewSymbol("");
        }
    };

    const removeFromWatchlist = (sym: string) => {
        setWatchlist((prev) => prev.filter((s) => s !== sym));
    };

    return (
        <aside className="flex h-full w-60 shrink-0 flex-col border-r border-gray-800 bg-[#0d1117]">
            {/* Quick Actions */}
            <div className="border-b border-gray-800 p-3">
                <h3 className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-500">
                    Quick Actions
                </h3>
                <div className="space-y-0.5">
                    {QUICK_ACTIONS.map((action) => (
                        <button
                            key={action.label}
                            onClick={() => onQuery(action.query)}
                            className="flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-xs text-gray-300 transition-all hover:bg-white/5 hover:text-white"
                        >
                            <action.icon className="h-3.5 w-3.5 text-gray-500" />
                            {action.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Watchlist */}
            <div className="border-b border-gray-800 p-3">
                <div className="mb-2 flex items-center gap-1">
                    <Star className="h-3 w-3 text-yellow-500" />
                    <h3 className="text-[10px] font-semibold uppercase tracking-wider text-gray-500">
                        Watchlist
                    </h3>
                </div>

                {/* Add input */}
                <div className="mb-2 flex gap-1">
                    <input
                        value={newSymbol}
                        onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
                        onKeyDown={(e) => e.key === "Enter" && addToWatchlist()}
                        placeholder="Add symbol..."
                        className="flex-1 rounded-md border border-gray-700 bg-[#1a1f2e] px-2 py-1 text-xs text-gray-200 placeholder-gray-600 outline-none focus:border-blue-500/50"
                    />
                    <button
                        onClick={addToWatchlist}
                        className="rounded-md border border-gray-700 p-1 text-gray-500 hover:bg-gray-800 hover:text-white transition"
                    >
                        <Plus className="h-3.5 w-3.5" />
                    </button>
                </div>

                {/* Watchlist items */}
                <div className="space-y-0.5 max-h-36 overflow-y-auto">
                    {watchlist.length === 0 ? (
                        <p className="text-[10px] text-gray-600 py-1">
                            No stocks added yet
                        </p>
                    ) : (
                        watchlist.map((sym) => (
                            <div
                                key={sym}
                                className="flex items-center justify-between rounded-lg px-2 py-1.5 hover:bg-white/5 group"
                            >
                                <button
                                    onClick={() => onQuery(`Analyse ${sym}`)}
                                    className="text-xs font-medium text-gray-300 hover:text-blue-400"
                                >
                                    {sym}
                                </button>
                                <button
                                    onClick={() => removeFromWatchlist(sym)}
                                    className="text-gray-600 opacity-0 group-hover:opacity-100 transition"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Popular Stocks */}
            <div className="flex-1 overflow-y-auto p-3">
                <h3 className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-500">
                    Popular Stocks
                </h3>
                <div className="flex flex-wrap gap-1">
                    {POPULAR_STOCKS.map((sym) => (
                        <button
                            key={sym}
                            onClick={() => onQuery(`Analyse ${sym}`)}
                            className="rounded-md border border-gray-800 px-2 py-1 text-[10px] text-gray-400 transition-all hover:border-blue-500/40 hover:text-blue-300 hover:bg-blue-500/5"
                        >
                            {sym}
                        </button>
                    ))}
                </div>
            </div>
        </aside>
    );
}
