from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping, Protocol

from .persistent_assets import (
    CrudOperation,
    MutationPersistence,
    PersistentAssetDescriptor,
)


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
    # Caller assertions only. Trusted semantics are derived from the selected
    # capability's mutation contract and PersistentAssetCatalog.
    mutation_persistence: MutationPersistence | str | None = None
    persistent_asset: PersistentAssetDescriptor | None = None
    persistent_operation: CrudOperation | str | None = None


@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    """Detached value object for executor/reconciler results.

    `frozen=True` protects only field assignment; without detaching mutable `output` or
    `evidence`, a caller holding the public result can otherwise mutate the same nested
    objects retained by a coordinator-owned UNKNOWN record. We therefore snapshot both
    fields at construction and return defensive copies on ordinary attribute access.
    This keeps UNKNOWN reconciliation truth detached from caller-owned mutable state.
    """

    disposition: ExecutionDisposition
    output: Any = None
    provider_ref: str | None = None
    evidence: Mapping[str, Any] = field(default_factory=dict)
    error: str | None = None

    def __post_init__(self) -> None:
        try:
            snap_output = deepcopy(object.__getattribute__(self, "output"))
            raw_evidence = object.__getattribute__(self, "evidence")
            snap_evidence = deepcopy(dict(raw_evidence))
        except Exception as exc:
            raise TypeError(
                "ExecutionOutcome output/evidence must support detached snapshot semantics"
            ) from exc
        object.__setattr__(self, "output", snap_output)
        object.__setattr__(self, "evidence", snap_evidence)

    def __getattribute__(self, name: str) -> Any:
        value = object.__getattribute__(self, name)
        if name in {"output", "evidence"}:
            try:
                return deepcopy(value)
            except Exception as exc:
                raise TypeError(
                    f"ExecutionOutcome.{name} must support defensive-copy access"
                ) from exc
        return value


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
