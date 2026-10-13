from __future__ import annotations

from dataclasses import replace
from threading import RLock
from typing import Any

from .ports import RuntimeMessage, RuntimeWorkflowStatus, WorkflowNotFound, WorkflowRef, WorkflowSpec, WorkflowStateError


class InMemoryDurableRuntime:
    """Reference state semantics, not a crash-durable production runtime."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowRef] = {}
        self._specs: dict[str, WorkflowSpec] = {}
        self._messages: dict[tuple[str, str | None], list[RuntimeMessage]] = {}
        self._message_keys: set[tuple[str, str]] = set()
        self._events: dict[tuple[str, str], Any] = {}
        self._lock = RLock()

    def start(self, spec: WorkflowSpec) -> WorkflowRef:
        with self._lock:
            existing = self._workflows.get(spec.workflow_id)
            if existing is not None:
                return existing
            ref = WorkflowRef(spec.workflow_id, RuntimeWorkflowStatus.PENDING)
            self._workflows[spec.workflow_id] = ref
            self._specs[spec.workflow_id] = spec
            return ref

    def retrieve(self, workflow_id: str) -> WorkflowRef:
        with self._lock:
            try:
                return self._workflows[workflow_id]
            except KeyError as exc:
                raise WorkflowNotFound(workflow_id) from exc

    def cancel(self, workflow_id: str) -> None:
        with self._lock:
            current = self.retrieve(workflow_id)
            if current.status is RuntimeWorkflowStatus.COMPLETED:
                raise WorkflowStateError("completed workflow cannot be cancelled")
            self._workflows[workflow_id] = replace(current, status=RuntimeWorkflowStatus.CANCELLED)

    def resume(self, workflow_id: str) -> WorkflowRef:
        with self._lock:
            current = self.retrieve(workflow_id)
            if current.status not in {
                RuntimeWorkflowStatus.CANCELLED,
                RuntimeWorkflowStatus.PAUSED,
                RuntimeWorkflowStatus.FAILED,
                RuntimeWorkflowStatus.PENDING,
            }:
                raise WorkflowStateError(f"workflow {workflow_id} cannot resume from {current.status}")
            resumed = replace(current, status=RuntimeWorkflowStatus.RUNNING)
            self._workflows[workflow_id] = resumed
            return resumed

    def mark_paused(self, workflow_id: str) -> WorkflowRef:
        with self._lock:
            current = self.retrieve(workflow_id)
            if current.status in {RuntimeWorkflowStatus.CANCELLED, RuntimeWorkflowStatus.COMPLETED}:
                raise WorkflowStateError(f"workflow {workflow_id} cannot pause from {current.status}")
            paused = replace(current, status=RuntimeWorkflowStatus.PAUSED)
            self._workflows[workflow_id] = paused
            return paused

    def mark_completed(self, workflow_id: str) -> WorkflowRef:
        with self._lock:
            current = self.retrieve(workflow_id)
            if current.status is RuntimeWorkflowStatus.CANCELLED:
                raise WorkflowStateError("cancelled workflow cannot complete without resume")
            completed = replace(current, status=RuntimeWorkflowStatus.COMPLETED)
            self._workflows[workflow_id] = completed
            return completed

    def send(self, message: RuntimeMessage) -> None:
        with self._lock:
            self.retrieve(message.workflow_id)
            if message.idempotency_key is not None:
                key = (message.workflow_id, message.idempotency_key)
                if key in self._message_keys:
                    return
                self._message_keys.add(key)
            bucket = self._messages.setdefault((message.workflow_id, message.topic), [])
            bucket.append(message)

    def recv(self, workflow_id: str, topic: str | None = None) -> RuntimeMessage | None:
        with self._lock:
            self.retrieve(workflow_id)
            bucket = self._messages.setdefault((workflow_id, topic), [])
            return bucket.pop(0) if bucket else None

    def set_event(self, workflow_id: str, key: str, value: Any) -> None:
        with self._lock:
            self.retrieve(workflow_id)
            self._events[(workflow_id, key)] = value

    def get_event(self, workflow_id: str, key: str, *, timeout_seconds: float = 0) -> Any:
        del timeout_seconds
        with self._lock:
            self.retrieve(workflow_id)
            return self._events.get((workflow_id, key))
