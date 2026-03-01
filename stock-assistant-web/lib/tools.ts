/**
 * Groq Tool Definitions — All tools the LLM can call.
 */
import type Groq from "groq-sdk";

type ToolDef = Groq.Chat.Completions.ChatCompletionTool;

export const TOOLS: ToolDef[] = [
    {
        type: "function",
        function: {
            name: "get_stock_price",
            description:
                "Get current price, open, high, low, volume for any NSE/BSE stock",
            parameters: {
                type: "object",
                properties: {
                    symbol: {
                        type: "string",
                        description: "NSE stock symbol, e.g. RELIANCE, TCS, INFY",
                    },
                },
                required: ["symbol"],
            },
        },
    },
    {
        type: "function",
        function: {
            name: "compare_stocks",
            description: "Compare prices of multiple stocks at once",
            parameters: {
                type: "object",
                properties: {
                    symbols: {
                        type: "string",
                        description: "Comma-separated stock symbols, e.g. TCS,INFY,WIPRO",
                    },
                },
                required: ["symbols"],
            },
        },
    },
    {
        type: "function",
        function: {
            name: "get_technicals",
            description:
                "Get technical analysis — RSI, MACD, moving averages, Bollinger Bands, trend signals",
            parameters: {
                type: "object",
                properties: {
                    symbol: { type: "string", description: "NSE stock symbol" },
                    period: {
                        type: "string",
                        description: "Lookback period: 1mo, 3mo, 6mo, 1y. Default 6mo",
                    },
                },
                required: ["symbol"],
            },
        },
    },
    {
        type: "function",
        function: {
            name: "get_fundamentals",
            description:
                "Get fundamentals — PE ratio, EPS, market cap, debt, ROE, margins",
            parameters: {
                type: "object",
                properties: {
                    symbol: { type: "string", description: "NSE stock symbol" },
                },
                required: ["symbol"],
            },
        },
    },
    {
        type: "function",
        function: {
            name: "get_news",
            description: "Get latest news about any stock or market topic",
            parameters: {
                type: "object",
                properties: {
                    query: {
                        type: "string",
                        description: "Search query, e.g. 'Infosys results', 'Nifty today'",
                    },
                },
                required: ["query"],
            },
        },
    },
    {
        type: "function",
        function: {
            name: "get_market_overview",
            description:
                "Get full market overview — Nifty 50, Bank Nifty, top gainers, top losers, market status",
            parameters: {
                type: "object",
                properties: {},
                required: [],
            },
        },
    },
];
