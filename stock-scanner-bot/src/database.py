from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    def __init__(self, database_url: str) -> None:
        if not database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// DATABASE_URL is supported by the built-in database adapter.")
        self.path = Path(database_url.replace("sqlite:///", ""))
        if not self.path.is_absolute():
            self.path = Path.cwd() / self.path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                create table if not exists users (
                    id integer primary key autoincrement,
                    line_user_id text unique not null,
                    created_at text default current_timestamp
                );

                create table if not exists watchlists (
                    id integer primary key autoincrement,
                    user_id integer not null,
                    ticker text not null,
                    company_name text,
                    sector text,
                    created_at text default current_timestamp,
                    unique(user_id, ticker),
                    foreign key(user_id) references users(id)
                );

                create table if not exists price_alerts (
                    id integer primary key autoincrement,
                    user_id integer not null,
                    ticker text not null,
                    target_price real not null,
                    condition text not null,
                    active integer default 1,
                    created_at text default current_timestamp,
                    foreign key(user_id) references users(id)
                );
                """
            )

    def get_or_create_user(self, line_user_id: str) -> int:
        with self.connect() as conn:
            conn.execute("insert or ignore into users(line_user_id) values (?)", (line_user_id,))
            row = conn.execute("select id from users where line_user_id = ?", (line_user_id,)).fetchone()
            return int(row["id"])
