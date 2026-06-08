from __future__ import annotations

from dataclasses import asdict

from config import SECTOR_TICKERS
from src.fundamental_analysis import FundamentalAnalysis
from src.news_collector import NewsCollector, NewsItem
from src.sentiment_analysis import SentimentAnalysis
from src.stock_data import StockDataClient, StockSnapshot
from src.stock_scorer import StockScorer
from src.technical_analysis import TechnicalAnalysis


DISCLAIMER = "หมายเหตุ: ข้อมูลนี้ใช้เพื่อการศึกษาและช่วยประกอบการตัดสินใจเท่านั้น ไม่ใช่คำแนะนำการลงทุนแบบรับประกันผลตอบแทน ผู้ลงทุนควรศึกษาข้อมูลเพิ่มเติมและบริหารความเสี่ยงด้วยตนเอง"


class ResponseGenerator:
    def __init__(self, data_client: StockDataClient | None = None) -> None:
        self.data_client = data_client or StockDataClient()
        self.technical = TechnicalAnalysis()
        self.fundamental = FundamentalAnalysis()
        self.sentiment = SentimentAnalysis()
        self.scorer = StockScorer()
        self.news = NewsCollector()

    def stock_scan(self, ticker: str) -> str:
        report = self._analyze_ticker(ticker)
        return self.stock_scan_from_report(report)

    def stock_scan_from_report(self, report: dict) -> str:
        snapshot: StockSnapshot = report["snapshot"]
        technical = report["technical"]
        fundamental = report["fundamental"]
        sentiment = report["sentiment"]
        score = report["score"]
        news_items = report["news"]
        return "\n".join(
            [
                f"Stock Scan: {snapshot.ticker} - {snapshot.company_name}",
                "",
                "ราคาและภาพรวม",
                f"- ราคาล่าสุด: {snapshot.latest_price}",
                f"- เปลี่ยนแปลงวันนี้: {snapshot.daily_change_pct}%",
                f"- Market Cap: {snapshot.market_cap}",
                f"- Exchange: {snapshot.exchange}",
                f"- Sector: {snapshot.sector}",
                f"- Industry: {snapshot.industry}",
                "",
                "ธุรกิจหลัก",
                self._shorten(snapshot.business_overview, 650),
                "",
                "ข่าวล่าสุด",
                self._format_news(news_items),
                "",
                "Technical View",
                f"- Trend: {technical['trend']}",
                f"- MA20: {technical['ma20']}",
                f"- MA50: {technical['ma50']}",
                f"- MA200: {technical['ma200']}",
                f"- RSI 14: {technical['rsi14']} ({technical['momentum']})",
                f"- MACD: {technical['macd']} / Signal: {technical['macd_signal']} ({technical['macd_interpretation']})",
                f"- Bollinger Bands: {technical['bollinger_lower']} - {technical['bollinger_upper']}",
                f"- Volume: {technical['volume_trend']} | Avg 20D: {technical['average_volume_20d']}",
                f"- Support: {technical['support']}",
                f"- Resistance: {technical['resistance']}",
                f"- Buy Zone: {technical['buy_zone']}",
                f"- Take Profit Zone: {technical['take_profit_zone']}",
                f"- Stop Loss: {technical['stop_loss_area']}",
                "",
                "Fundamental View",
                f"- Revenue growth: {fundamental['revenue_growth']}",
                f"- EPS growth: {fundamental['eps_growth']}",
                f"- P/E: {fundamental['pe_ratio']}",
                f"- Gross margin: {fundamental['gross_margin']}",
                f"- Free cash flow: {fundamental['free_cash_flow']}",
                f"- Debt level: {fundamental['debt_level']}",
                f"- Valuation view: {fundamental['valuation_view']}",
                f"- Competitive advantage: {fundamental['competitive_advantage']}",
                "",
                "Bull Case",
                self._bullets(sentiment["bullish_points"]),
                "",
                "Bear Case",
                self._bullets(sentiment["bearish_points"]),
                "",
                "Risk Level",
                f"- {report['risk_level']}",
                "",
                "Overall Score",
                f"- {score['overall_score']} / 100 = {score['label']}",
                f"- Fundamental: {score['fundamental_score']} | Technical: {score['technical_score']} | News: {score['news_sentiment_score']} | Valuation: {score['valuation_score']} | Risk: {score['risk_score']}",
                "",
                "Bot View",
                f"- ระยะสั้น: {technical['trend']} / {sentiment['label']}",
                f"- ระยะกลาง: ดูแนว {technical['support']} - {technical['resistance']}",
                f"- ระยะยาว: {fundamental['valuation_view']}",
                f"- เหมาะกับนักลงทุนแบบ: {self._investor_fit(report['risk_level'])}",
                f"- Action: {self._action(report)}",
                "",
                f"Disclaimer: {DISCLAIMER}",
            ]
        )

    @staticmethod
    def help_menu() -> str:
        return "\n".join(
            [
                "คำสั่งที่ใช้กับ WealthViewer Bot ได้",
                "",
                "1. สแกนหุ้นเต็ม",
                "- NVDA",
                "- Tesla",
                "- วิเคราะห์ AAPL",
                "",
                "2. วิเคราะห์เทคนิค",
                "- แนวรับแนวต้าน NVDA",
                "- RSI AMD",
                "- AAPL support resistance",
                "",
                "3. ข่าวหุ้น",
                "- ข่าว TSLA วันนี้",
                "- สรุปข่าว Microsoft",
                "- PLTR news",
                "",
                "4. พื้นฐานหุ้น",
                "- พื้นฐาน AAPL ดีไหม",
                "- งบ NVDA เป็นยังไง",
                "- revenue Tesla",
                "",
                "5. เปรียบเทียบหุ้น",
                "- NVDA vs AMD",
                "- เทียบ AAPL กับ MSFT",
                "",
                "6. สแกนกลุ่มหุ้น",
                "- สแกน semiconductor",
                "- หุ้น AI ตัวไหนน่าสนใจ",
                "- หุ้น dividend",
                "- healthcare / financial / cloud / software / momentum",
                "",
                "7. Watchlist",
                "- เพิ่ม NVDA",
                "- ลบ TSLA",
                "- สรุป watchlist",
                "",
                "8. Price alert",
                "- แจ้งเตือนถ้า NVDA ลงถึง 120",
                "- แจ้งเตือนถ้า AAPL ทะลุ 220",
                "",
                "พิมพ์ ticker หรือชื่อบริษัทได้เลย เช่น NVDA, AAPL, Tesla",
                "",
                DISCLAIMER,
            ]
        )

    def technical_scan(self, ticker: str) -> str:
        report = self._analyze_ticker(ticker)
        technical = report["technical"]
        return "\n".join(
            [
                f"Technical Scan: {ticker.upper()}",
                f"- Trend: {technical['trend']}",
                f"- Support: {technical['support']}",
                f"- Resistance: {technical['resistance']}",
                f"- MA20: {technical['ma20']}",
                f"- MA50: {technical['ma50']}",
                f"- MA200: {technical['ma200']}",
                f"- RSI 14: {technical['rsi14']} ({technical['momentum']})",
                f"- MACD: {technical['macd']} / Signal: {technical['macd_signal']} ({technical['macd_interpretation']})",
                f"- Bollinger Bands: {technical['bollinger_lower']} - {technical['bollinger_upper']}",
                f"- Volume trend: {technical['volume_trend']}",
                f"- Buy zone: {technical['buy_zone']}",
                f"- Take profit zone: {technical['take_profit_zone']}",
                f"- Stop-loss area: {technical['stop_loss_area']}",
                f"- Risk level: {report['risk_level']}",
                "",
                DISCLAIMER,
            ]
        )

    def news_scan(self, ticker: str) -> str:
        snapshot = self.data_client.get_snapshot(ticker)
        news_items = self.news.collect_for_ticker(ticker, snapshot.company_name)
        sentiment = self.sentiment.score_news(news_items)
        return "\n".join(
            [
                f"News Scan: {ticker.upper()} - {snapshot.company_name}",
                self._format_news(news_items),
                "",
                f"Short-term sentiment: {sentiment['label']} ({sentiment['score']}/100)",
                "Bullish points:",
                self._bullets(sentiment["bullish_points"]),
                "Bearish points:",
                self._bullets(sentiment["bearish_points"]),
                "",
                DISCLAIMER,
            ]
        )

    def fundamental_scan(self, ticker: str) -> str:
        snapshot = self.data_client.get_snapshot(ticker)
        fundamental = self.fundamental.analyze(snapshot)
        return "\n".join(
            [
                f"Fundamental Scan: {ticker.upper()} - {snapshot.company_name}",
                f"- Revenue growth: {fundamental['revenue_growth']}",
                f"- EPS growth: {fundamental['eps_growth']}",
                f"- P/E: {fundamental['pe_ratio']}",
                f"- Gross margin: {fundamental['gross_margin']}",
                f"- Operating margin: {fundamental['operating_margin']}",
                f"- Free cash flow: {fundamental['free_cash_flow']}",
                f"- Debt level: {fundamental['debt_level']}",
                f"- Valuation: {fundamental['valuation_view']}",
                f"- Competitive advantage: {fundamental['competitive_advantage']}",
                f"- Fundamental score: {fundamental['fundamental_score']}/100",
                "",
                DISCLAIMER,
            ]
        )

    def compare(self, tickers: list[str]) -> str:
        reports = [self._analyze_ticker(ticker) for ticker in tickers[:4]]
        rows = ["| Metric | " + " | ".join(report["snapshot"].ticker for report in reports) + " |", "| --- | " + " | ".join(["---"] * len(reports)) + " |"]
        metrics = [
            ("Price", lambda report: report["snapshot"].latest_price),
            ("Market Cap", lambda report: report["snapshot"].market_cap),
            ("Revenue Growth", lambda report: report["fundamental"]["revenue_growth"]),
            ("P/E", lambda report: report["fundamental"]["pe_ratio"]),
            ("RSI", lambda report: report["technical"]["rsi14"]),
            ("Trend", lambda report: report["technical"]["trend"]),
            ("Risk", lambda report: report["risk_level"]),
            ("Score", lambda report: report["score"]["overall_score"]),
        ]
        for name, getter in metrics:
            rows.append("| " + name + " | " + " | ".join(str(getter(report)) for report in reports) + " |")
        best = max(reports, key=lambda report: report["score"]["overall_score"]) if reports else None
        conclusion = f"สรุป: {best['snapshot'].ticker} มีคะแนนรวมสูงสุดในชุดนี้ แต่ควรดู valuation และ risk เพิ่มเติม" if best else "ยังไม่มีข้อมูลเปรียบเทียบ"
        return "\n".join(["Peer Comparison", "", *rows, "", conclusion, "", DISCLAIMER])

    def sector_scan(self, sector: str) -> str:
        tickers = SECTOR_TICKERS.get(sector, [])[:8]
        reports = [self._analyze_ticker(ticker) for ticker in tickers]
        rows = ["| Ticker | Trend | RSI | Risk | Score | Action |", "| --- | --- | --- | --- | --- | --- |"]
        for report in reports:
            rows.append(
                f"| {report['snapshot'].ticker} | {report['technical']['trend']} | {report['technical']['rsi14']} | {report['risk_level']} | {report['score']['overall_score']} | {self._action(report)} |"
            )
        return "\n".join([f"Sector Scan: {sector}", "", "Watchlist table:", *rows, "", DISCLAIMER])

    def _analyze_ticker(self, ticker: str) -> dict:
        snapshot = self.data_client.get_snapshot(ticker)
        history = self.data_client.get_history(ticker)
        technical = self.technical.analyze(history)
        fundamental = self.fundamental.analyze(snapshot)
        news_items = self.news.collect_for_ticker(ticker, snapshot.company_name)
        sentiment = self.sentiment.score_news(news_items)
        risk_level = self._risk_level(technical, fundamental, sentiment)
        score = self.scorer.score(fundamental, technical, sentiment, risk_level)
        return {
            "snapshot": snapshot,
            "technical": technical,
            "fundamental": fundamental,
            "news": news_items,
            "sentiment": sentiment,
            "risk_level": risk_level,
            "score": score,
        }

    @staticmethod
    def _risk_level(technical: dict, fundamental: dict, sentiment: dict) -> str:
        if technical.get("momentum") in {"Overbought", "Oversold"} or sentiment.get("score", 50) <= 35:
            return "High"
        if fundamental.get("pe_ratio") and fundamental["pe_ratio"] > 60:
            return "Medium"
        if technical.get("trend") in {"Weak / correction", "Below MA50"}:
            return "Medium"
        return "Low"

    @staticmethod
    def _action(report: dict) -> str:
        score = report["score"]["overall_score"]
        technical = report["technical"]
        risk = report["risk_level"]
        if score >= 75 and risk != "High":
            return "Buy on Dip"
        if technical.get("momentum") == "Overbought":
            return "Take Profit"
        if score < 40 or risk == "High":
            return "Avoid"
        if score >= 55:
            return "Watch"
        return "Hold"

    @staticmethod
    def _investor_fit(risk_level: str) -> str:
        return {"Low": "defensive / long-term", "Medium": "growth with risk control", "High": "high-risk momentum only"}.get(risk_level, "watchlist")

    @staticmethod
    def _format_news(news_items: list[NewsItem]) -> str:
        if not news_items:
            return "ยังไม่พบข่าวล่าสุดจาก RSS ที่ match กับหุ้นนี้ครับ"
        lines = []
        for index, item in enumerate(news_items, start=1):
            lines.extend([f"{index}. {item.title}", f"   สรุป: {item.summary or 'No summary'}", "   ผลกระทบ: กระทบ sentiment หรือ expectation ระยะสั้น ควรอ่านแหล่งข่าวเต็ม", f"   แหล่งข่าว: {item.url}"])
        return "\n".join(lines)

    @staticmethod
    def _bullets(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items)

    @staticmethod
    def _shorten(text: str, max_len: int) -> str:
        return text if len(text) <= max_len else text[: max_len - 3] + "..."
