from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from config import NEWS_FEEDS
from src.entity_extractor import ExtractedEntities


@dataclass(frozen=True)
class SourceResult:
    source_name: str
    source_type: str
    url: str
    retrieved_at: str
    raw_data: dict


class DataSearcher:
    def search(self, intent: str, entities: ExtractedEntities) -> list[SourceResult]:
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        sources: list[SourceResult] = []
        for ticker in entities.tickers:
            sources.append(SourceResult("Yahoo Finance", "market_data", f"https://finance.yahoo.com/quote/{ticker}", now, {"ticker": ticker}))
            sources.append(SourceResult("Nasdaq", "market_data", f"https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}", now, {"ticker": ticker}))
            sources.append(SourceResult("SEC EDGAR", "filings", "https://www.sec.gov/edgar/search/", now, {"ticker": ticker}))
        if intent in {"news_scan", "stock_detail_scan", "sector_scan", "peer_comparison"}:
            for name, url in NEWS_FEEDS.items():
                sources.append(SourceResult(name, "news", url, now, {}))
        return sources
