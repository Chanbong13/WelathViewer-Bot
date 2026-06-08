from __future__ import annotations

from dataclasses import dataclass, field

from src.entity_extractor import ExtractedEntities
from src.response_generator import ResponseGenerator


@dataclass
class CollectedData:
    reports: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class DataCollector:
    def __init__(self, responses: ResponseGenerator) -> None:
        self.responses = responses

    def collect(self, intent: str, entities: ExtractedEntities) -> CollectedData:
        reports = []
        warnings = []
        tickers = entities.tickers[:8]
        for ticker in tickers:
            try:
                reports.append(self.responses._analyze_ticker(ticker))
            except Exception as exc:
                warnings.append(f"{ticker}: {exc}")
        return CollectedData(reports=reports, warnings=warnings)
