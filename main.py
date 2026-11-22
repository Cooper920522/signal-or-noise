import yfinance as yf

tickers = ["NVDA", "AAPL", "MSFT"]

# 抓近 3 個月的股價，各存一個 CSV
for t in tickers:
    df = yf.download(t, period="3mo")
    df.to_csv(f"{t}.csv")
    print(t, len(df), "rows")

# 看一則新聞長什麼樣子
news = yf.Ticker("NVDA").news
print(news[0])