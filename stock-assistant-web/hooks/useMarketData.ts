"use client";
import { useState, useEffect, useCallback } from "react";
import type { MarketOverview } from "@/types";

export function useMarketData() {
    const [marketData, setMarketData] = useState<MarketOverview | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [isRealtime, setIsRealtime] = useState(false);

    const fetchData = useCallback(async () => {
        try {
            setIsLoading(true);
            const res = await fetch("/api/market", {
                signal: AbortSignal.timeout(15000),
            });
            const data = await res.json();

            if (data.error) {
                setError(data.error);
            } else {
                setMarketData(data);
                setLastUpdated(new Date());
                setError(null);
            }

            // Check if Angel One is connected
            try {
                const statusRes = await fetch("/api/angel?type=status", {
                    signal: AbortSignal.timeout(5000),
                });
                const status = await statusRes.json();
                setIsRealtime(status.isConnected === true);
            } catch {
                setIsRealtime(false);
            }
        } catch (e: unknown) {
            const msg = e instanceof Error ? e.message : "Failed to fetch market data";
            setError(msg);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();

        // Auto-refresh: 10s if Angel One connected, 60s otherwise
        const interval = setInterval(() => {
            const now = new Date();
            const istHour = (now.getUTCHours() + 5) % 24;
            const isWeekday = now.getDay() >= 1 && now.getDay() <= 5;
            if (isWeekday && istHour >= 9 && istHour < 16) {
                fetchData();
            }
        }, isRealtime ? 10000 : 60000);

        return () => clearInterval(interval);
    }, [fetchData, isRealtime]);

    return { marketData, isLoading, error, lastUpdated, isRealtime, refetch: fetchData };
}
