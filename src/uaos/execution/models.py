from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping, Protocol


class ExecutionDisposition(StrEnum):
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class CapabilityHealth(StrEnum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    action_id: str
    action_name: str
    target: str
    payload: Any
    required_permissions: tuple[str, ...] = ()
    required_capability_id: str | None = None
    parameter_hash: str = ""
    side_effect_class: str = "READ"
    idempotency_key: str | None = None
    approval_required: bool = False
    quality_floor: float = 0.0
    cost_ceiling: float | None = None


@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    disposition: ExecutionDisposition
    output: Any = None
    provider_ref: str | None = None
    evidence: Mapping[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass(frozen=True, slots=True)
class CapabilityObservation:
    capability_id: str
    health: CapabilityHealth
    observed_at_epoch: float
    supported_actions: tuple[str, ...]
    permissions: tuple[str, ...] = ()
    quality_score: float = 0.0
    estimated_cost: float = 0.0
    executor_kind: str = ""
    expires_at_epoch: float | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


class Executor(Protocol):
    def execute(self, request: ExecutionRequest) -> ExecutionOutcome: ...


class Reconciler(Protocol):
    def reconcile(self, request: ExecutionRequest, unknown: ExecutionOutcome) -> ExecutionOutcome: ...
