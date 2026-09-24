"""Small SQLite store for per-server bot settings."""

import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).parent / "catgirl.sqlite3"


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize() -> None:
    with closing(_connect()) as connection, connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                welcome_channel_id INTEGER,
                welcome_message TEXT NOT NULL DEFAULT 'Welcome {mention} to {server}! You are member #{member_count}.',
                welcome_title TEXT NOT NULL DEFAULT 'Welcome to {server}!',
                welcome_color TEXT NOT NULL DEFAULT '#FF9ECF'
            )"""
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS feature_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                submitter TEXT NOT NULL,
                suggestion TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def get_guild_settings(guild_id: int) -> dict:
    with closing(_connect()) as connection, connection:
        row = connection.execute(
            "SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,)
        ).fetchone()
    return (
        dict(row)
        if row
        else {
            "guild_id": guild_id,
            "welcome_channel_id": None,
            "welcome_message": "Welcome {mention} to {server}! You are member #{member_count}.",
            "welcome_title": "Welcome to {server}!",
            "welcome_color": "#FF9ECF",
        }
    )


def update_guild_setting(guild_id: int, setting: str, value) -> None:
    allowed = {
        "welcome_channel_id",
        "welcome_message",
        "welcome_title",
        "welcome_color",
    }
    if setting not in allowed:
        raise ValueError(f"Unsupported setting: {setting}")
    with closing(_connect()) as connection, connection:
        connection.execute(
            "INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)", (guild_id,)
        )
        connection.execute(
            f"UPDATE guild_settings SET {setting} = ? WHERE guild_id = ?",
            (value, guild_id),
        )


def add_suggestion(guild_id: int, user_id: int, submitter: str, suggestion: str) -> int:
    with closing(_connect()) as connection, connection:
        cursor = connection.execute(
            """INSERT INTO feature_suggestions (guild_id, user_id, submitter, suggestion)
            VALUES (?, ?, ?, ?)""",
            (guild_id, user_id, submitter, suggestion),
        )
        return cursor.lastrowid


def count_suggestions(guild_id: int) -> int:
    with closing(_connect()) as connection, connection:
        row = connection.execute(
            "SELECT COUNT(*) AS total FROM feature_suggestions WHERE guild_id = ?",
            (guild_id,),
        ).fetchone()
    return row["total"]


def get_suggestions(guild_id: int, limit: int, offset: int) -> list[dict]:
    with closing(_connect()) as connection, connection:
        rows = connection.execute(
            """SELECT id, user_id, submitter, suggestion, created_at
            FROM feature_suggestions WHERE guild_id = ?
            ORDER BY id DESC LIMIT ? OFFSET ?""",
            (guild_id, limit, offset),
        ).fetchall()
    return [dict(row) for row in rows]
