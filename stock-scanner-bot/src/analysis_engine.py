from __future__ import annotations

from dataclasses import dataclass

from src.data_structurer import StructuredData


@dataclass(frozen=True)
class AnalysisResult:
    intent: str
    structured: StructuredData
    risk_level: str
    action_label: str
    summary_points: list[str]


class AnalysisEngine:
    def analyze(self, intent: str, structured: StructuredData) -> AnalysisResult:
        reports = structured.reports
        if not reports:
            return AnalysisResult(intent, structured, "Unknown", "Clarify", ["No validated market data was available."])
        high_risk_count = sum(1 for report in reports if report["risk_level"] == "High")
        avg_score = sum(report["score"]["overall_score"] for report in reports) / len(reports)
        risk = "High" if high_risk_count else "Medium" if avg_score < 60 else "Low"
        action = "Watch" if avg_score >= 50 else "Avoid"
        points = [
            f"Analyzed {len(reports)} ticker(s).",
            f"Average score: {avg_score:.1f}/100.",
            f"Validation: price={structured.validation.price_data_status}, news={structured.validation.news_data_status}, financials={structured.validation.financial_data_status}.",
        ]
        return AnalysisResult(intent, structured, risk, action, points)
