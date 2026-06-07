from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass

import feedparser
import requests

from config import NEWS_FEEDS


@dataclass(frozen=True)
class NewsItem:
    title: str
    summary: str
    url: str
    source: str
    published: str


class NewsCollector:
    def __init__(self, max_items: int = 5, timeout: int = 12) -> None:
        self.max_items = max_items
        self.timeout = timeout

    def collect_for_ticker(self, ticker: str, company: str = "") -> list[NewsItem]:
        matches: list[NewsItem] = []
        keywords = {ticker.upper(), company.upper()} if company else {ticker.upper()}
        for source, url in NEWS_FEEDS.items():
            matches.extend(self._read_feed(source, url, keywords))
            if len(matches) >= self.max_items:
                break
        return self._dedupe(matches)[: self.max_items]

    def _read_feed(self, source: str, url: str, keywords: set[str]) -> list[NewsItem]:
        try:
            response = requests.get(url, timeout=self.timeout, headers={"User-Agent": "stock-scanner-bot/1.0"})
            response.raise_for_status()
            feed = feedparser.parse(response.content)
        except Exception:
            return []
        items = []
        for entry in feed.entries[:80]:
            title = self._clean(getattr(entry, "title", ""))
            summary = self._clean(getattr(entry, "summary", ""))
            haystack = f"{title} {summary}".upper()
            if any(keyword and keyword in haystack for keyword in keywords):
                items.append(
                    NewsItem(
                        title=title,
                        summary=summary,
                        url=getattr(entry, "link", url),
                        source=source,
                        published=getattr(entry, "published", "") or getattr(entry, "updated", "") or dt.datetime.utcnow().isoformat(),
                    )
                )
        return items

    @staticmethod
    def _clean(text: str) -> str:
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _dedupe(items: list[NewsItem]) -> list[NewsItem]:
        seen = set()
        unique = []
        for item in items:
            key = item.url or item.title
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique
