from __future__ import annotations

import re

from src.database import Database


class AlertManager:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create_from_text(self, line_user_id: str, ticker: str, text: str) -> str:
        target = self._extract_price(text)
        if target is None:
            return "ยังไม่พบราคาเป้าหมายครับ ลองพิมพ์เช่น แจ้งเตือนถ้า NVDA ลงถึง 120"
        condition = "below" if any(word in text.lower() for word in ["ลง", "below", "ต่ำ", "ถึง"]) else "above"
        user_id = self.db.get_or_create_user(line_user_id)
        with self.db.connect() as conn:
            conn.execute(
                "insert into price_alerts(user_id, ticker, target_price, condition, active) values (?, ?, ?, ?, 1)",
                (user_id, ticker.upper(), target, condition),
            )
        direction = "ลงถึง" if condition == "below" else "ทะลุ"
        return f"ตั้งแจ้งเตือน {ticker.upper()} เมื่อราคา{direction} {target} แล้วครับ"

    @staticmethod
    def _extract_price(text: str) -> float | None:
        numbers = re.findall(r"\d+(?:\.\d+)?", text)
        if not numbers:
            return None
        return float(numbers[-1])
