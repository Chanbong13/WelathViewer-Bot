from __future__ import annotations


class StockScorer:
    def score(self, fundamental: dict, technical: dict, sentiment: dict, risk_level: str) -> dict:
        fundamental_score = fundamental.get("fundamental_score", 50)
        technical_score = self._technical_score(technical)
        news_score = sentiment.get("score", 50)
        valuation_score = self._valuation_score(fundamental.get("pe_ratio"))
        risk_score = {"Low": 90, "Medium": 60, "High": 25}.get(risk_level, 50)
        overall = round(
            fundamental_score * 0.35
            + technical_score * 0.30
            + news_score * 0.20
            + valuation_score * 0.10
            + risk_score * 0.05,
            1,
        )
        return {
            "overall_score": overall,
            "fundamental_score": fundamental_score,
            "technical_score": technical_score,
            "news_sentiment_score": news_score,
            "valuation_score": valuation_score,
            "risk_score": risk_score,
            "label": self._label(overall),
        }

    @staticmethod
    def _technical_score(technical: dict) -> int:
        score = 50
        if technical.get("trend") == "Strong uptrend":
            score += 25
        elif technical.get("trend") == "Uptrend":
            score += 15
        elif technical.get("trend") in {"Weak / correction", "Below MA50"}:
            score -= 15
        if technical.get("macd_interpretation") == "Bullish momentum":
            score += 10
        if technical.get("momentum") == "Overbought":
            score -= 10
        if technical.get("momentum") == "Oversold":
            score -= 5
        return max(0, min(100, score))

    @staticmethod
    def _valuation_score(pe_ratio: float | None) -> int:
        if pe_ratio is None:
            return 50
        if pe_ratio < 20:
            return 80
        if pe_ratio < 45:
            return 60
        if pe_ratio < 80:
            return 40
        return 25

    @staticmethod
    def _label(score: float) -> str:
        if score >= 80:
            return "Strong candidate"
        if score >= 65:
            return "Good but wait for price"
        if score >= 50:
            return "Neutral / Watch"
        if score >= 35:
            return "Weak"
        return "Avoid"
