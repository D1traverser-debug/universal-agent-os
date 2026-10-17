from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping, Protocol

from .persistent_assets import CrudOperation, PersistentAssetDescriptor


class ExecutionDisposition(StrEnum):
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class CapabilityHealth(StrEnum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


class CapabilityCostClass(StrEnum):
    INCLUDED = "INCLUDED"
    FREE = "FREE"
    PAID = "PAID"
    UNKNOWN = "UNKNOWN"


class CapabilityAvailability(StrEnum):
    SESSION = "SESSION"
    LOCAL = "LOCAL"
    BACKGROUND = "BACKGROUND"


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
    allow_paid: bool = False
    allow_unknown_cost: bool = False
    requires_background: bool = False
    target_authority: str | None = None
    governance_basis: str | None = None
    persistent_asset: PersistentAssetDescriptor | None = None
    persistent_operation: CrudOperation | None = None


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
    cost_class: CapabilityCostClass = CapabilityCostClass.FREE
    availability: CapabilityAvailability = CapabilityAvailability.SESSION


class Executor(Protocol):
    def execute(self, request: ExecutionRequest) -> ExecutionOutcome: ...


class Reconciler(Protocol):
    def reconcile(self, request: ExecutionRequest, unknown: ExecutionOutcome) -> ExecutionOutcome: ...
