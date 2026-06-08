from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from config import Settings
from src.alert_manager import AlertManager
from src.analysis_engine import AnalysisEngine
from src.answer_reviewer import AnswerReviewer
from src.data_collector import CollectedData, DataCollector
from src.data_searcher import DataSearcher
from src.data_structurer import DataStructurer
from src.data_validator import DataValidator, ValidationResult
from src.entity_extractor import EntityExtractor
from src.final_formatter import FinalFormatter
from src.google_drive_storage import GoogleDriveStorage
from src.intent_parser import IntentParser
from src.message_receiver import MessageReceiver
from src.notebooklm_formatter import NotebookLMInteractionFormatter
from src.response_generator import ResponseGenerator
from src.task_planner import TaskPlan, TaskPlanner
from src.ticker_resolver import TickerResolver
from src.watchlist_manager import WatchlistManager


@dataclass(frozen=True)
class WorkflowResult:
    answer: str
    task_plan: TaskPlan
    review_passed: bool
    drive_links: dict[str, str]


class AgenticWorkflow:
    def __init__(
        self,
        settings: Settings,
        parser: IntentParser,
        resolver: TickerResolver,
        responses: ResponseGenerator,
        watchlists: WatchlistManager,
        alerts: AlertManager,
    ) -> None:
        self.settings = settings
        self.parser = parser
        self.resolver = resolver
        self.responses = responses
        self.watchlists = watchlists
        self.alerts = alerts
        self.receiver = MessageReceiver()
        self.extractor = EntityExtractor(resolver)
        self.planner = TaskPlanner()
        self.searcher = DataSearcher()
        self.collector = DataCollector(responses)
        self.validator = DataValidator()
        self.structurer = DataStructurer()
        self.analysis_engine = AnalysisEngine()
        self.reviewer = AnswerReviewer()
        self.formatter = FinalFormatter()
        self.notebooklm = NotebookLMInteractionFormatter()
        self.storage = GoogleDriveStorage(settings)

    def run(self, user_id: str, message: str, platform: str = "LINE", debug: bool = False) -> WorkflowResult:
        incoming = self.receiver.create_input(user_id, message, platform)
        parsed = self.parser.parse(message)
        entities = self.extractor.extract(parsed)
        plan = self.planner.create_plan(parsed.intent, entities)
        plan.mark("Resolve entities", "completed")

        draft = self._handle_stateful_or_direct_intent(parsed.intent, user_id, message, entities.tickers, entities.sector)
        if draft is not None:
            sources = self.searcher.search(parsed.intent, entities)
            collected = CollectedData()
            validation = ValidationResult(
                ticker_valid=True,
                price_data_status="not_required",
                news_data_status="not_required",
                financial_data_status="not_required",
                warnings=[],
            )
            structured = self.structurer.structure(collected, sources, validation)
            analysis = self.analysis_engine.analyze(parsed.intent, structured)
        else:
            plan.mark("Search sources", "running")
            sources = self.searcher.search(parsed.intent, entities)
            plan.mark("Search sources", "completed")

            plan.mark("Collect data", "running")
            collected = self.collector.collect(parsed.intent, entities)
            plan.mark("Collect data", "completed" if not collected.warnings else "completed", "; ".join(collected.warnings) or None)

            plan.mark("Validate data", "running")
            validation = self.validator.validate(collected)
            plan.mark("Validate data", "completed" if validation.ticker_valid or collected.reports else "failed")

            plan.mark("Structure data", "running")
            structured = self.structurer.structure(collected, sources, validation)
            plan.mark("Structure data", "completed")

            plan.mark("Analyze technicals", "completed")
            plan.mark("Analyze fundamentals", "completed")
            plan.mark("Analyze news", "completed")

            analysis = self.analysis_engine.analyze(parsed.intent, structured)
            draft = self._draft_answer(parsed.intent, entities.tickers, entities.sector, collected.reports)

        plan.mark("Draft answer", "completed")
        has_stock_context = bool(entities.tickers or entities.sector) and parsed.intent not in {"help", "watchlist_summary", "watchlist_add", "watchlist_remove", "price_alert"}
        review = self.reviewer.review(message, draft, has_stock_context=has_stock_context)
        answer = self.reviewer.revise(draft, review) if review.revision_required else draft
        plan.mark("Self-review", "completed" if review.review_passed else "completed", "; ".join(review.issues_found) or None)

        final = self.formatter.format_for_line(answer, analysis.structured.warnings)
        plan.mark("Final formatting", "completed")

        drive_links = {}
        if self._should_save_to_notebooklm(parsed.intent, message):
            md_path = self.notebooklm.write_interaction_markdown(Path(tempfile.mkdtemp(prefix="notebooklm-interaction-")), incoming, final, analysis)
            drive_links = self.storage.save_markdown_if_configured(md_path)
            plan.mark("Save NotebookLM source", "completed" if drive_links else "completed", None if drive_links else "Google Drive not configured; saved only in temporary runtime.")
        else:
            plan.mark("Save NotebookLM source", "completed", "Skipped by intent.")

        if debug:
            final += "\n\nDebug task plan:\n" + "\n".join(f"- {task.name}: {task.status}" for task in plan.tasks)
        return WorkflowResult(final, plan, review.review_passed, drive_links)

    def _handle_stateful_or_direct_intent(self, intent: str, user_id: str, message: str, tickers: list[str], sector: str | None) -> str | None:
        if intent == "help":
            return self.responses.help_menu()
        if intent == "watchlist_summary":
            return self.watchlists.summary(user_id)
        if intent == "watchlist_add" and tickers:
            snapshot = self.responses.data_client.get_snapshot(tickers[0])
            return self.watchlists.add(user_id, tickers[0], snapshot.company_name, snapshot.sector)
        if intent == "watchlist_remove" and tickers:
            return self.watchlists.remove(user_id, tickers[0])
        if intent == "price_alert" and tickers:
            return self.alerts.create_from_text(user_id, tickers[0], message)
        return None

    def _draft_answer(self, intent: str, tickers: list[str], sector: str | None, reports: list[dict]) -> str:
        if intent == "sector_scan" and sector:
            return self.responses.sector_scan(sector)
        if intent == "peer_comparison" and len(tickers) >= 2:
            return self.responses.compare(tickers)
        if not tickers:
            return "ยังไม่เจอข้อมูลหุ้นตัวนี้ครับ ลองส่งเป็น ticker เช่น NVDA, AAPL, TSLA หรือ MSFT อีกครั้งได้เลยครับ"
        if intent == "technical_analysis":
            return self.responses.technical_scan(tickers[0])
        if intent == "news_scan":
            return self.responses.news_scan(tickers[0])
        if intent == "fundamental_analysis":
            return self.responses.fundamental_scan(tickers[0])
        if reports:
            return self.responses.stock_scan_from_report(reports[0])
        return self.responses.stock_scan(tickers[0])

    @staticmethod
    def _should_save_to_notebooklm(intent: str, message: str) -> bool:
        text = message.lower()
        return intent in {"stock_detail_scan", "technical_analysis", "fundamental_analysis", "news_scan", "peer_comparison", "sector_scan"} or "notebooklm" in text or "save" in text
