"""
Grok LLM Agent — The brain of the stock assistant.
Uses OpenAI-compatible SDK with tool calling to connect
Grok LLM to all stock market data sources.
"""

import json
from openai import OpenAI
from config import GROK_API_KEY, GROK_BASE_URL, GROK_MODEL

# Import all tools
from tools.stock_price import get_stock_price, compare_stocks
from tools.technicals import get_technicals
from tools.fundamentals import get_fundamentals_tool
from tools.news import get_news
from tools.indices import get_market_overview, get_nifty_sectors


# ── Initialize Grok Client ──────────────────────────────────────
client = OpenAI(
    api_key=GROK_API_KEY,
    base_url=GROK_BASE_URL,
)

# ── System Prompt ────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert Indian stock market assistant with deep knowledge of NSE, BSE,
Nifty 50, Sensex, F&O markets, and Indian economy.

You have real-time tools available. ALWAYS use tools before answering —
never guess or assume prices, news, or market data.

Your rules:
1. Always call tools to get fresh data before every answer
2. Explain in very simple language — user is new to stock markets
3. When asked about a stock → get both price AND technicals AND news
4. Give practical interpretation of technical signals in plain English
5. Format numbers clearly: prices in ₹, percentages with %
6. Always end every response with:
   ⚠️ Disclaimer: This is for educational purposes only.
   Not financial advice. Consult a SEBI-registered advisor before investing.
7. If asked about prediction → explain you give signals not predictions
8. If market is closed → mention data is from last trading session
9. Be friendly, patient, and encouraging to beginners
"""

# ── Tool Definitions for Grok ────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get current price, open, high, low, volume for any NSE/BSE stock",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "NSE stock symbol, e.g. RELIANCE, TCS, INFY, HDFCBANK",
                    }
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_stocks",
            "description": "Compare prices of multiple stocks at once",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "string",
                        "description": "Comma-separated stock symbols, e.g. TCS,INFY,WIPRO",
                    }
                },
                "required": ["symbols"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_technicals",
            "description": "Get technical analysis indicators — RSI, MACD, moving averages, Bollinger Bands, trend signals",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "NSE stock symbol",
                    },
                    "period": {
                        "type": "string",
                        "description": "Lookback period: 1mo, 3mo, 6mo, 1y. Default 3mo",
                        "default": "3mo",
                    },
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fundamentals_tool",
            "description": "Get company fundamentals — PE ratio, EPS, market cap, debt-to-equity, ROE, margins, sector info",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "NSE stock symbol",
                    }
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Get latest news articles about any stock or market topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query, e.g. 'Infosys results', 'Nifty today', 'IT sector'",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_market_overview",
            "description": "Get full market overview — Nifty 50, Bank Nifty, Nifty IT, top gainers, top losers, market status",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_nifty_sectors",
            "description": "Get performance of all NSE sector indices — IT, Bank, Pharma, Auto, FMCG, Metal, Realty, Energy",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# ── Tool Name → Function Mapping ────────────────────────────────
TOOL_MAP = {
    "get_stock_price": get_stock_price,
    "compare_stocks": compare_stocks,
    "get_technicals": get_technicals,
    "get_fundamentals_tool": get_fundamentals_tool,
    "get_news": get_news,
    "get_market_overview": get_market_overview,
    "get_nifty_sectors": get_nifty_sectors,
}


def execute_tool(name: str, arguments: str) -> str:
    """
    Execute a tool by name with the given arguments.

    Args:
        name:      tool function name
        arguments: JSON string of arguments

    Returns:
        string representation of the tool result
    """
    try:
        args = json.loads(arguments) if isinstance(arguments, str) else arguments

        if name not in TOOL_MAP:
            return json.dumps({"error": f"Unknown tool: {name}"})

        func = TOOL_MAP[name]
        result = func(**args)
        return json.dumps(result, default=str, ensure_ascii=False)

    except Exception as e:
        print(f"⚠️ [execute_tool] Error executing {name}: {e}")
        return json.dumps({"error": f"Tool execution failed: {str(e)}"})


def ask_assistant(user_query: str, conversation_history: list = None) -> str:
    """
    Send a user query to Grok with tool calling and return the final response.

    Args:
        user_query:           the user's question in plain English
        conversation_history: list of previous messages for context

    Returns:
        string response from the assistant
    """
    try:
        if conversation_history is None:
            conversation_history = []

        # Build message list
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_query})

        # Agentic loop — keep calling until no more tool calls
        max_iterations = 10  # Safety limit
        for _ in range(max_iterations):
            response = client.chat.completions.create(
                model=GROK_MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )

            choice = response.choices[0]

            # If the model wants to call tools
            if choice.finish_reason == "tool_calls" or (
                choice.message.tool_calls and len(choice.message.tool_calls) > 0
            ):
                # Append the assistant's message (with tool calls)
                messages.append(choice.message)

                # Execute each tool call
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments

                    print(f"   🔧 Calling tool: {tool_name}")
                    result = execute_tool(tool_name, tool_args)

                    # Append tool result
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

                # Continue the loop — let Grok process tool results
                continue
            else:
                # No more tool calls — return the final text
                return choice.message.content or "I couldn't generate a response. Please try again."

        return "I reached the maximum number of tool calls. Please simplify your question."

    except Exception as e:
        print(f"⚠️ [ask_assistant] Error: {e}")
        return f"Sorry, I encountered an error: {str(e)}\nPlease check your GROK_API_KEY and try again."
