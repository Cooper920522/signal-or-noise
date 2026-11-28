# config.py
DB_PATH = "signal.db"

# 抓新聞的股票
TICKERS = ["NVDA", "AAPL", "MSFT"]

# 抓股價的股票：新聞那幾檔 + QQQ 當大盤對照組
PRICE_TICKERS = TICKERS + ["QQQ"]

# 股價從哪一天開始抓
PRICE_START = "2024-01-01"