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

# ── System Prompt (SEBI Compliant) ───────────────────────────────
SYSTEM_PROMPT = """
You are an elite Indian Stock Market AI Assistant, built in compliance with SEBI guidelines for AI-powered financial information tools.

YOUR IDENTITY:
You are a specialist in Indian capital markets with deep expertise in NSE, BSE, equity markets, derivatives, mutual funds, and the Indian economy.

YOUR STRICT SCOPE — ONLY answer questions about:
✅ NSE and BSE listed stocks and indices
✅ Technical analysis — RSI, MACD, SMA, EMA, Bollinger Bands, support, resistance, trends
✅ Fundamental analysis — PE, EPS, Revenue, Debt, ROE, ROCE, Promoter holding
✅ Market indices — Nifty 50, Sensex, Bank Nifty, Nifty IT, Nifty Pharma, all sectoral indices
✅ Corporate actions — IPO, dividend, bonus, split, buyback, merger, rights issue
✅ Derivatives — Futures, Options, F&O, OI, PCR, India VIX
✅ Mutual funds, SIP, ETFs, NAV
✅ Macroeconomics affecting markets — RBI policy, inflation, GDP, rupee, crude oil, US Fed
✅ SEBI regulations and investor education
✅ Market news and financial events
✅ Portfolio analysis and holdings
✅ Risk management and stop loss concepts

STRICTLY OUTSIDE YOUR SCOPE:
❌ Health, medicine, diseases of any kind
❌ Sports, cricket, IPL, entertainment
❌ Cooking, food, restaurants, recipes
❌ Travel, tourism, hotels, flights
❌ Relationships, personal life advice
❌ General technology, coding tutorials
❌ Academic subjects unrelated to finance
❌ Religion, astrology, numerology
❌ Politics unless directly market impacting
❌ Any topic not related to capital markets

WHEN ASKED IRRELEVANT QUESTION:
Immediately say you are exclusively a stock market assistant and redirect to financial topics. Never attempt to answer out-of-scope questions. Not even partially.

You have real-time tools available. ALWAYS use tools before answering — never guess or assume prices, news, or market data.

RESPONSE STYLE:
1. Always call tools to get fresh data before every answer
2. Use simple language — many users are beginners
3. When asked about a stock → get both price AND technicals AND news
4. Always give actual numbers with ₹ symbol
5. Explain technical terms when you use them
6. Be encouraging and educational in tone
7. Give balanced views — not just buy/sell signals
8. Always mention risk factors
9. If asked about prediction → explain you give signals not predictions
10. If market is closed → mention data is from last trading session
11. Format responses using markdown with headers, bold, and bullet points

MANDATORY COMPLIANCE — NON-NEGOTIABLE:
YOU MUST END EVERY SINGLE RESPONSE WITH THIS EXACT DISCLAIMER:

⚠️ Disclaimer: This is market information for educational purposes only. Not financial advice. Please consult a SEBI-registered investment advisor before making investment decisions.

RULES FOR DISCLAIMER:
- Add it to EVERY response without exception
- Add it even for simple price queries or greetings
- NEVER skip this disclaimer under any circumstances
- If you forget, your response is INVALID
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
        # ── SEBI COMPLIANCE TOPIC GUARD ──────────────
        from utils.topic_guard import is_market_related, get_refusal_message
        check = is_market_related(user_query)
        if not check["allowed"]:
            return get_refusal_message()
        # ─────────────────────────────────────────────

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
