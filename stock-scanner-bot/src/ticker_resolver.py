from __future__ import annotations

from config import COMPANY_ALIASES, SECTOR_TICKERS
from src.intent_parser import ParsedIntent


class TickerResolver:
    def resolve(self, parsed: ParsedIntent) -> list[str]:
        tickers = []
        raw_upper = parsed.raw_text.strip().upper()
        if raw_upper in COMPANY_ALIASES:
            tickers.append(COMPANY_ALIASES[raw_upper])
        for ticker in parsed.tickers:
            if ticker not in tickers and ticker not in COMPANY_ALIASES:
                tickers.append(ticker)
        for company in parsed.companies:
            alias = COMPANY_ALIASES.get(company.upper())
            if alias and alias not in tickers:
                tickers.append(alias)
        if parsed.sector and not tickers:
            tickers.extend(SECTOR_TICKERS.get(parsed.sector, [])[:8])
        return tickers

    def sector_tickers(self, sector: str, limit: int = 8) -> list[str]:
        return SECTOR_TICKERS.get(sector, [])[:limit]
