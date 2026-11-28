# fetch_news.py
import sqlite3
import time
from datetime import datetime, timezone

import yfinance as yf

from config import DB_PATH, TICKERS


def to_utc_iso(value):
    """把不同格式的時間統一轉成 UTC 的 ISO 字串"""
    if value is None:
        return None
    if isinstance(value, (int, float)):  # Unix 時間戳記（秒）
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    # ISO 字串，例如 "2026-11-20T15:30:00Z"
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc).isoformat()


def parse_item(item, ticker):
    """從一則新聞的 dict 取出我們要的欄位"""
    c = item.get("content", item)  # 新版 yfinance 把欄位包在 content 裡
    provider = c.get("provider") or {}
    url = (c.get("canonicalUrl") or {}).get("url") or c.get("link")
    return {
        "id": item.get("id") or c.get("uuid"),
        "ticker": ticker,
        "title": c.get("title"),
        "publisher": provider.get("displayName") or c.get("publisher"),
        "url": url,
        "published_at": to_utc_iso(c.get("pubDate") or c.get("providerPublishTime")),
    }


def fetch_news_with_retry(ticker, retries=3, wait=30):
    """抓新聞，失敗時等一下再重試，最多 retries 次"""
    for attempt in range(1, retries + 1):
        try:
            return yf.Ticker(ticker).news
        except Exception as e:
            print(f"{ticker}: attempt {attempt}/{retries} failed - {e}")
            if attempt < retries:
                time.sleep(wait)
    return None

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id           TEXT NOT NULL,
            ticker       TEXT NOT NULL,
            title        TEXT,
            publisher    TEXT,
            url          TEXT,
            published_at TEXT,
            fetched_at   TEXT NOT NULL,
            PRIMARY KEY (id, ticker)
        )
    """)

    fetched_at = datetime.now(timezone.utc).isoformat()

    for t in TICKERS:
        items = fetch_news_with_retry(t)
        if items is None:
            print(f"{t}: giving up after retries")
            continue


        new_count = 0
        for item in items:
            row = parse_item(item, t)
            if not row["id"]:
                continue
            cur = conn.execute(
                """INSERT OR IGNORE INTO news
                    (id, ticker, title, publisher, url, published_at, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (row["id"], row["ticker"], row["title"], row["publisher"],
                    row["url"], row["published_at"], fetched_at),
            )
            new_count += cur.rowcount
        print(f"{t}: {len(items)} fetched, {new_count} new")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()