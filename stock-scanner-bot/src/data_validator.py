from __future__ import annotations

from dataclasses import dataclass, field

from src.data_collector import CollectedData


@dataclass(frozen=True)
class ValidationResult:
    ticker_valid: bool
    price_data_status: str
    news_data_status: str
    financial_data_status: str
    warnings: list[str] = field(default_factory=list)


class DataValidator:
    def validate(self, collected: CollectedData) -> ValidationResult:
        warnings = list(collected.warnings)
        if not collected.reports:
            return ValidationResult(False, "missing", "missing", "missing", warnings + ["No analyzable ticker data collected."])
        price_missing = [report["snapshot"].ticker for report in collected.reports if report["snapshot"].latest_price is None]
        financial_partial = [report["snapshot"].ticker for report in collected.reports if report["fundamental"].get("pe_ratio") is None]
        news_missing = [report["snapshot"].ticker for report in collected.reports if not report.get("news")]
        if price_missing:
            warnings.append(f"Missing latest price for: {', '.join(price_missing)}")
        if financial_partial:
            warnings.append(f"Partial financial metrics for: {', '.join(financial_partial)}")
        if news_missing:
            warnings.append(f"No recent matched RSS news for: {', '.join(news_missing)}")
        return ValidationResult(
            ticker_valid=not price_missing,
            price_data_status="fresh" if not price_missing else "partial",
            news_data_status="fresh" if not news_missing else "partial",
            financial_data_status="available" if not financial_partial else "partial",
            warnings=warnings,
        )
