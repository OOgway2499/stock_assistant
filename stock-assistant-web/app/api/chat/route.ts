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
            const response = await groq.chat.completions.create({
                model: GROQ_MODEL,
                messages,
                tools: TOOLS,
                tool_choice: "auto",
                temperature: 0.7,
                max_tokens: 4096,
            });

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
                        const args = JSON.parse(tc.function.arguments || "{}");
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
                response: `Sorry, I encountered an error: ${msg}. Please try again.`,
                toolsUsed: [],
            },
            { status: 500 }
        );
    }
}
