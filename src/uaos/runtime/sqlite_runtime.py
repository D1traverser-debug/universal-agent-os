from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .ports import (
    RuntimeMessage,
    RuntimeWorkflowStatus,
    WorkflowNotFound,
    WorkflowRef,
    WorkflowSpec,
    WorkflowStateError,
)


class SQLiteCheckpointRuntime:
    """Zero-cost local durable control runtime.

    Workflow identity, lifecycle state, control messages and events survive process
    restarts. Execution resumes at UAOS WorkUnit/checkpoint boundaries; this adapter
    deliberately does not attempt transparent Python call-stack replay.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
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
                CREATE TABLE IF NOT EXISTS uaos_local_workflow (
                    workflow_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    application_version TEXT,
                    attributes TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS uaos_local_message (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL UNIQUE,
                    workflow_id TEXT NOT NULL,
                    topic TEXT,
                    idempotency_key TEXT,
                    payload TEXT NOT NULL,
                    consumed INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(workflow_id) REFERENCES uaos_local_workflow(workflow_id)
                )
                """
            )
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS uaos_local_message_idem "
                "ON uaos_local_message(workflow_id, idempotency_key) "
                "WHERE idempotency_key IS NOT NULL"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS uaos_local_event (
                    workflow_id TEXT NOT NULL,
                    event_key TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY(workflow_id, event_key),
                    FOREIGN KEY(workflow_id) REFERENCES uaos_local_workflow(workflow_id)
                )
                """
            )

    def start(self, spec: WorkflowSpec) -> WorkflowRef:
        attributes = json.dumps(dict(spec.attributes), separators=(",", ":"), ensure_ascii=False)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT status FROM uaos_local_workflow WHERE workflow_id = ?",
                (spec.workflow_id,),
            ).fetchone()
            if row is None:
                connection.execute(
                    "INSERT INTO uaos_local_workflow "
                    "(workflow_id, status, application_version, attributes) VALUES (?, ?, ?, ?)",
                    (
                        spec.workflow_id,
                        RuntimeWorkflowStatus.PENDING.value,
                        spec.application_version,
                        attributes,
                    ),
                )
                status = RuntimeWorkflowStatus.PENDING
            else:
                status = RuntimeWorkflowStatus(row[0])
            connection.commit()
        return WorkflowRef(spec.workflow_id, status)

    def retrieve(self, workflow_id: str) -> WorkflowRef:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT status FROM uaos_local_workflow WHERE workflow_id = ?",
                (workflow_id,),
            ).fetchone()
        if row is None:
            raise WorkflowNotFound(workflow_id)
        return WorkflowRef(workflow_id, RuntimeWorkflowStatus(row[0]))

    def _set_status(self, workflow_id: str, status: RuntimeWorkflowStatus) -> WorkflowRef:
        self.retrieve(workflow_id)
        with self._connect() as connection:
            connection.execute(
                "UPDATE uaos_local_workflow SET status = ? WHERE workflow_id = ?",
                (status.value, workflow_id),
            )
        return WorkflowRef(workflow_id, status)

    def resume(self, workflow_id: str) -> WorkflowRef:
        current = self.retrieve(workflow_id)
        if current.status not in {
            RuntimeWorkflowStatus.CANCELLED,
            RuntimeWorkflowStatus.PAUSED,
            RuntimeWorkflowStatus.FAILED,
            RuntimeWorkflowStatus.PENDING,
        }:
            raise WorkflowStateError(
                f"workflow {workflow_id} cannot resume from {current.status}"
            )
        return self._set_status(workflow_id, RuntimeWorkflowStatus.RUNNING)

    def cancel(self, workflow_id: str) -> None:
        current = self.retrieve(workflow_id)
        if current.status is RuntimeWorkflowStatus.COMPLETED:
            raise WorkflowStateError("completed workflow cannot be cancelled")
        self._set_status(workflow_id, RuntimeWorkflowStatus.CANCELLED)

    def mark_paused(self, workflow_id: str) -> WorkflowRef:
        return self._set_status(workflow_id, RuntimeWorkflowStatus.PAUSED)

    def mark_completed(self, workflow_id: str) -> WorkflowRef:
        return self._set_status(workflow_id, RuntimeWorkflowStatus.COMPLETED)

    def mark_failed(self, workflow_id: str) -> WorkflowRef:
        return self._set_status(workflow_id, RuntimeWorkflowStatus.FAILED)

    def send(self, message: RuntimeMessage) -> None:
        self.retrieve(message.workflow_id)
        payload = json.dumps(message.payload, separators=(",", ":"), ensure_ascii=False)
        with self._connect() as connection:
            try:
                connection.execute(
                    "INSERT INTO uaos_local_message "
                    "(message_id, workflow_id, topic, idempotency_key, payload) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        message.message_id,
                        message.workflow_id,
                        message.topic,
                        message.idempotency_key,
                        payload,
                    ),
                )
            except sqlite3.IntegrityError:
                if message.idempotency_key is not None:
                    return
                raise

    def recv(self, workflow_id: str, topic: str | None = None) -> RuntimeMessage | None:
        self.retrieve(workflow_id)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if topic is None:
                row = connection.execute(
                    "SELECT sequence, message_id, payload, topic, idempotency_key "
                    "FROM uaos_local_message WHERE workflow_id = ? AND consumed = 0 "
                    "ORDER BY sequence LIMIT 1",
                    (workflow_id,),
                ).fetchone()
            else:
                row = connection.execute(
                    "SELECT sequence, message_id, payload, topic, idempotency_key "
                    "FROM uaos_local_message "
                    "WHERE workflow_id = ? AND topic = ? AND consumed = 0 "
                    "ORDER BY sequence LIMIT 1",
                    (workflow_id, topic),
                ).fetchone()
            if row is None:
                connection.rollback()
                return None
            connection.execute(
                "UPDATE uaos_local_message SET consumed = 1 WHERE sequence = ?",
                (row[0],),
            )
            connection.commit()
        return RuntimeMessage(row[1], workflow_id, json.loads(row[2]), row[3], row[4])

    def set_event(self, workflow_id: str, key: str, value: Any) -> None:
        self.retrieve(workflow_id)
        payload = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO uaos_local_event(workflow_id, event_key, payload) "
                "VALUES (?, ?, ?) "
                "ON CONFLICT(workflow_id, event_key) DO UPDATE SET payload = excluded.payload",
                (workflow_id, key, payload),
            )

    def get_event(self, workflow_id: str, key: str, *, timeout_seconds: float = 0) -> Any:
        del timeout_seconds
        self.retrieve(workflow_id)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM uaos_local_event "
                "WHERE workflow_id = ? AND event_key = ?",
                (workflow_id, key),
            ).fetchone()
        return None if row is None else json.loads(row[0])
