"use client";
import { useState, useCallback } from "react";
import type { StockPrice } from "@/types";

export function useStock() {
    const [stockData, setStockData] = useState<StockPrice | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchStock = useCallback(async (symbol: string) => {
        try {
            setIsLoading(true);
            setError(null);
            const res = await fetch(
                `/api/stock?symbol=${encodeURIComponent(symbol)}&type=price`,
                { signal: AbortSignal.timeout(10000) }
            );
            const data = await res.json();
            if (data.error) {
                setError(data.error);
            } else {
                setStockData(data);
            }
        } catch (e: unknown) {
            const msg = e instanceof Error ? e.message : "Failed to fetch stock data";
            setError(msg);
        } finally {
            setIsLoading(false);
        }
    }, []);

    return { stockData, isLoading, error, fetchStock };
}
