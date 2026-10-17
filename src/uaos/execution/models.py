from __future__ import annotations

from dataclasses import dataclass, field, fields
from enum import Enum, StrEnum
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .persistent_assets import (
    AssetLifecycle,
    AssetRole,
    CrudOperation,
    MutationPersistence,
    PersistentAssetDescriptor,
    PersistentSurface,
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


_ALLOWED_EXECUTION_ENUM_TYPES = {
    ExecutionDisposition,
    CapabilityHealth,
    CapabilityCostClass,
    CapabilityAvailability,
    CrudOperation,
    MutationPersistence,
    PersistentSurface,
    AssetRole,
    AssetLifecycle,
}


def _freeze_trusted_value(value: object) -> object:
    """Convert execution data into a detached immutable value domain.

    Enum objects are never retained because Python Enum members are process singletons and
    may carry mutable auxiliary attributes even when their semantic value is immutable.
    Known UAOS enums are encoded as an immutable semantic tuple; unknown/custom enums are
    rejected rather than trusted by module/name convention. Arbitrary dataclasses and
    custom objects are also rejected.
    """

    if value is None:
        return None

    if isinstance(value, Enum):
        enum_type = type(value)
        if enum_type not in _ALLOWED_EXECUTION_ENUM_TYPES:
            raise TypeError(
                f"unsupported enum in execution value: "
                f"{enum_type.__module__}.{enum_type.__qualname__}"
            )
        return (
            "__uaos_enum__",
            f"{enum_type.__module__}.{enum_type.__qualname__}",
            _freeze_trusted_value(value.value),
        )

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

    # Normalize scalar subclasses to exact immutable builtins. Their auxiliary mutable
    # attributes are intentionally discarded.
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


def _normalize_enum_assertion(
    value: object,
    enum_type: type[StrEnum],
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None
    if type(value) is enum_type:
        return str(value.value)
    if isinstance(value, str):
        try:
            return str(enum_type(str(value)).value)
        except (TypeError, ValueError) as exc:
            raise TypeError(f"invalid {field_name}: {value!r}") from exc
    raise TypeError(f"invalid {field_name}: {value!r}")


def _persistent_asset_assertion(
    value: PersistentAssetDescriptor | Mapping[str, Any] | None,
) -> Mapping[str, object] | None:
    """Return a primitive detached assertion; never retain descriptor Enum singletons."""

    if value is None:
        return None
    if isinstance(value, Mapping) and not isinstance(value, PersistentAssetDescriptor):
        required = {
            "asset_id",
            "resource_ref",
            "surface",
            "role",
            "lifecycle",
            "owner_authority",
            "allowed_operations",
            "canonical_authority_ref",
            "migration_target_ref",
        }
        if set(value.keys()) != required:
            raise TypeError("persistent asset assertion mapping has unexpected fields")
        frozen = _freeze_trusted_value(value)
        if not isinstance(frozen, Mapping):
            raise TypeError("persistent asset assertion must freeze to a mapping")
        return frozen
    if type(value) is not PersistentAssetDescriptor:
        raise TypeError("persistent_asset assertion must use PersistentAssetDescriptor")
    return MappingProxyType(
        {
            "asset_id": str(value.asset_id),
            "resource_ref": str(value.resource_ref),
            "surface": str(value.surface.value),
            "role": str(value.role.value),
            "lifecycle": str(value.lifecycle.value),
            "owner_authority": str(value.owner_authority),
            "allowed_operations": tuple(
                sorted(str(operation.value) for operation in value.allowed_operations)
            ),
            "canonical_authority_ref": (
                None
                if value.canonical_authority_ref is None
                else str(value.canonical_authority_ref)
            ),
            "migration_target_ref": (
                None if value.migration_target_ref is None else str(value.migration_target_ref)
            ),
        }
    )


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
    # capability's mutation contract and PersistentAssetCatalog. Assertions are stored
    # as primitive detached values so Enum singletons never enter retained request truth.
    mutation_persistence: MutationPersistence | str | None = None
    persistent_asset: PersistentAssetDescriptor | Mapping[str, Any] | None = None
    persistent_operation: CrudOperation | str | None = None

    def __post_init__(self) -> None:
        for item in fields(self):
            value = getattr(self, item.name)
            if item.name == "mutation_persistence":
                frozen = _normalize_enum_assertion(
                    value,
                    MutationPersistence,
                    field_name="mutation_persistence",
                )
            elif item.name == "persistent_operation":
                frozen = _normalize_enum_assertion(
                    value,
                    CrudOperation,
                    field_name="persistent_operation",
                )
            elif item.name == "persistent_asset":
                frozen = _persistent_asset_assertion(value)
            else:
                frozen = _freeze_trusted_value(value)
            object.__setattr__(self, item.name, frozen)


@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    """Structurally immutable result value for executor/reconciler boundaries."""

    disposition: ExecutionDisposition
    output: Any = None
    provider_ref: str | None = None
    evidence: Mapping[str, Any] = field(default_factory=dict)
    error: str | None = None

    def __post_init__(self) -> None:
        try:
            disposition = (
                self.disposition
                if type(self.disposition) is ExecutionDisposition
                else ExecutionDisposition(str(self.disposition))
            )
            frozen_output = _freeze_trusted_value(self.output)
            frozen_evidence = _freeze_trusted_value(self.evidence)
            frozen_provider_ref = _freeze_trusted_value(self.provider_ref)
            frozen_error = _freeze_trusted_value(self.error)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "ExecutionOutcome disposition/output/evidence must use the trusted immutable value domain"
            ) from exc
        if not isinstance(frozen_evidence, Mapping):
            raise TypeError("ExecutionOutcome evidence must be a mapping")
        object.__setattr__(self, "disposition", disposition)
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
