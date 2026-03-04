"use client";
import { useState, useEffect } from "react";
import { ChevronDown, ChevronUp, Wifi, WifiOff } from "lucide-react";

interface ApiStatus {
    configured: boolean;
    isConnected: boolean;
    apis: {
        trading: boolean;
        publisher: boolean;
        historical: boolean;
        feeds: boolean;
    };
}

export default function AngelOneStatus() {
    const [status, setStatus] = useState<ApiStatus | null>(null);
    const [expanded, setExpanded] = useState(false);

    useEffect(() => {
        const check = async () => {
            try {
                const res = await fetch("/api/angel?type=status", {
                    signal: AbortSignal.timeout(8000),
                });
                setStatus(await res.json());
            } catch {
                setStatus(null);
            }
        };
        check();
        const interval = setInterval(check, 60000);
        return () => clearInterval(interval);
    }, []);

    if (!status) return null;

    const apis = [
        { key: "trading", label: "Trading" },
        { key: "publisher", label: "Publisher" },
        { key: "historical", label: "Historical" },
        { key: "feeds", label: "Feeds" },
    ];

    return (
        <div className="glass-card p-3">
            {/* Header — always visible */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="flex w-full items-center justify-between"
            >
                <div className="flex items-center gap-2">
                    {status.isConnected ? (
                        <Wifi className="h-3.5 w-3.5 text-green-400" />
                    ) : (
                        <WifiOff className="h-3.5 w-3.5 text-red-400" />
                    )}
                    <span className="text-xs font-medium text-gray-300">
                        Angel One
                    </span>
                    <span
                        className={`inline-block h-2 w-2 rounded-full ${status.isConnected ? "bg-green-400 live-pulse" : "bg-red-400"
                            }`}
                    />
                </div>
                {expanded ? (
                    <ChevronUp className="h-3.5 w-3.5 text-gray-500" />
                ) : (
                    <ChevronDown className="h-3.5 w-3.5 text-gray-500" />
                )}
            </button>

            {/* Expanded — show all 4 APIs */}
            {expanded && (
                <div className="mt-2 space-y-1 border-t border-gray-800 pt-2">
                    {apis.map(({ key, label }) => {
                        const active = status.apis[key as keyof typeof status.apis];
                        return (
                            <div key={key} className="flex items-center gap-2 text-[11px]">
                                <span
                                    className={`inline-block h-1.5 w-1.5 rounded-full ${active ? "bg-green-400" : "bg-red-400"
                                        }`}
                                />
                                <span className="text-gray-400">{label} API</span>
                                <span className={`ml-auto ${active ? "text-green-400" : "text-red-400"}`}>
                                    {active ? "Configured" : "Missing"}
                                </span>
                            </div>
                        );
                    })}
                    {!status.configured && (
                        <p className="mt-1 text-[10px] text-gray-600">
                            Add credentials to .env.local to connect
                        </p>
                    )}
                </div>
            )}
        </div>
    );
}
