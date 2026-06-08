from __future__ import annotations


class FinalFormatter:
    def format_for_line(self, answer: str, warnings: list[str] | None = None) -> str:
        if not warnings:
            return answer
        warning_text = "\n".join(f"- {warning}" for warning in warnings[:5])
        return f"{answer}\n\nData limitations:\n{warning_text}"
