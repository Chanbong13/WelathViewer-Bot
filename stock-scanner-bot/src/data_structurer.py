from __future__ import annotations

from dataclasses import dataclass, field

from src.data_collector import CollectedData
from src.data_validator import ValidationResult
from src.data_searcher import SourceResult


@dataclass(frozen=True)
class StructuredData:
    reports: list[dict]
    sources: list[SourceResult]
    validation: ValidationResult
    warnings: list[str] = field(default_factory=list)


class DataStructurer:
    def structure(self, collected: CollectedData, sources: list[SourceResult], validation: ValidationResult) -> StructuredData:
        return StructuredData(
            reports=collected.reports,
            sources=sources,
            validation=validation,
            warnings=[*collected.warnings, *validation.warnings],
        )
