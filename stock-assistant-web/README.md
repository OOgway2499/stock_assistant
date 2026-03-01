# 🇮🇳 Indian Stock Market AI Assistant — Web App

A full-stack AI-powered stock market assistant built with **Next.js 14**, **Tailwind CSS**, and **Groq LLM**.

> Ask questions in plain English. Get live prices, technical analysis, fundamentals, and market news — all in a beautiful dark trading terminal UI.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **AI Chat** | Natural language stock queries powered by Groq (Llama 3) |
| **Live Dashboard** | Nifty 50, Bank Nifty, Nifty IT with auto-refresh |
| **Top Gainers/Losers** | Click any stock to analyze it instantly |
| **Sector Performance** | Visual bars for IT, Bank, Pharma, Auto, FMCG, Metal, Energy |
| **Technical Analysis** | RSI, MACD, SMA, EMA, Bollinger Bands with signals |
| **Fundamental Analysis** | PE, EPS, market cap, debt, ROE with valuation signals |
| **News** | Real-time Google News RSS for any stock or topic |
| **Watchlist** | Add/remove stocks, persisted in localStorage |
| **Mobile Responsive** | Tab-based navigation on phones |
| **Tool Calling** | Groq uses tools to fetch real data before answering |

---

## 🚀 Quick Setup

### Step 1: Install Dependencies
```bash
cd stock-assistant-web
npm install
```

### Step 2: Add Your Groq API Key
Get a free key from [console.groq.com](https://console.groq.com) (14,400 requests/day free).

Edit `.env.local`:
```
GROQ_API_KEY=gsk_your_key_here
```

### Step 3: Run Locally
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000)

---

## 🌐 Deploy to Vercel (Free)

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com) → Import repo
3. Add environment variable: `GROQ_API_KEY`
4. Click Deploy → **Done!**

Your app will be live at `https://your-project.vercel.app`

---

## 💬 Example Questions

```
How is Reliance doing today?
Show me RSI and MACD for TCS
Compare TCS, Infosys and Wipro
What are today's top gainers on NSE?
Latest news on HDFC Bank
How is the IT sector performing?
Give me full analysis of Zomato
What is ICICI Bank's PE ratio?
```

---

## 📊 Data Sources

| Source | Cost | API Key | Delay |
|--------|------|---------|-------|
| Yahoo Finance (via yahoo-finance2) | Free | None | ~15 min |
| NSE India API | Free | None | Near real-time |
| Google News RSS | Free | None | Real-time |
| Groq LLM (Llama 3) | Free tier | From console.groq.com | — |

---

## 🔒 Security

- `GROQ_API_KEY` is **server-side only** (never exposed to browser)
- All LLM calls happen in `/api/chat` route
- No env vars prefixed with `NEXT_PUBLIC_`

---

## ⚠️ Disclaimer

This is for **educational purposes only**. Not financial advice.
Always consult a **SEBI-registered advisor** before investing.
