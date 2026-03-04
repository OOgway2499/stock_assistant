/**
 * POST /api/chat — Groq LLM with tool calling.
 * The brain of the assistant. Accepts messages, calls tools, returns final answer.
 */
import { NextRequest, NextResponse } from "next/server";
import { groq, GROQ_MODEL, SYSTEM_PROMPT } from "@/lib/groq";
import { TOOLS } from "@/lib/tools";
import { getStockPrice, getTechnicals, getFundamentals } from "@/lib/stockData";
import { getMarketOverview } from "@/lib/nseData";
import { getNews } from "@/lib/newsData";
import { getAngelPortfolio } from "@/lib/angelOne";
import type Groq from "groq-sdk";

type ChatMessage = Groq.Chat.Completions.ChatCompletionMessageParam;

/**
 * Execute a tool call by name.
 */
async function executeTool(
    name: string,
    args: Record<string, string>
): Promise<string> {
    try {
        let result: unknown;

        switch (name) {
            case "get_stock_price":
                result = await getStockPrice(args.symbol);
                break;
            case "compare_stocks": {
                const symbols = args.symbols.split(",").map((s) => s.trim());
                const prices = await Promise.all(symbols.map(getStockPrice));
                result = prices;
                break;
            }
            case "get_technicals":
                result = await getTechnicals(args.symbol, args.period || "6mo");
                break;
            case "get_fundamentals":
                result = await getFundamentals(args.symbol);
                break;
            case "get_news":
                result = await getNews(args.query);
                break;
            case "get_market_overview":
                result = await getMarketOverview();
                break;
            case "get_portfolio":
                result = await getAngelPortfolio() || { error: "Portfolio not available — Angel One not configured" };
                break;
            default:
                result = { error: `Unknown tool: ${name}` };
        }

        return JSON.stringify(result);
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        return JSON.stringify({ error: `Tool execution failed: ${msg}` });
    }
}

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { messages: clientMessages, userQuery } = body;

        if (!userQuery) {
            return NextResponse.json(
                { error: "userQuery is required" },
                { status: 400 }
            );
        }

        // Build message list
        const messages: ChatMessage[] = [
            { role: "system", content: SYSTEM_PROMPT },
        ];

        // Add conversation history (last 10 messages)
        if (Array.isArray(clientMessages)) {
            const recent = clientMessages.slice(-10);
            for (const m of recent) {
                if (m.role === "user" || m.role === "assistant") {
                    messages.push({ role: m.role, content: m.content });
                }
            }
        }

        // Add current user message
        messages.push({ role: "user", content: userQuery });

        const toolsUsed: string[] = [];
        const MAX_ITERATIONS = 8;

        // Agentic tool-calling loop
        for (let i = 0; i < MAX_ITERATIONS; i++) {
            let response;
            try {
                response = await groq.chat.completions.create({
                    model: GROQ_MODEL,
                    messages,
                    tools: TOOLS,
                    tool_choice: "auto",
                    temperature: 0.3,
                    max_tokens: 4096,
                });
            } catch (toolError: unknown) {
                // Handle Groq's "tool_use_failed" error —
                // the model generated a malformed tool call.
                // Retry WITHOUT tools so it gives a plain text answer.
                const errMsg = toolError instanceof Error ? toolError.message : String(toolError);
                console.warn("[/api/chat] Tool call failed, retrying without tools:", errMsg);

                try {
                    const fallback = await groq.chat.completions.create({
                        model: GROQ_MODEL,
                        messages,
                        temperature: 0.3,
                        max_tokens: 4096,
                        // No tools — force text-only response
                    });
                    return NextResponse.json({
                        response:
                            fallback.choices[0]?.message?.content ||
                            "I had trouble processing that. Could you rephrase your question?",
                        toolsUsed: [...new Set(toolsUsed)],
                    });
                } catch (fallbackError: unknown) {
                    const fbMsg = fallbackError instanceof Error ? fallbackError.message : String(fallbackError);
                    return NextResponse.json({
                        response: `I'm having trouble connecting to the AI service. Please try again in a moment. (${fbMsg})`,
                        toolsUsed: [],
                    });
                }
            }

            const choice = response.choices[0];

            // Check if the model wants to call tools
            if (
                choice.finish_reason === "tool_calls" ||
                (choice.message.tool_calls && choice.message.tool_calls.length > 0)
            ) {
                // Add assistant message with tool calls
                messages.push(choice.message);

                // Execute each tool call in parallel
                const toolCalls = choice.message.tool_calls || [];
                const toolResults = await Promise.all(
                    toolCalls.map(async (tc) => {
                        let args: Record<string, string> = {};
                        try {
                            args = JSON.parse(tc.function.arguments || "{}");
                        } catch {
                            console.warn("[/api/chat] Bad tool args:", tc.function.arguments);
                            args = {};
                        }
                        toolsUsed.push(tc.function.name);
                        const result = await executeTool(tc.function.name, args);
                        return {
                            role: "tool" as const,
                            tool_call_id: tc.id,
                            content: result,
                        };
                    })
                );

                messages.push(...toolResults);
                continue;
            }

            // No more tool calls — return final response
            return NextResponse.json({
                response:
                    choice.message.content ||
                    "I couldn't generate a response. Please try again.",
                toolsUsed: [...new Set(toolsUsed)],
            });
        }

        return NextResponse.json({
            response:
                "I reached the maximum number of tool calls. Please simplify your question.",
            toolsUsed,
        });
    } catch (e: unknown) {
        console.error("[/api/chat] Error:", e);
        const msg = e instanceof Error ? e.message : String(e);
        return NextResponse.json(
            {
                response: `Sorry, I encountered an error. Please try again. (${msg})`,
                toolsUsed: [],
            },
            { status: 500 }
        );
    }
}
