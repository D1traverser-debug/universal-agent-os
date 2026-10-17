from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum, StrEnum
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .persistent_assets import (
    CrudOperation,
    MutationPersistence,
    PersistentAssetDescriptor,
)


def _freeze_trusted_value(value: object) -> object:
    """Convert execution data into a recursively immutable, detached value domain.

    External/custom objects are rejected instead of trusting ``deepcopy`` or a frozen
    dataclass wrapper. Scalar subclasses are normalized to exact builtin values so they
    cannot smuggle mutable side state into retained execution truth.
    """

    if value is None:
        return None
    if isinstance(value, Enum):
        enum_type = type(value)
        if not enum_type.__module__.startswith("uaos."):
            raise TypeError(
                f"unsupported external enum in execution value: "
                f"{enum_type.__module__}.{enum_type.__qualname__}"
            )
        return value

    value_type = type(value)
    if value_type is bool:
        return value
    if value_type is int:
        return value
    if value_type is float:
        return value
    if value_type is str:
        return value
    if value_type is bytes:
        return value

    # Normalize subclasses to exact immutable builtin values. Do this after Enum so
    # UAOS StrEnum/IntEnum instances retain their semantic type.
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return float(value)
    if isinstance(value, str):
        return str(value)
    if isinstance(value, bytes):
        return bytes(value)
    if isinstance(value, bytearray):
        return bytes(value)

    if is_dataclass(value):
        dataclass_type = type(value)
        if not dataclass_type.__module__.startswith("uaos."):
            raise TypeError(
                f"unsupported external dataclass in execution value: "
                f"{dataclass_type.__module__}.{dataclass_type.__qualname__}"
            )
        frozen_fields = {
            item.name: _freeze_trusted_value(getattr(value, item.name))
            for item in fields(value)
        }
        try:
            return dataclass_type(**frozen_fields)
        except TypeError as exc:
            raise TypeError(
                f"execution dataclass cannot be structurally snapshotted: "
                f"{dataclass_type.__module__}.{dataclass_type.__qualname__}"
            ) from exc

    if isinstance(value, Mapping):
        frozen: dict[object, object] = {}
        for key, item in value.items():
            frozen_key = _freeze_trusted_value(key)
            frozen_value = _freeze_trusted_value(item)
            try:
                frozen[frozen_key] = frozen_value
            except TypeError as exc:
                raise TypeError("execution mapping key is not safely hashable") from exc
        return MappingProxyType(frozen)

    if isinstance(value, (tuple, list)):
        return tuple(_freeze_trusted_value(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze_trusted_value(item) for item in value)

    raise TypeError(
        f"unsupported execution value type: {value_type.__module__}.{value_type.__qualname__}"
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

    def __post_init__(self) -> None:
        # Construction itself establishes a detached value object. The coordinator
        # reconstructs requests again at its trust boundary, so even object.__setattr__
        # tampering on a caller-owned request cannot carry mutable subclasses/containers
        # into the retained execution record.
        for item in fields(self):
            object.__setattr__(self, item.name, _freeze_trusted_value(getattr(self, item.name)))


@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    """Structurally immutable result value for executor/reconciler boundaries.

    Only the trusted execution value domain is accepted. Arbitrary custom objects are
    rejected even if they claim to support ``deepcopy``; successful copying is not proof
    of detachment. Nested mappings/lists/sets are converted to immutable structures.
    """

    disposition: ExecutionDisposition
    output: Any = None
    provider_ref: str | None = None
    evidence: Mapping[str, Any] = field(default_factory=dict)
    error: str | None = None

    def __post_init__(self) -> None:
        try:
            frozen_output = _freeze_trusted_value(self.output)
            frozen_evidence = _freeze_trusted_value(self.evidence)
            frozen_provider_ref = _freeze_trusted_value(self.provider_ref)
            frozen_error = _freeze_trusted_value(self.error)
        except TypeError as exc:
            raise TypeError(
                "ExecutionOutcome output/evidence must use the trusted immutable value domain"
            ) from exc
        if not isinstance(frozen_evidence, Mapping):
            raise TypeError("ExecutionOutcome evidence must be a mapping")
        object.__setattr__(self, "output", frozen_output)
        object.__setattr__(self, "evidence", frozen_evidence)
        object.__setattr__(self, "provider_ref", frozen_provider_ref)
        object.__setattr__(self, "error", frozen_error)


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
