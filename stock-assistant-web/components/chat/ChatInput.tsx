"use client";
import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";

interface Props {
    onSend: (message: string) => void;
    isLoading: boolean;
}

export default function ChatInput({ onSend, isLoading }: Props) {
    const [input, setInput] = useState("");
    const inputRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        inputRef.current?.focus();
    }, [isLoading]);

    const handleSend = () => {
        if (input.trim() && !isLoading) {
            onSend(input.trim());
            setInput("");
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="border-t border-gray-800 bg-[#0d1117] px-4 py-3">
            <div className="flex items-end gap-2 rounded-xl border border-gray-700 bg-[#1a1f2e] px-3 py-2 focus-within:border-blue-500/50 transition-colors">
                <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={
                        isLoading
                            ? "Analyzing..."
                            : "Ask about any stock, market, or sector..."
                    }
                    disabled={isLoading}
                    rows={1}
                    className="flex-1 resize-none bg-transparent text-sm text-gray-100 placeholder-gray-500 outline-none disabled:opacity-50"
                    style={{ minHeight: "24px", maxHeight: "120px" }}
                    onInput={(e) => {
                        const target = e.target as HTMLTextAreaElement;
                        target.style.height = "24px";
                        target.style.height = target.scrollHeight + "px";
                    }}
                />
                <button
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition-all hover:bg-blue-500 disabled:opacity-30 disabled:hover:bg-blue-600"
                >
                    <Send className="h-4 w-4" />
                </button>
            </div>
            <p className="mt-1.5 text-center text-[10px] text-gray-600">
                Data from Yahoo Finance (15 min delay) & NSE India • Powered by Groq AI
            </p>
        </div>
    );
}
