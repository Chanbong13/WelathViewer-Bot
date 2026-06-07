from __future__ import annotations

import re
from dataclasses import dataclass, field


TICKER_RE = re.compile(r"\b[A-Z]{1,5}(?:[.-][A-Z])?\b", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedIntent:
    intent: str
    tickers: list[str] = field(default_factory=list)
    companies: list[str] = field(default_factory=list)
    sector: str | None = None
    timeframe: str | None = None
    risk_style: str | None = None
    raw_text: str = ""


class IntentParser:
    TECH_KEYWORDS = ["แนวรับ", "แนวต้าน", "กราฟ", "rsi", "macd", "support", "resistance", "technical", "จุดซื้อ", "stop"]
    NEWS_KEYWORDS = ["ข่าว", "news", "headline", "ล่าสุด", "today"]
    FUNDAMENTAL_KEYWORDS = ["พื้นฐาน", "งบ", "รายได้", "eps", "revenue", "fundamental", "margin", "valuation"]
    COMPARE_KEYWORDS = ["เทียบ", "compare", " vs ", "versus", "กับ"]
    SECTOR_KEYWORDS = ["sector", "กลุ่ม", "semiconductor", "ai", "cloud", "software", "healthcare", "biotech", "consumer", "financial", "dividend", "momentum", "sp500", "s&p500"]
    WATCHLIST_ADD = ["เพิ่ม", "add"]
    WATCHLIST_REMOVE = ["ลบ", "remove", "delete"]
    WATCHLIST_SUMMARY = ["watchlist", "วอชลิสต์", "สรุป watchlist"]
    ALERT_KEYWORDS = ["แจ้งเตือน", "alert"]

    def parse(self, text: str) -> ParsedIntent:
        normalized = self._normalize(text)
        tickers = self._extract_tickers(text)
        sector = self._extract_sector(normalized)
        intent = self._detect_intent(normalized, tickers, sector)
        companies = self._extract_company_candidates(text, tickers)
        return ParsedIntent(
            intent=intent,
            tickers=tickers,
            companies=companies,
            sector=sector,
            timeframe="today" if any(key in normalized for key in ["วันนี้", "today", "ล่าสุด"]) else None,
            risk_style="defensive" if "defensive" in normalized or "ปลอดภัย" in normalized else None,
            raw_text=text,
        )

    def _detect_intent(self, normalized: str, tickers: list[str], sector: str | None) -> str:
        if self._contains_any(normalized, self.ALERT_KEYWORDS):
            return "price_alert"
        if self._contains_any(normalized, self.WATCHLIST_SUMMARY):
            if self._contains_any(normalized, self.WATCHLIST_ADD):
                return "watchlist_add"
            if self._contains_any(normalized, self.WATCHLIST_REMOVE):
                return "watchlist_remove"
            return "watchlist_summary"
        if self._contains_any(normalized, self.WATCHLIST_ADD) and tickers:
            return "watchlist_add"
        if self._contains_any(normalized, self.WATCHLIST_REMOVE) and tickers:
            return "watchlist_remove"
        if self._contains_any(normalized, self.COMPARE_KEYWORDS) and len(tickers) >= 2:
            return "peer_comparison"
        if sector and self._contains_any(normalized, self.SECTOR_KEYWORDS):
            return "sector_scan"
        if self._contains_any(normalized, self.NEWS_KEYWORDS):
            return "news_scan"
        if self._contains_any(normalized, self.TECH_KEYWORDS):
            return "technical_analysis"
        if self._contains_any(normalized, self.FUNDAMENTAL_KEYWORDS):
            return "fundamental_analysis"
        return "stock_detail_scan"

    @staticmethod
    def _extract_tickers(text: str) -> list[str]:
        ignored = {"AI", "RSI", "MACD", "EPS", "PE", "CEO", "IPO", "ETF", "USA", "USD"}
        found = []
        for match in TICKER_RE.findall(text.upper()):
            ticker = match.replace(".", "-")
            if ticker not in ignored and ticker not in found:
                found.append(ticker)
        return found

    @staticmethod
    def _extract_company_candidates(text: str, tickers: list[str]) -> list[str]:
        cleaned = re.sub(TICKER_RE, " ", text)
        words = [part.strip(" ?!.,") for part in cleaned.split()]
        candidates = [word for word in words if len(word) >= 4 and not re.search(r"[\u0E00-\u0E7F]", word)]
        return [candidate for candidate in candidates if candidate.upper() not in tickers][:3]

    @staticmethod
    def _extract_sector(normalized: str) -> str | None:
        aliases = {
            "semiconductor": ["semiconductor", "chip", "ชิป"],
            "ai": [" ai ", "หุ้น ai", "artificial intelligence"],
            "cloud": ["cloud"],
            "software": ["software"],
            "healthcare": ["healthcare", "สุขภาพ"],
            "biotech": ["biotech"],
            "consumer": ["consumer", "ค้าปลีก"],
            "financial": ["financial", "bank", "ธนาคาร", "การเงิน"],
            "dividend": ["dividend", "ปันผล"],
            "momentum": ["momentum", "high risk", "เก็งกำไร"],
            "sp500": ["sp500", "s&p500", "s&p 500"],
        }
        padded = f" {normalized} "
        for sector, keys in aliases.items():
            if any(key in padded for key in keys):
                return sector
        return None

    @staticmethod
    def _contains_any(text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())
