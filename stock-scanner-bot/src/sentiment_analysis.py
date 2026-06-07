from __future__ import annotations

from src.news_collector import NewsItem


class SentimentAnalysis:
    POSITIVE = ["beat", "growth", "raises", "upgrade", "record", "strong", "demand", "profit", "surge", "partnership"]
    NEGATIVE = ["miss", "cut", "downgrade", "lawsuit", "probe", "weak", "risk", "decline", "falls", "delay"]

    def score_news(self, news: list[NewsItem]) -> dict:
        if not news:
            return {"score": 50, "label": "Neutral", "bullish_points": ["No recent matched news found."], "bearish_points": ["Limited news visibility."]}
        score = 50
        bullish = []
        bearish = []
        for item in news:
            text = f"{item.title} {item.summary}".lower()
            if any(word in text for word in self.POSITIVE):
                score += 8
                bullish.append(item.title)
            if any(word in text for word in self.NEGATIVE):
                score -= 8
                bearish.append(item.title)
        score = max(0, min(100, score))
        label = "Bullish" if score >= 65 else "Bearish" if score <= 40 else "Neutral"
        return {
            "score": score,
            "label": label,
            "bullish_points": bullish[:3] or ["No clear bullish headline detected."],
            "bearish_points": bearish[:3] or ["No clear bearish headline detected."],
        }
