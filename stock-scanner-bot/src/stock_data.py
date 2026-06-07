from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yfinance as yf


@dataclass
class StockSnapshot:
    ticker: str
    company_name: str = ""
    exchange: str = ""
    sector: str = ""
    industry: str = ""
    business_overview: str = ""
    latest_price: float | None = None
    daily_change_pct: float | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    revenue_growth: float | None = None
    eps_growth: float | None = None
    analyst_sentiment: str = "Unavailable"


class StockDataClient:
    def __init__(self, cache_dir: str = ".yfinance-cache") -> None:
        cache_path = Path.cwd() / cache_dir
        cache_path.mkdir(parents=True, exist_ok=True)
        try:
            yf.set_tz_cache_location(str(cache_path))
        except Exception:
            pass

    def get_snapshot(self, ticker: str) -> StockSnapshot:
        symbol = ticker.replace(".", "-").upper()
        try:
            yf_ticker = yf.Ticker(symbol)
            info = yf_ticker.info or {}
            fast = yf_ticker.fast_info or {}
        except Exception:
            info = {}
            fast = {}

        price = self._safe_float(fast.get("last_price") or info.get("currentPrice") or info.get("regularMarketPrice"))
        previous = self._safe_float(info.get("previousClose"))
        change = round((price - previous) / previous * 100, 2) if price and previous else None
        return StockSnapshot(
            ticker=symbol,
            company_name=info.get("longName") or info.get("shortName") or symbol,
            exchange=info.get("exchange", ""),
            sector=info.get("sector", "Unknown"),
            industry=info.get("industry", "Unknown"),
            business_overview=info.get("longBusinessSummary", "Business overview unavailable from data source."),
            latest_price=price,
            daily_change_pct=change,
            market_cap=self._safe_float(info.get("marketCap") or fast.get("market_cap")),
            pe_ratio=self._safe_float(info.get("trailingPE") or info.get("forwardPE")),
            revenue_growth=self._safe_float(info.get("revenueGrowth")),
            eps_growth=self._safe_float(info.get("earningsGrowth")),
            analyst_sentiment=self._analyst_sentiment(info),
        )

    def get_history(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        try:
            frame = yf.download(ticker.replace(".", "-"), period=period, interval="1d", auto_adjust=False, progress=False, threads=False)
        except Exception:
            return pd.DataFrame()
        if frame.empty:
            return frame
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)
        return frame.rename(columns={column: str(column).title() for column in frame.columns})

    @staticmethod
    def _safe_float(value) -> float | None:
        try:
            return round(float(value), 4)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _analyst_sentiment(info: dict) -> str:
        mean = info.get("recommendationMean")
        key = info.get("recommendationKey")
        if key:
            return str(key).replace("_", " ").title()
        if mean is None:
            return "Unavailable"
        if mean <= 2:
            return "Bullish"
        if mean <= 3:
            return "Neutral"
        return "Cautious"
