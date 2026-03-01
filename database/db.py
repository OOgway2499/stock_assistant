"""
Database module — SQLite storage for query history and watchlist.
Uses Python's built-in sqlite3, no extra install needed.
"""

import sqlite3
from datetime import datetime


class StockDB:
    """Manages the stock assistant SQLite database."""

    def __init__(self, db_path: str = "stock_assistant.db"):
        """
        Initialize the database and create tables if they don't exist.

        Args:
            db_path: path to the SQLite database file
        """
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Create tables if they don't exist."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL UNIQUE,
                    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT DEFAULT ''
                )
            """)

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ [StockDB._create_tables] Error: {e}")

    # ── Query History ────────────────────────────────────────────

    def save_query(self, query: str, response: str):
        """
        Save a user query and assistant response to history.

        Args:
            query:    the user's question
            response: the assistant's answer
        """
        try:
            conn = self._get_connection()
            conn.execute(
                "INSERT INTO query_history (query, response, timestamp) VALUES (?, ?, ?)",
                (query, response, datetime.now().isoformat()),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ [StockDB.save_query] Error: {e}")

    def get_history(self, limit: int = 10) -> list:
        """
        Get the most recent queries.

        Args:
            limit: number of recent queries to return

        Returns:
            list of dicts with query, response, timestamp
        """
        try:
            conn = self._get_connection()
            rows = conn.execute(
                "SELECT query, response, timestamp FROM query_history "
                "ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"⚠️ [StockDB.get_history] Error: {e}")
            return []

    # ── Watchlist ────────────────────────────────────────────────

    def add_to_watchlist(self, symbol: str, notes: str = ""):
        """
        Add a stock to the watchlist.

        Args:
            symbol: NSE stock symbol
            notes:  optional notes about why you're watching
        """
        try:
            conn = self._get_connection()
            conn.execute(
                "INSERT OR REPLACE INTO watchlist (symbol, added_date, notes) VALUES (?, ?, ?)",
                (symbol.upper(), datetime.now().isoformat(), notes),
            )
            conn.commit()
            conn.close()
            return {"status": "success", "symbol": symbol.upper()}
        except Exception as e:
            print(f"⚠️ [StockDB.add_to_watchlist] Error: {e}")
            return {"error": str(e)}

    def get_watchlist(self) -> list:
        """
        Get all stocks in the watchlist.

        Returns:
            list of dicts with symbol, added_date, notes
        """
        try:
            conn = self._get_connection()
            rows = conn.execute(
                "SELECT symbol, added_date, notes FROM watchlist ORDER BY added_date DESC"
            ).fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"⚠️ [StockDB.get_watchlist] Error: {e}")
            return []

    def remove_from_watchlist(self, symbol: str):
        """
        Remove a stock from the watchlist.

        Args:
            symbol: NSE stock symbol to remove
        """
        try:
            conn = self._get_connection()
            conn.execute(
                "DELETE FROM watchlist WHERE symbol = ?",
                (symbol.upper(),),
            )
            conn.commit()
            conn.close()
            return {"status": "removed", "symbol": symbol.upper()}
        except Exception as e:
            print(f"⚠️ [StockDB.remove_from_watchlist] Error: {e}")
            return {"error": str(e)}
