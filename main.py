"""
Indian Stock Market AI Assistant — Terminal Chatbot Entry Point.
Uses Grok LLM + yfinance + NSE India API for intelligent stock analysis.
"""

import sys
from llm.grok_agent import ask_assistant
from database.db import StockDB


def print_banner():
    """Display the startup banner."""
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   🇮🇳  Indian Stock Market AI Assistant       ║")
    print("║   Powered by Grok + yfinance + NSE India     ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    print("💡 Example questions you can ask:")
    print("  • How is Reliance doing today?")
    print("  • Show me RSI and MACD for TCS")
    print("  • What are today's top gainers on NSE?")
    print("  • Compare TCS, Infosys and Wipro")
    print("  • Latest news on HDFC Bank")
    print("  • How is Nifty 50 today?")
    print("  • Give me full analysis of Zomato")
    print("  • How is the IT sector performing?")
    print()
    print("📌 Commands: 'history' | 'watchlist' | 'clear' | 'exit'")
    print("─" * 48)


def print_history(db: StockDB):
    """Print the last 10 queries from the database."""
    history = db.get_history(limit=10)
    if not history:
        print("\n📭 No query history yet. Ask me something!\n")
        return

    print("\n📜 Recent Query History:")
    print("─" * 40)
    for i, entry in enumerate(history, 1):
        query = entry["query"][:80]
        ts = entry["timestamp"][:16]
        print(f"  {i}. [{ts}] {query}")
    print("─" * 40)
    print()


def print_watchlist(db: StockDB):
    """Print all stocks in the watchlist."""
    watchlist = db.get_watchlist()
    if not watchlist:
        print("\n📭 Watchlist is empty. Add stocks with your questions!\n")
        return

    print("\n⭐ Your Watchlist:")
    print("─" * 40)
    for entry in watchlist:
        notes = f" — {entry['notes']}" if entry["notes"] else ""
        print(f"  • {entry['symbol']}{notes}  (added {entry['added_date'][:10]})")
    print("─" * 40)
    print()


def main():
    """Main chatbot loop."""
    # Initialize database
    db = StockDB()

    # Conversation history for context
    conversation_history = []

    # Print welcome banner
    print_banner()

    try:
        while True:
            # Get user input
            try:
                user_input = input("\n📌 You: ").strip()
            except EOFError:
                break

            # Skip empty input
            if not user_input:
                continue

            # ── Handle special commands ──────────────────────────
            lower = user_input.lower()

            if lower in ("exit", "quit", "bye"):
                print("\n👋 Goodbye! Happy investing! 📈")
                print("   Remember: Always do your own research.\n")
                break

            if lower == "history":
                print_history(db)
                continue

            if lower == "watchlist":
                print_watchlist(db)
                continue

            if lower == "clear":
                conversation_history = []
                print("\n✅ Conversation cleared! Starting fresh.\n")
                continue

            # ── Send to Grok ─────────────────────────────────────
            print("🤔 Thinking...", end="", flush=True)

            response = ask_assistant(user_input, conversation_history)
            print("\r" + " " * 20 + "\r", end="")  # Clear "Thinking..."

            print(f"\n🤖 Assistant:\n{response}\n")

            # Save to database
            db.save_query(user_input, response)

            # Update conversation history (keep last 10 messages)
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
            conversation_history = conversation_history[-10:]

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Happy investing! 📈")
        print("   Remember: Always do your own research.\n")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   The assistant will try to continue...\n")


if __name__ == "__main__":
    main()