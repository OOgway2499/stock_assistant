"use client";
import { useRef, useEffect } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import SuggestedQueries from "./SuggestedQueries";
import { TypingIndicator } from "@/components/ui/LoadingSpinner";
import { useChat } from "@/hooks/useChat";

interface Props {
    externalQuery?: string | null;
    onQueryConsumed?: () => void;
}

export default function ChatWindow({ externalQuery, onQueryConsumed }: Props) {
    const { messages, isLoading, sendMessage, clearChat } = useChat();
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll on new message
    useEffect(() => {
        scrollRef.current?.scrollTo({
            top: scrollRef.current.scrollHeight,
            behavior: "smooth",
        });
    }, [messages, isLoading]);

    // Handle external queries from sidebar/dashboard
    useEffect(() => {
        if (externalQuery) {
            sendMessage(externalQuery);
            onQueryConsumed?.();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [externalQuery]);

    const showSuggestions = messages.length <= 1;

    return (
        <div className="flex h-full flex-col">
            {/* Header bar */}
            <div className="flex items-center justify-between border-b border-gray-800 px-4 py-2.5">
                <div className="flex items-center gap-2">
                    <span className="text-lg">💬</span>
                    <h2 className="text-sm font-semibold">Chat with AI</h2>
                </div>
                <button
                    onClick={clearChat}
                    className="rounded-md px-2.5 py-1 text-xs text-gray-400 transition-all hover:bg-gray-800 hover:text-gray-200"
                >
                    Clear Chat
                </button>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto">
                <div className="py-4">
                    {messages.map((msg) => (
                        <ChatMessage key={msg.id} message={msg} />
                    ))}
                    {isLoading && <TypingIndicator />}
                </div>

                {/* Suggested queries */}
                <SuggestedQueries
                    onSelect={(q) => sendMessage(q)}
                    visible={showSuggestions && !isLoading}
                />
            </div>

            {/* Input */}
            <ChatInput onSend={sendMessage} isLoading={isLoading} />
        </div>
    );
}
