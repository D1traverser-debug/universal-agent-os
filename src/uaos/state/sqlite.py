from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Generic, Mapping, TypeVar

from .ledger import LedgerEvent
from .ports import NotFound, VersionConflict, Versioned

T = TypeVar("T")


class SQLiteVersionedRepository(Generic[T]):
    """Zero-cost local authoritative CAS repository using Python stdlib SQLite."""

    def __init__(
        self,
        path: str | Path,
        namespace: str,
        *,
        encode: Callable[[T], str] | None = None,
        decode: Callable[[str], T] | None = None,
    ) -> None:
        if not namespace.strip():
            raise ValueError("namespace is required")
        self.path = str(path)
        self.namespace = namespace
        self._encode = encode or (
            lambda value: json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        )
        self._decode = decode or json.loads
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS uaos_versioned_object (
                    namespace TEXT NOT NULL,
                    object_id TEXT NOT NULL,
                    version INTEGER NOT NULL CHECK (version >= 1),
                    payload TEXT NOT NULL,
                    PRIMARY KEY (namespace, object_id)
                )
                """
            )

    def get(self, object_id: str) -> Versioned[T]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT version, payload FROM uaos_versioned_object "
                "WHERE namespace = ? AND object_id = ?",
                (self.namespace, object_id),
            ).fetchone()
        if row is None:
            raise NotFound(object_id)
        return Versioned(self._decode(row[1]), int(row[0]))

    def create(self, object_id: str, value: T) -> Versioned[T]:
        payload = self._encode(value)
        try:
            with self._connect() as connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    "INSERT INTO uaos_versioned_object "
                    "(namespace, object_id, version, payload) VALUES (?, ?, 1, ?)",
                    (self.namespace, object_id, payload),
                )
                connection.commit()
        except sqlite3.IntegrityError as exc:
            raise VersionConflict(f"{object_id} already exists") from exc
        return Versioned(value, 1)

    def compare_and_set(
        self, object_id: str, expected_version: int, value: T
    ) -> Versioned[T]:
        payload = self._encode(value)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT version FROM uaos_versioned_object "
                "WHERE namespace = ? AND object_id = ?",
                (self.namespace, object_id),
            ).fetchone()
            if row is None:
                connection.rollback()
                raise NotFound(object_id)
            current = int(row[0])
            if current != expected_version:
                connection.rollback()
                raise VersionConflict(
                    f"stale version for {object_id}: "
                    f"expected {expected_version}, current {current}"
                )
            new_version = current + 1
            cursor = connection.execute(
                "UPDATE uaos_versioned_object SET version = ?, payload = ? "
                "WHERE namespace = ? AND object_id = ? AND version = ?",
                (new_version, payload, self.namespace, object_id, current),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                raise VersionConflict(f"concurrent update for {object_id}")
            connection.commit()
        return Versioned(value, new_version)


class SQLiteAppendOnlyLedger:
    """Append-only local event ledger sharing the same zero-cost SQLite backend."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS uaos_ledger (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    aggregate_type TEXT NOT NULL,
                    aggregate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    occurred_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS uaos_ledger_aggregate_idx "
                "ON uaos_ledger(aggregate_type, aggregate_id, sequence)"
            )

    def append(
        self,
        *,
        event_id: str,
        aggregate_type: str,
        aggregate_id: str,
        event_type: str,
        payload: Mapping[str, object],
        occurred_at: datetime | None = None,
    ) -> LedgerEvent:
        event_time = occurred_at or datetime.now(UTC)
        raw_payload = json.dumps(dict(payload), separators=(",", ":"), ensure_ascii=False)
        try:
            with self._connect() as connection:
                connection.execute("BEGIN IMMEDIATE")
                cursor = connection.execute(
                    "INSERT INTO uaos_ledger "
                    "(event_id, aggregate_type, aggregate_id, event_type, payload, occurred_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        event_id,
                        aggregate_type,
                        aggregate_id,
                        event_type,
                        raw_payload,
                        event_time.isoformat(),
                    ),
                )
                sequence = int(cursor.lastrowid)
                connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"duplicate event_id: {event_id}") from exc
        return LedgerEvent(
            sequence,
            event_id,
            aggregate_type,
            aggregate_id,
            event_type,
            dict(payload),
            event_time,
        )

    def events_for(self, aggregate_type: str, aggregate_id: str) -> tuple[LedgerEvent, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT sequence, event_id, event_type, payload, occurred_at "
                "FROM uaos_ledger WHERE aggregate_type = ? AND aggregate_id = ? "
                "ORDER BY sequence",
                (aggregate_type, aggregate_id),
            ).fetchall()
        return tuple(
            LedgerEvent(
                int(sequence),
                event_id,
                aggregate_type,
                aggregate_id,
                event_type,
                json.loads(payload),
                datetime.fromisoformat(occurred_at),
            )
            for sequence, event_id, event_type, payload, occurred_at in rows
        )

    def all(self) -> tuple[LedgerEvent, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT sequence, event_id, aggregate_type, aggregate_id, "
                "event_type, payload, occurred_at FROM uaos_ledger ORDER BY sequence"
            ).fetchall()
        return tuple(
            LedgerEvent(
                int(sequence),
                event_id,
                aggregate_type,
                aggregate_id,
                event_type,
                json.loads(payload),
                datetime.fromisoformat(occurred_at),
            )
            for sequence, event_id, aggregate_type, aggregate_id, event_type, payload, occurred_at in rows
        )
