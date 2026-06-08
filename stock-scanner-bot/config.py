from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    polygon_api_key: str = os.getenv("POLYGON_API_KEY", "")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    line_channel_access_token: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    line_channel_secret: str = os.getenv("LINE_CHANNEL_SECRET", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/stock_scanner.db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_drive_folder_id: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_refresh_token: str = os.getenv("GOOGLE_REFRESH_TOKEN", "")
    google_application_credentials_json: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
    google_service_account_file: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
    scheduler_secret: str = os.getenv("SCHEDULER_SECRET", os.getenv("DAILY_REPORT_TOKEN", ""))
    daily_report_token: str = os.getenv("DAILY_REPORT_TOKEN", "")
    default_line_user_id: str = os.getenv("DEFAULT_LINE_USER_ID", "")
    timezone: str = os.getenv("TIMEZONE", "Asia/Bangkok")
    daily_report_tickers: list[str] = None
    notebooklm_source_prefix: str = os.getenv("NOTEBOOKLM_SOURCE_PREFIX", "NotebookLM_Source_Global_Stock_Briefing")
    pdf_report_prefix: str = os.getenv("PDF_REPORT_PREFIX", "Global_Stock_Briefing")
    csv_report_prefix: str = os.getenv("CSV_REPORT_PREFIX", "Raw_Stock_Data")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "th")
    max_news_items: int = int(os.getenv("MAX_NEWS_ITEMS", "5"))
    price_history_period: str = os.getenv("PRICE_HISTORY_PERIOD", "1y")

    def __post_init__(self) -> None:
        raw = os.getenv("DAILY_REPORT_TICKERS", "NVDA,MSFT,AAPL,GOOGL,AMZN,META,TSLA,AVGO,AMD,COST,JPM,LLY")
        object.__setattr__(self, "daily_report_tickers", [ticker.strip().upper() for ticker in raw.split(",") if ticker.strip()])


NEWS_FEEDS = {
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "CNBC Markets": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "Nasdaq": "https://www.nasdaq.com/feed/rssoutbound?category=Stocks",
    "SEC Latest Filings": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=8-K&company=&dateb=&owner=include&start=0&count=80&output=atom",
}


COMPANY_ALIASES = {
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "NVIDIA": "NVDA",
    "TESLA": "TSLA",
    "GOOGLE": "GOOGL",
    "ALPHABET": "GOOGL",
    "AMAZON": "AMZN",
    "META": "META",
    "FACEBOOK": "META",
    "BROADCOM": "AVGO",
    "AMD": "AMD",
    "PALANTIR": "PLTR",
    "NETFLIX": "NFLX",
    "COSTCO": "COST",
    "JPMORGAN": "JPM",
}


SECTOR_TICKERS = {
    "semiconductor": ["NVDA", "AMD", "AVGO", "INTC", "QCOM", "MU", "MRVL", "AMAT", "LRCX", "KLAC", "ASML", "TSM"],
    "ai": ["NVDA", "MSFT", "GOOGL", "AMZN", "AVGO", "AMD", "PLTR", "META", "ORCL", "SNOW"],
    "cloud": ["MSFT", "AMZN", "GOOGL", "ORCL", "CRM", "NOW", "DDOG", "SNOW", "NET"],
    "software": ["MSFT", "CRM", "NOW", "ADBE", "SNOW", "DDOG", "PLTR", "NET"],
    "healthcare": ["LLY", "UNH", "JNJ", "MRK", "ABBV", "AMGN", "GILD", "ISRG", "REGN", "NVO"],
    "biotech": ["AMGN", "GILD", "REGN", "VRTX", "BIIB", "MRNA"],
    "consumer": ["COST", "WMT", "HD", "MCD", "SBUX", "NKE", "AMZN", "TGT"],
    "financial": ["JPM", "BAC", "GS", "MS", "BLK", "V", "MA", "AXP", "C"],
    "dividend": ["KO", "PEP", "PG", "JNJ", "MCD", "COST", "WMT", "CL", "MO", "PM"],
    "momentum": ["TSLA", "AMD", "PLTR", "COIN", "MSTR", "SNOW", "NET", "RBLX", "SMCI"],
    "sp500": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "BRK-B", "LLY", "JPM", "AVGO", "TSLA", "UNH", "V", "XOM", "MA", "COST"],
}
