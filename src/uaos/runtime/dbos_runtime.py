from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Callable

from .ports import RuntimeMessage, RuntimeWorkflowStatus, WorkflowRef, WorkflowSpec


class DBOSRuntime:
    """Adapter around DBOS public workflow-management APIs.

    DBOS remains behind the DurableRuntime boundary. Importing this module does
    not require DBOS; ``from_installed`` imports it only in a configured runtime.
    """

    def __init__(self, *, dbos_api: Any, set_workflow_id: Callable[..., AbstractContextManager[Any]]) -> None:
        self._dbos = dbos_api
        self._set_workflow_id = set_workflow_id

    @classmethod
    def from_installed(cls) -> "DBOSRuntime":
        from dbos import DBOS, SetWorkflowID
        return cls(dbos_api=DBOS, set_workflow_id=SetWorkflowID)

    def start(self, spec: WorkflowSpec) -> WorkflowRef:
        with self._set_workflow_id(spec.workflow_id):
            handle = self._dbos.start_workflow(spec.workflow, *spec.args, **dict(spec.kwargs))
        actual_id = handle.get_workflow_id()
        if actual_id != spec.workflow_id:
            raise RuntimeError(f"DBOS returned unexpected workflow id {actual_id!r}")
        return WorkflowRef(actual_id, self._map_status(handle.get_status()))

    def retrieve(self, workflow_id: str) -> WorkflowRef:
        handle = self._dbos.retrieve_workflow(workflow_id)
        return WorkflowRef(handle.get_workflow_id(), self._map_status(handle.get_status()))

    def resume(self, workflow_id: str) -> WorkflowRef:
        handle = self._dbos.resume_workflow(workflow_id)
        return WorkflowRef(handle.get_workflow_id(), self._map_status(handle.get_status()))

    def cancel(self, workflow_id: str) -> None:
        self._dbos.cancel_workflow(workflow_id)

    def send(self, message: RuntimeMessage) -> None:
        self._dbos.send(
            message.workflow_id,
            message.payload,
            message.topic,
            idempotency_key=message.idempotency_key,
        )

    def get_event(self, workflow_id: str, key: str, *, timeout_seconds: float = 0) -> Any:
        return self._dbos.get_event(workflow_id, key, timeout_seconds=timeout_seconds)

    @staticmethod
    def _map_status(status: Any) -> RuntimeWorkflowStatus:
        raw = getattr(status, "status", status)
        value = str(getattr(raw, "value", raw)).upper()
        mapping = {
            "PENDING": RuntimeWorkflowStatus.PENDING,
            "ENQUEUED": RuntimeWorkflowStatus.PENDING,
            "RUNNING": RuntimeWorkflowStatus.RUNNING,
            "CANCELLED": RuntimeWorkflowStatus.CANCELLED,
            "SUCCESS": RuntimeWorkflowStatus.COMPLETED,
            "COMPLETED": RuntimeWorkflowStatus.COMPLETED,
            "ERROR": RuntimeWorkflowStatus.FAILED,
            "FAILED": RuntimeWorkflowStatus.FAILED,
        }
        return mapping.get(value, RuntimeWorkflowStatus.UNKNOWN)
