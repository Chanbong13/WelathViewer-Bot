from __future__ import annotations

from src.stock_data import StockSnapshot


class FundamentalAnalysis:
    def analyze(self, snapshot: StockSnapshot) -> dict:
        score = 50
        if snapshot.revenue_growth and snapshot.revenue_growth > 0.1:
            score += 15
        if snapshot.eps_growth and snapshot.eps_growth > 0.1:
            score += 15
        if snapshot.pe_ratio and snapshot.pe_ratio < 30:
            score += 10
        if snapshot.pe_ratio and snapshot.pe_ratio > 80:
            score -= 15
        return {
            "revenue_growth": snapshot.revenue_growth,
            "eps_growth": snapshot.eps_growth,
            "pe_ratio": snapshot.pe_ratio,
            "gross_margin": None,
            "operating_margin": None,
            "free_cash_flow": None,
            "debt_level": "Unavailable",
            "valuation_view": self._valuation_view(snapshot.pe_ratio),
            "competitive_advantage": self._moat(snapshot),
            "fundamental_score": max(0, min(100, score)),
        }

    @staticmethod
    def _valuation_view(pe_ratio: float | None) -> str:
        if pe_ratio is None:
            return "Valuation data unavailable"
        if pe_ratio < 20:
            return "Reasonable valuation versus broad growth stocks"
        if pe_ratio < 45:
            return "Moderate to premium valuation"
        return "High valuation; sensitive to growth expectations"

    @staticmethod
    def _moat(snapshot: StockSnapshot) -> str:
        sector = snapshot.sector.lower()
        if "technology" in sector:
            return "Potential moat from product ecosystem, scale, software, data, or platform effects."
        if "health" in sector:
            return "Potential moat from patents, pipeline, regulation, and distribution."
        if "consumer" in sector:
            return "Potential moat from brand, distribution, pricing power, and repeat demand."
        return "Moat requires manual review from filings and company sources."
