from config import Settings
from src.agentic_workflow import AgenticWorkflow
from src.alert_manager import AlertManager
from src.database import Database
from src.intent_parser import IntentParser
from src.response_generator import ResponseGenerator
from src.stock_data import StockDataClient
from src.ticker_resolver import TickerResolver
from src.watchlist_manager import WatchlistManager


def test_workflow_help_command_returns_menu(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}")
    db = Database(settings.database_url)
    workflow = AgenticWorkflow(
        settings,
        IntentParser(),
        TickerResolver(),
        ResponseGenerator(StockDataClient()),
        WatchlistManager(db),
        AlertManager(db),
    )
    result = workflow.run("user-1", "help")
    assert "NVDA" in result.answer
    assert result.review_passed
    assert any(task.name == "Self-review" and task.status == "completed" for task in result.task_plan.tasks)
