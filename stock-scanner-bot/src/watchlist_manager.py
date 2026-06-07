from __future__ import annotations

from src.database import Database


class WatchlistManager:
    def __init__(self, db: Database) -> None:
        self.db = db

    def add(self, line_user_id: str, ticker: str, company_name: str = "", sector: str = "") -> str:
        user_id = self.db.get_or_create_user(line_user_id)
        with self.db.connect() as conn:
            conn.execute(
                "insert or ignore into watchlists(user_id, ticker, company_name, sector) values (?, ?, ?, ?)",
                (user_id, ticker.upper(), company_name, sector),
            )
        return f"เพิ่ม {ticker.upper()} เข้า watchlist แล้วครับ"

    def remove(self, line_user_id: str, ticker: str) -> str:
        user_id = self.db.get_or_create_user(line_user_id)
        with self.db.connect() as conn:
            conn.execute("delete from watchlists where user_id = ? and ticker = ?", (user_id, ticker.upper()))
        return f"ลบ {ticker.upper()} จาก watchlist แล้วครับ"

    def summary(self, line_user_id: str) -> str:
        user_id = self.db.get_or_create_user(line_user_id)
        with self.db.connect() as conn:
            rows = conn.execute("select ticker, company_name, sector from watchlists where user_id = ? order by ticker", (user_id,)).fetchall()
        if not rows:
            return "watchlist ยังว่างอยู่ครับ ส่งข้อความเช่น เพิ่ม NVDA เพื่อเริ่มติดตามได้เลย"
        lines = ["Watchlist ของคุณ:"]
        for row in rows:
            label = f"{row['ticker']}"
            if row["company_name"]:
                label += f" - {row['company_name']}"
            if row["sector"]:
                label += f" ({row['sector']})"
            lines.append(f"- {label}")
        return "\n".join(lines)
