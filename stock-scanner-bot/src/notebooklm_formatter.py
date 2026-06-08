from __future__ import annotations

import datetime as dt
from pathlib import Path

from src.analysis_engine import AnalysisResult
from src.message_receiver import IncomingMessage


class NotebookLMInteractionFormatter:
    def write_interaction_markdown(self, output_dir: Path, incoming: IncomingMessage, answer: str, analysis: AnalysisResult) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_time = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        ticker_label = "-".join(report["snapshot"].ticker for report in analysis.structured.reports) or "general"
        path = output_dir / f"NotebookLM_Interaction_{safe_time}_{ticker_label}.md"
        lines = [
            f"# Bot Interaction Source - {safe_time}",
            "",
            f"## User",
            f"- User ID: {incoming.user_id}",
            f"- Platform: {incoming.platform}",
            f"- Timestamp: {incoming.timestamp}",
            "",
            "## User Question",
            incoming.message,
            "",
            "## Parsed / Analysis Summary",
            f"- Intent: {analysis.intent}",
            f"- Risk level: {analysis.risk_level}",
            f"- Action label: {analysis.action_label}",
            "",
            "## Final Answer",
            answer,
            "",
            "## Source Index",
        ]
        for index, source in enumerate(analysis.structured.sources, start=1):
            lines.append(f"- S{index:03d} | {source.source_name} | {source.source_type} | {source.url} | retrieved_at={source.retrieved_at}")
        path.write_text("\n".join(lines), encoding="utf-8")
        return path
