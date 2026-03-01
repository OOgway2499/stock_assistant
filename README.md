# 🇮🇳 Indian Stock Market AI Assistant

An intelligent terminal-based chatbot for Indian stock market analysis.
Powered by **Grok LLM** + **yfinance** + **NSE India API**.

> Ask questions in plain English and get smart, data-driven answers about
> NSE/BSE stocks, Nifty indices, technical indicators, and market news.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Stock Prices** | Current price, open, high, low, volume for any NSE/BSE stock |
| **Technical Analysis** | RSI, MACD, SMA, EMA, Bollinger Bands, ATR with human-readable signals |
| **Fundamental Analysis** | PE ratio, EPS, market cap, debt-to-equity, ROE with valuation signals |
| **Market Overview** | Nifty 50, Bank Nifty, top gainers, top losers, market status |
| **Sector Performance** | IT, Bank, Pharma, FMCG, Auto, Metal, Realty, Energy indices |
| **Stock Comparison** | Compare multiple stocks side by side |
| **News** | Latest stock & market news from Google News |
| **Watchlist** | Save stocks to a local watchlist |
| **Query History** | SQLite-backed history of all your queries |
| **Conversational AI** | Natural language understanding via Grok LLM with tool calling |

---

## 🚀 Quick Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get Your Free Grok API Key

1. Go to [console.x.ai](https://console.x.ai)
2. Sign up (free — **$25 free credits** on signup)
3. Create an API key

### Step 3: Add Your Key

Open the `.env` file and replace the placeholder:

```
GROK_API_KEY=xai-your-actual-key-here
```

### Step 4: Run the Assistant

```bash
python main.py
```

---

## 💬 Example Questions

```
📌 You: How is Reliance doing today?
📌 You: Show me RSI and MACD for TCS
📌 You: What are today's top gainers on NSE?
📌 You: Compare TCS, Infosys and Wipro
📌 You: Latest news on HDFC Bank
📌 You: How is Nifty 50 today?
📌 You: Give me full analysis of Zomato
📌 You: How is the IT sector performing?
📌 You: What is the PE ratio of ICICI Bank?
```

### Special Commands

| Command | Action |
|---------|--------|
| `history` | Show last 10 queries |
| `watchlist` | Show your saved stocks |
| `clear` | Reset conversation context |
| `exit` | Quit the assistant |

---

## 📊 Data Sources

| Source | Cost | API Key | Delay |
|--------|------|---------|-------|
| **yfinance** | Free | ❌ None needed | ~15 min |
| **NSE India API** | Free | ❌ None needed | Near real-time |
| **Google News RSS** | Free | ❌ None needed | Real-time |
| **Grok LLM** | Free tier | ✅ From console.x.ai | — |

---

## 📁 Project Structure

```
stock-assistant/
├── main.py                  # Terminal chatbot entry point
├── config.py                # Grok credentials loader
├── .env                     # GROK_API_KEY (only secret needed)
├── .gitignore               # Keeps .env safe
├── requirements.txt         # Python dependencies
│
├── data_sources/
│   ├── yfinance_data.py     # Stock prices, history, fundamentals
│   └── nse_data.py          # Nifty, gainers, losers, option chain
│
├── tools/
│   ├── stock_price.py       # Tool: get current stock price
│   ├── technicals.py        # Tool: RSI, MACD, SMA indicators
│   ├── fundamentals.py      # Tool: PE, EPS, market cap
│   ├── news.py              # Tool: latest stock news
│   └── indices.py           # Tool: Nifty, Sensex, gainers, losers
│
├── llm/
│   └── grok_agent.py        # Grok LLM brain with tool calling
│
├── database/
│   └── db.py                # SQLite for query history & watchlist
│
└── README.md
```

---

## 🔮 Future Upgrades

- **Angel One SmartAPI** — Plug in for true real-time data with 0 delay
  (once your Angel One account is activated)
- **Web UI** — FastAPI + React dashboard
- **Portfolio Tracking** — Track your holdings and P&L
- **Alerts** — Price/indicator alerts via Telegram

---

## ⚠️ Disclaimer

This project is for **educational purposes only**.
It does **not** constitute financial advice.
Always consult a **SEBI-registered investment advisor** before making
any investment decisions. Past performance does not guarantee future results.

---

## 📜 License

MIT License — use freely, modify as you wish.
