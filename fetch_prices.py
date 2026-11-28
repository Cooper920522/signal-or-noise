# fetch_prices.py
import sqlite3
from datetime import datetime, timezone

import yfinance as yf

from config import DB_PATH, PRICE_START, PRICE_TICKERS


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            date       TEXT NOT NULL,   -- 交易日（美東日期），YYYY-MM-DD
            ticker     TEXT NOT NULL,
            open       REAL,
            high       REAL,
            low        REAL,
            close      REAL,
            volume     INTEGER,
            fetched_at TEXT NOT NULL,
            PRIMARY KEY (date, ticker)
        )
    """)

    fetched_at = datetime.now(timezone.utc).isoformat()

    for t in PRICE_TICKERS:
        try:
            df = yf.Ticker(t).history(start=PRICE_START)
        except Exception as e:
            print(f"{t}: failed to fetch prices - {e}")
            continue

        if df.empty:
            print(f"{t}: no data")
            continue

        rows = [
            (idx.strftime("%Y-%m-%d"), t,
                float(r["Open"]), float(r["High"]), float(r["Low"]), float(r["Close"]),
                int(r["Volume"]), fetched_at)
            for idx, r in df.iterrows()
        ]

        conn.executemany(
            """INSERT OR REPLACE INTO prices
                (date, ticker, open, high, low, close, volume, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        print(f"{t}: {len(rows)} rows saved")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()