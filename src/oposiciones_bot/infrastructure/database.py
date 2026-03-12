import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass
class Database:
    path: str

    def __enter__(self) -> "Database":
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        self.init()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.cursor.close()
        self.connection.close()

    def init(self) -> None:
        with self.connection:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS explanations (
                    id INTEGER PRIMARY KEY,
                    explanation TEXT
                )
                """
            )

    def save_explanation(self, question_id: str, explanation: str) -> None:
        with self.connection:
            self.cursor.execute(
                "INSERT INTO explanations (id, explanation) VALUES (?, ?)",
                [question_id, explanation],
            )

    def get_explanation(self, question_id: str) -> str | None:
        with self.connection:
            self.cursor.execute(
                "SELECT explanation FROM explanations WHERE id = ?",
                [question_id],
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
