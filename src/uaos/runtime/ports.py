from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Mapping, Protocol

WorkflowCallable = Callable[..., Any]


class RuntimeWorkflowStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class ControlTopic(StrEnum):
    REQUIREMENT_UPDATE = "requirement_update"
    PAUSE = "pause"
    CANCEL = "cancel"
    APPROVAL = "approval"


class WorkflowNotFound(KeyError):
    pass


class WorkflowStateError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class WorkflowRef:
    workflow_id: str
    status: RuntimeWorkflowStatus = RuntimeWorkflowStatus.PENDING


@dataclass(frozen=True, slots=True)
class RuntimeMessage:
    message_id: str
    workflow_id: str
    payload: Any
    topic: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowSpec:
    workflow_id: str
    workflow: WorkflowCallable
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    application_version: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)


class DurableRuntime(Protocol):
    def start(self, spec: WorkflowSpec) -> WorkflowRef: ...
    def retrieve(self, workflow_id: str) -> WorkflowRef: ...
    def resume(self, workflow_id: str) -> WorkflowRef: ...
    def cancel(self, workflow_id: str) -> None: ...
    def send(self, message: RuntimeMessage) -> None: ...
    def get_event(self, workflow_id: str, key: str, *, timeout_seconds: float = 0) -> Any: ...
