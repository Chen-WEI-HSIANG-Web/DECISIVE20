from __future__ import annotations

"""Persistence for live game sessions.

A whole :class:`GameSession` is pure data (the rule functions live at module
level, not on the instance), so it pickles cleanly — including the seeded
``random.Random`` state, which is what keeps a reloaded game deterministic.

Two interchangeable backends:

* :class:`MemoryGameStore` — process-local dict, used by tests and ephemeral runs.
* :class:`SqliteGameStore` — file-backed, survives a server restart with no
  external service. Each blob is a pickled session keyed by game id.

The blobs are produced and consumed only by this application and stored
locally, so pickle's trust caveat does not apply here.
"""

import pickle
import sqlite3
import threading
from pathlib import Path
from typing import Protocol, Union

from decisive20.session import GameSession


class GameStore(Protocol):
    def save(self, game_id: str, session: GameSession) -> None: ...
    def load(self, game_id: str) -> GameSession | None: ...
    def delete(self, game_id: str) -> None: ...
    def count(self) -> int: ...


class MemoryGameStore:
    """In-memory store; state is lost when the process exits."""

    def __init__(self) -> None:
        self._games: dict[str, GameSession] = {}

    def save(self, game_id: str, session: GameSession) -> None:
        self._games[game_id] = session

    def load(self, game_id: str) -> GameSession | None:
        return self._games.get(game_id)

    def delete(self, game_id: str) -> None:
        self._games.pop(game_id, None)

    def count(self) -> int:
        return len(self._games)


class SqliteGameStore:
    """File-backed store. Pickled sessions survive a restart."""

    def __init__(self, path: Union[str, Path]) -> None:
        self._path = str(path)
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        # A fresh connection per operation keeps this safe across FastAPI's
        # threadpool without sharing a connection between threads.
        return sqlite3.connect(self._path)

    def _execute(self, sql: str, params: tuple = (), *, fetch: bool = False):
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute(sql, params)
                result = cur.fetchone() if fetch else None
                conn.commit()
                return result
            finally:
                conn.close()

    def _init_db(self) -> None:
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id         TEXT PRIMARY KEY,
                blob       BLOB NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )

    def save(self, game_id: str, session: GameSession) -> None:
        blob = pickle.dumps(session, protocol=pickle.HIGHEST_PROTOCOL)
        self._execute(
            """
            INSERT INTO games (id, blob, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                blob = excluded.blob,
                updated_at = excluded.updated_at
            """,
            (game_id, blob),
        )

    def load(self, game_id: str) -> GameSession | None:
        row = self._execute("SELECT blob FROM games WHERE id = ?", (game_id,), fetch=True)
        if row is None:
            return None
        return pickle.loads(row[0])

    def delete(self, game_id: str) -> None:
        self._execute("DELETE FROM games WHERE id = ?", (game_id,))

    def count(self) -> int:
        row = self._execute("SELECT COUNT(*) FROM games", fetch=True)
        return int(row[0]) if row else 0
