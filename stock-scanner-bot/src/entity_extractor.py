from __future__ import annotations

from dataclasses import dataclass, field

from src.intent_parser import ParsedIntent
from src.ticker_resolver import TickerResolver


@dataclass(frozen=True)
class ExtractedEntities:
    tickers: list[str] = field(default_factory=list)
    company_names: list[str] = field(default_factory=list)
    sector: str | None = None
    market: str | None = None
    timeframe: str | None = None
    user_objective: str | None = None
    output_format: str = "line"
    risk_preference: str | None = None


class EntityExtractor:
    def __init__(self, resolver: TickerResolver | None = None) -> None:
        self.resolver = resolver or TickerResolver()

    def extract(self, parsed: ParsedIntent) -> ExtractedEntities:
        return ExtractedEntities(
            tickers=self.resolver.resolve(parsed),
            company_names=parsed.companies,
            sector=parsed.sector,
            market="US",
            timeframe=parsed.timeframe,
            user_objective=parsed.intent,
            output_format="line",
            risk_preference=parsed.risk_style,
        )
