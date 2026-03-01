"use client";
import { useState, useEffect, useCallback } from "react";
import type { MarketOverview } from "@/types";

export function useMarketData() {
    const [marketData, setMarketData] = useState<MarketOverview | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

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
        } catch (e: unknown) {
            const msg = e instanceof Error ? e.message : "Failed to fetch market data";
            setError(msg);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();

        // Auto-refresh every 60 seconds during market hours (9AM-4PM IST)
        const interval = setInterval(() => {
            const now = new Date();
            const istHour = (now.getUTCHours() + 5) % 24; // Rough IST
            const isWeekday = now.getDay() >= 1 && now.getDay() <= 5;
            if (isWeekday && istHour >= 9 && istHour < 16) {
                fetchData();
            }
        }, 60000);

        return () => clearInterval(interval);
    }, [fetchData]);

    return { marketData, isLoading, error, lastUpdated, refetch: fetchData };
}
