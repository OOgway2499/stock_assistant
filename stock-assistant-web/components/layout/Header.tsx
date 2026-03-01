"use client";
import { Activity, RefreshCw } from "lucide-react";
import MarketStatus from "@/components/dashboard/MarketStatus";

interface Props {
    marketStatus: string;
    onRefresh: () => void;
}

export default function Header({ marketStatus, onRefresh }: Props) {
    return (
        <header className="flex items-center justify-between border-b border-gray-800 bg-[#0d1117] px-4 py-2.5 lg:px-6">
            {/* Logo */}
            <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                    <Activity className="h-4 w-4 text-white" />
                </div>
                <div>
                    <h1 className="text-sm font-bold leading-tight">
                        <span className="mr-1">🇮🇳</span>
                        Stock AI
                    </h1>
                    <p className="text-[10px] text-gray-500 leading-tight">
                        NSE • BSE • Powered by Groq
                    </p>
                </div>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-3">
                <MarketStatus status={marketStatus} />
                <button
                    onClick={onRefresh}
                    className="rounded-md p-1.5 text-gray-400 transition-all hover:bg-gray-800 hover:text-white"
                    title="Refresh market data"
                >
                    <RefreshCw className="h-4 w-4" />
                </button>
            </div>
        </header>
    );
}
