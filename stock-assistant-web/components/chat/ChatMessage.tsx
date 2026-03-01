"use client";
import { format } from "date-fns";
import type { Message } from "@/types";

export default function ChatMessage({ message }: { message: Message }) {
    const isUser = message.role === "user";

    return (
        <div className={`flex gap-3 px-4 py-3 ${isUser ? "flex-row-reverse" : ""}`}>
            {/* Avatar */}
            <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm ${isUser
                        ? "bg-blue-500/20"
                        : "bg-purple-500/20"
                    }`}
            >
                {isUser ? "🧑" : "🤖"}
            </div>

            {/* Bubble */}
            <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${isUser
                        ? "bg-blue-600 text-white rounded-tr-sm"
                        : "bg-[#1a1f2e] border border-gray-800 rounded-tl-sm"
                    }`}
            >
                {/* Content */}
                <div className={`chat-markdown text-sm leading-relaxed ${isUser ? "" : "text-gray-200"}`}>
                    {isUser ? (
                        <p>{message.content}</p>
                    ) : (
                        <div
                            dangerouslySetInnerHTML={{
                                __html: formatMarkdown(message.content),
                            }}
                        />
                    )}
                </div>

                {/* Tools used */}
                {message.toolsUsed && message.toolsUsed.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                        {message.toolsUsed.map((tool, i) => (
                            <span
                                key={i}
                                className="rounded-full bg-purple-500/15 px-2 py-0.5 text-[10px] text-purple-300"
                            >
                                🔧 {tool.replace(/_/g, " ")}
                            </span>
                        ))}
                    </div>
                )}

                {/* Timestamp */}
                <div
                    className={`mt-1 text-[10px] ${isUser ? "text-blue-200" : "text-gray-500"
                        }`}
                >
                    {format(new Date(message.timestamp), "h:mm a")}
                </div>
            </div>
        </div>
    );
}

/**
 * Simple markdown → HTML for assistant messages.
 */
function formatMarkdown(text: string): string {
    return text
        // Headers
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        // Bold
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        // Italic
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        // Inline code
        .replace(/`(.+?)`/g, "<code>$1</code>")
        // Unordered list items
        .replace(/^[-•] (.+)$/gm, "<li>$1</li>")
        // Ordered list items
        .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
        // Line breaks
        .replace(/\n\n/g, "</p><p>")
        .replace(/\n/g, "<br/>")
        // Wrap
        .replace(/^/, "<p>")
        .replace(/$/, "</p>");
}
