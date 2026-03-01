"use client";
import { useState, useCallback, useRef } from "react";
import type { Message } from "@/types";

const WELCOME_MESSAGE: Message = {
    id: "welcome",
    role: "assistant",
    content:
        "👋 **Namaste!** I'm your Indian Stock Market Assistant.\n\nI can help you with:\n- 📊 **Live stock prices** (Reliance, TCS, Infosys...)\n- 📈 **Technical analysis** (RSI, MACD, moving averages)\n- 💰 **Fundamentals** (PE ratio, market cap, debt)\n- 📰 **Market news** and sector performance\n- 🏆 **Top gainers & losers** on NSE\n\nWhat would you like to know today?",
    timestamp: new Date(),
};

export function useChat() {
    const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const abortRef = useRef<AbortController | null>(null);

    const sendMessage = useCallback(
        async (content: string) => {
            if (!content.trim() || isLoading) return;

            const userMsg: Message = {
                id: Date.now().toString(),
                role: "user",
                content: content.trim(),
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, userMsg]);
            setIsLoading(true);
            setError(null);

            try {
                abortRef.current = new AbortController();

                // Send only role + content for history
                const historyForApi = messages
                    .filter((m) => m.id !== "welcome")
                    .map((m) => ({ role: m.role, content: m.content }));

                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        messages: historyForApi,
                        userQuery: content.trim(),
                    }),
                    signal: abortRef.current.signal,
                });

                const data = await res.json();

                const assistantMsg: Message = {
                    id: (Date.now() + 1).toString(),
                    role: "assistant",
                    content:
                        data.response || "Sorry, I couldn't process that. Please try again.",
                    timestamp: new Date(),
                    toolsUsed: data.toolsUsed || [],
                };

                setMessages((prev) => [...prev, assistantMsg]);
            } catch (e: unknown) {
                if (e instanceof Error && e.name === "AbortError") return;
                const msg = e instanceof Error ? e.message : "An unexpected error occurred";
                setError(msg);
                setMessages((prev) => [
                    ...prev,
                    {
                        id: (Date.now() + 1).toString(),
                        role: "assistant",
                        content: `❌ Error: ${msg}. Please try again.`,
                        timestamp: new Date(),
                    },
                ]);
            } finally {
                setIsLoading(false);
            }
        },
        [isLoading, messages]
    );

    const clearChat = useCallback(() => {
        setMessages([WELCOME_MESSAGE]);
        setError(null);
    }, []);

    return { messages, isLoading, error, sendMessage, clearChat };
}
