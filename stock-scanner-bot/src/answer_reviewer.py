from __future__ import annotations

from dataclasses import dataclass, field

from src.response_generator import DISCLAIMER


@dataclass(frozen=True)
class ReviewResult:
    review_passed: bool
    issues_found: list[str] = field(default_factory=list)
    final_response_ready: bool = False
    revision_required: bool = False


class AnswerReviewer:
    RISK_WORDS = ["Risk", "risk", "ความเสี่ยง", "Risk Level"]
    OVERCONFIDENT_PHRASES = ["guaranteed profit", "แน่นอน 100%", "รับประกันกำไร", "ไม่มีความเสี่ยง"]

    def review(self, user_message: str, draft_answer: str, has_stock_context: bool = True) -> ReviewResult:
        issues = []
        if has_stock_context and not any(word in draft_answer for word in self.RISK_WORDS):
            issues.append("Missing risk section")
        if DISCLAIMER not in draft_answer and "Disclaimer" not in draft_answer:
            issues.append("Missing disclaimer")
        if any(phrase in draft_answer for phrase in self.OVERCONFIDENT_PHRASES):
            issues.append("Overconfident investment wording")
        if not draft_answer.strip():
            issues.append("Empty response")
        passed = not issues
        return ReviewResult(passed, issues, passed, not passed)

    def revise(self, draft_answer: str, review: ReviewResult) -> str:
        revised = draft_answer.strip()
        if "Missing risk section" in review.issues_found:
            revised += "\n\nRisk:\n- ข้อมูลบางส่วนอาจไม่ครบถ้วน และราคาตลาดเปลี่ยนแปลงได้ตลอดเวลา"
        if "Missing disclaimer" in review.issues_found:
            revised += f"\n\nDisclaimer: {DISCLAIMER}"
        if "Overconfident investment wording" in review.issues_found:
            revised += "\n\nหมายเหตุเพิ่มเติม: มุมมองนี้เป็น scenario analysis ไม่ใช่การรับประกันผลลัพธ์"
        return revised
