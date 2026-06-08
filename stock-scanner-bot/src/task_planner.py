from __future__ import annotations

from dataclasses import dataclass

from src.entity_extractor import ExtractedEntities


@dataclass
class Task:
    name: str
    status: str = "pending"
    error: str | None = None


@dataclass
class TaskPlan:
    tasks: list[Task]

    def mark(self, name: str, status: str, error: str | None = None) -> None:
        for task in self.tasks:
            if task.name == name:
                task.status = status
                task.error = error
                return


class TaskPlanner:
    def create_plan(self, intent: str, entities: ExtractedEntities) -> TaskPlan:
        tasks = ["Resolve entities", "Search sources", "Collect data", "Validate data", "Structure data"]
        if intent in {"technical_analysis", "stock_detail_scan", "peer_comparison", "sector_scan"}:
            tasks.append("Analyze technicals")
        if intent in {"fundamental_analysis", "stock_detail_scan", "peer_comparison", "sector_scan"}:
            tasks.append("Analyze fundamentals")
        if intent in {"news_scan", "stock_detail_scan", "peer_comparison", "sector_scan"}:
            tasks.append("Analyze news")
        tasks.extend(["Draft answer", "Self-review", "Final formatting", "Save NotebookLM source"])
        return TaskPlan([Task(name=task) for task in tasks])
