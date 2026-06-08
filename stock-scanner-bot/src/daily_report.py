from __future__ import annotations

import csv
import datetime as dt
import tempfile
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config import Settings
from src.response_generator import DISCLAIMER, ResponseGenerator


class DailyReportService:
    def __init__(self, settings: Settings, responses: ResponseGenerator | None = None) -> None:
        self.settings = settings
        self.responses = responses or ResponseGenerator()

    def generate(self, report_date: dt.date | None = None) -> dict:
        report_date = report_date or dt.date.today()
        date_text = report_date.isoformat()
        reports = [self.responses._analyze_ticker(ticker) for ticker in self.settings.daily_report_tickers]
        output_dir = Path(tempfile.mkdtemp(prefix="stock-scanner-report-"))
        markdown_path = output_dir / f"{self.settings.notebooklm_source_prefix}_{date_text}.md"
        pdf_path = output_dir / f"{self.settings.pdf_report_prefix}_{date_text}.pdf"
        csv_path = output_dir / f"{self.settings.csv_report_prefix}_{date_text}.csv"
        self._write_markdown(markdown_path, date_text, reports)
        self._write_csv(csv_path, reports)
        self._write_pdf(pdf_path, date_text, reports)
        return {
            "date": date_text,
            "files": [pdf_path, markdown_path, csv_path],
            "pdf": pdf_path,
            "markdown": markdown_path,
            "csv": csv_path,
            "summary": self._summary(reports),
        }

    def _write_markdown(self, path: Path, date_text: str, reports: list[dict]) -> None:
        source_index = self._source_index(reports)
        lines = [
            f"# Daily Global Stock Briefing - {date_text}",
            "",
            "Document type: NotebookLM source file",
            "Runtime: Google Cloud Run",
            "Storage: Google Drive",
            "",
            f"Disclaimer: {DISCLAIMER}",
            "",
            "## How To Use In NotebookLM",
            "- Ask by ticker, sector, risk level, technical trend, source ID, or action label.",
            "- Ask NotebookLM to cite `S###` source IDs from the Final Source Index.",
            "- Use ticker-level sections for direct stock questions.",
            "",
            "## Executive Summary",
            f"- Market bias: {self._market_bias(reports)}",
            f"- Tickers covered: {', '.join(report['snapshot'].ticker for report in reports)}",
            f"- Top watchlist candidates: {', '.join(self._top_tickers(reports))}",
            "",
            "## Ticker Coverage Map",
        ]
        for report in reports:
            snapshot = report["snapshot"]
            lines.append(f"- {snapshot.ticker}: {snapshot.company_name} | Sector: {snapshot.sector} | Risk: {report['risk_level']} | Score: {report['score']['overall_score']}")

        lines.extend(["", "## Ticker-Level Analysis", ""])
        for report in reports:
            lines.extend(self._ticker_markdown(report, source_index))

        lines.extend(["", "## Final Source Index", ""])
        if not source_index:
            lines.append("No recent source URLs were collected for this run.")
        else:
            for source_id, item, ticker in source_index:
                lines.extend(
                    [
                        f"### {source_id} - {ticker} - {item.source}",
                        f"- Title: {item.title}",
                        f"- URL: {item.url}",
                        f"- Published: {item.published}",
                        f"- Summary: {item.summary or 'No feed summary provided.'}",
                        "",
                    ]
                )
        path.write_text("\n".join(lines), encoding="utf-8")

    def _ticker_markdown(self, report: dict, source_index: list[tuple]) -> list[str]:
        snapshot = report["snapshot"]
        technical = report["technical"]
        fundamental = report["fundamental"]
        sentiment = report["sentiment"]
        score = report["score"]
        source_ids = [source_id for source_id, item, ticker in source_index if ticker == snapshot.ticker]
        return [
            f"### Ticker: {snapshot.ticker} - {snapshot.company_name}",
            f"Ticker symbol: {snapshot.ticker}",
            f"Company name: {snapshot.company_name}",
            f"Exchange: {snapshot.exchange}",
            f"Sector-level label: {snapshot.sector}",
            f"Industry: {snapshot.industry}",
            f"Source IDs: {', '.join(source_ids) if source_ids else 'None'}",
            "",
            "#### Price And Overview",
            f"- Latest price: {snapshot.latest_price}",
            f"- Daily change %: {snapshot.daily_change_pct}",
            f"- Market cap: {snapshot.market_cap}",
            f"- P/E ratio: {snapshot.pe_ratio}",
            "",
            "#### Technical Analysis",
            f"- Trend: {technical['trend']}",
            f"- Support: {technical['support']}",
            f"- Resistance: {technical['resistance']}",
            f"- Buy zone: {technical['buy_zone']}",
            f"- Take-profit zone: {technical['take_profit_zone']}",
            f"- Stop-loss area: {technical['stop_loss_area']}",
            f"- MA20: {technical['ma20']}",
            f"- MA50: {technical['ma50']}",
            f"- MA200: {technical['ma200']}",
            f"- RSI 14: {technical['rsi14']} ({technical['momentum']})",
            f"- MACD: {technical['macd']} / Signal: {technical['macd_signal']} ({technical['macd_interpretation']})",
            f"- Volume trend: {technical['volume_trend']}",
            "",
            "#### Fundamental Analysis",
            f"- Revenue growth: {fundamental['revenue_growth']}",
            f"- EPS growth: {fundamental['eps_growth']}",
            f"- Valuation view: {fundamental['valuation_view']}",
            f"- Fundamental score: {fundamental['fundamental_score']}",
            "",
            "#### News Sentiment And Risks",
            f"- News sentiment: {sentiment['label']} ({sentiment['score']}/100)",
            f"- Risk level: {report['risk_level']}",
            f"- Overall score: {score['overall_score']} / 100 = {score['label']}",
            f"- Action label: {self.responses._action(report)}",
            "",
        ]

    def _write_csv(self, path: Path, reports: list[dict]) -> None:
        fields = ["ticker", "company", "sector", "price", "daily_change_pct", "trend", "rsi14", "support", "resistance", "risk_level", "overall_score", "action"]
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for report in reports:
                snapshot = report["snapshot"]
                technical = report["technical"]
                writer.writerow(
                    {
                        "ticker": snapshot.ticker,
                        "company": snapshot.company_name,
                        "sector": snapshot.sector,
                        "price": snapshot.latest_price,
                        "daily_change_pct": snapshot.daily_change_pct,
                        "trend": technical["trend"],
                        "rsi14": technical["rsi14"],
                        "support": technical["support"],
                        "resistance": technical["resistance"],
                        "risk_level": report["risk_level"],
                        "overall_score": report["score"]["overall_score"],
                        "action": self.responses._action(report),
                    }
                )

    def _write_pdf(self, path: Path, date_text: str, reports: list[dict]) -> None:
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = [
            Paragraph(f"Daily Global Stock Briefing - {date_text}", styles["Title"]),
            Paragraph(DISCLAIMER, styles["BodyText"]),
            Spacer(1, 12),
            Paragraph(f"Market bias: {self._market_bias(reports)}", styles["Heading2"]),
            Paragraph(f"Top watchlist candidates: {', '.join(self._top_tickers(reports))}", styles["BodyText"]),
            Spacer(1, 12),
            self._summary_table(reports),
            PageBreak(),
        ]
        for report in reports:
            snapshot = report["snapshot"]
            technical = report["technical"]
            story.extend(
                [
                    Paragraph(f"{snapshot.ticker} - {snapshot.company_name}", styles["Heading1"]),
                    Paragraph(f"Sector: {snapshot.sector} | Risk: {report['risk_level']} | Score: {report['score']['overall_score']} | Action: {self.responses._action(report)}", styles["BodyText"]),
                    Paragraph(f"Price: {snapshot.latest_price} | Change: {snapshot.daily_change_pct}% | Trend: {technical['trend']}", styles["BodyText"]),
                    Paragraph(f"Support: {technical['support']} | Resistance: {technical['resistance']} | RSI14: {technical['rsi14']} | MACD: {technical['macd']}", styles["BodyText"]),
                    Spacer(1, 10),
                ]
            )
        doc.build(story)

    @staticmethod
    def _summary_table(reports: list[dict]) -> Table:
        data = [["Ticker", "Sector", "Trend", "Risk", "Score", "Action"]]
        service = ResponseGenerator()
        for report in reports:
            snapshot = report["snapshot"]
            data.append([snapshot.ticker, snapshot.sector, report["technical"]["trend"], report["risk_level"], str(report["score"]["overall_score"]), service._action(report)])
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        return table

    @staticmethod
    def _source_index(reports: list[dict]) -> list[tuple]:
        index = []
        counter = 1
        for report in reports:
            ticker = report["snapshot"].ticker
            for item in report["news"]:
                index.append((f"S{counter:03d}", item, ticker))
                counter += 1
        return index

    @staticmethod
    def _market_bias(reports: list[dict]) -> str:
        if not reports:
            return "Neutral"
        avg = sum(report["score"]["overall_score"] for report in reports) / len(reports)
        if avg >= 65:
            return "Neutral to Bullish"
        if avg < 45:
            return "Cautious"
        return "Neutral"

    @staticmethod
    def _top_tickers(reports: list[dict], count: int = 5) -> list[str]:
        return [report["snapshot"].ticker for report in sorted(reports, key=lambda item: item["score"]["overall_score"], reverse=True)[:count]]

    def _summary(self, reports: list[dict]) -> str:
        return f"Market bias: {self._market_bias(reports)} | Top watch: {', '.join(self._top_tickers(reports))}"
