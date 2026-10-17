from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
import time
from types import MappingProxyType
from typing import Callable, Mapping

from uaos.resilience import CapabilityCircuitBreaker

from .models import (
    CapabilityAvailability,
    CapabilityCostClass,
    CapabilityHealth,
    CapabilityObservation,
    ExecutionDisposition,
    ExecutionOutcome,
    ExecutionRequest,
    Executor,
)
from .persistent_assets import CrudOperation, MutationContract, MutationPersistence


class CapabilityUnavailable(RuntimeError):
    pass


TargetCanonicalizer = Callable[[str], str]


@dataclass(frozen=True, slots=True)
class RegisteredCapability:
    """Detached public view of trusted registration semantics.

    The executor and target canonicalizer are intentionally absent. Those objects are part
    of the registry's trusted computing base and are never returned through get/all/
    candidates. Public callers can inspect routing/contract semantics but cannot obtain a
    mutable provider/workspace object through a registry view.
    """

    observation: CapabilityObservation
    registration_generation: int
    read_only_actions: frozenset[str] = frozenset()
    mutation_contracts: Mapping[str, MutationContract] = field(default_factory=dict)

    def mutation_contract_for(self, action_name: str) -> MutationContract | None:
        if action_name in self.read_only_actions:
            return None
        try:
            return self.mutation_contracts[action_name]
        except KeyError as exc:
            raise CapabilityUnavailable(
                f"action={action_name!r} has no trusted read/mutation classification"
            ) from exc


@dataclass(frozen=True, slots=True)
class _ObservationRecord:
    capability_id: str
    health: CapabilityHealth
    observed_at_epoch: float
    supported_actions: tuple[str, ...]
    permissions: tuple[str, ...]
    quality_score: float
    estimated_cost: float
    executor_kind: str
    expires_at_epoch: float | None
    metadata_items: tuple[tuple[str, str], ...]
    cost_class: CapabilityCostClass
    availability: CapabilityAvailability


@dataclass(frozen=True, slots=True)
class _MutationContractRecord:
    action_name: str
    persistence: MutationPersistence
    operation: CrudOperation | None


@dataclass(frozen=True, slots=True)
class _RegisteredCapabilityRecord:
    observation: _ObservationRecord
    executor: Executor
    registration_generation: int
    read_only_actions: frozenset[str]
    mutation_contracts: tuple[_MutationContractRecord, ...]
    canonicalize_target: TargetCanonicalizer | None


def _exact_string(
    value: object,
    *,
    field_name: str,
    allow_empty: bool = False,
) -> str:
    if type(value) is not str or (not allow_empty and not value):
        requirement = "an exact builtin string" if allow_empty else "a non-empty exact builtin string"
        raise ValueError(f"{field_name} must be {requirement}")
    return value


def _observation_record(observation: CapabilityObservation) -> _ObservationRecord:
    if type(observation) is not CapabilityObservation:
        raise ValueError("capability observation must use the canonical value type")
    capability_id = _exact_string(observation.capability_id, field_name="capability_id")
    supported_actions = tuple(
        _exact_string(action, field_name="supported action")
        for action in observation.supported_actions
    )
    permissions = tuple(
        _exact_string(permission, field_name="permission")
        for permission in observation.permissions
    )
    executor_kind = _exact_string(
        observation.executor_kind,
        field_name="executor_kind",
        allow_empty=True,
    )
    metadata_items = tuple(
        sorted(
            (
                _exact_string(key, field_name="metadata key"),
                _exact_string(value, field_name="metadata value"),
            )
            for key, value in observation.metadata.items()
        )
    )
    return _ObservationRecord(
        capability_id=capability_id,
        health=(
            observation.health
            if isinstance(observation.health, CapabilityHealth)
            else CapabilityHealth(observation.health)
        ),
        observed_at_epoch=float(observation.observed_at_epoch),
        supported_actions=supported_actions,
        permissions=permissions,
        quality_score=float(observation.quality_score),
        estimated_cost=float(observation.estimated_cost),
        executor_kind=executor_kind,
        expires_at_epoch=(
            None if observation.expires_at_epoch is None else float(observation.expires_at_epoch)
        ),
        metadata_items=metadata_items,
        cost_class=(
            observation.cost_class
            if isinstance(observation.cost_class, CapabilityCostClass)
            else CapabilityCostClass(observation.cost_class)
        ),
        availability=(
            observation.availability
            if isinstance(observation.availability, CapabilityAvailability)
            else CapabilityAvailability(observation.availability)
        ),
    )


def _materialize_observation(record: _ObservationRecord) -> CapabilityObservation:
    return CapabilityObservation(
        capability_id=record.capability_id,
        health=record.health,
        observed_at_epoch=record.observed_at_epoch,
        supported_actions=tuple(record.supported_actions),
        permissions=tuple(record.permissions),
        quality_score=record.quality_score,
        estimated_cost=record.estimated_cost,
        executor_kind=record.executor_kind,
        expires_at_epoch=record.expires_at_epoch,
        metadata=MappingProxyType(dict(record.metadata_items)),
        cost_class=record.cost_class,
        availability=record.availability,
    )


def _contract_record(action_name: str, contract: MutationContract) -> _MutationContractRecord:
    action = _exact_string(action_name, field_name="mutation action")
    if type(contract) is not MutationContract:
        raise ValueError("mutation contract must use the canonical value type")
    persistence = (
        contract.persistence
        if isinstance(contract.persistence, MutationPersistence)
        else MutationPersistence(contract.persistence)
    )
    operation = (
        None
        if contract.operation is None
        else contract.operation
        if isinstance(contract.operation, CrudOperation)
        else CrudOperation(contract.operation)
    )
    normalized = MutationContract(persistence, operation)
    return _MutationContractRecord(action, normalized.persistence, normalized.operation)


def _materialize_registration(record: _RegisteredCapabilityRecord) -> RegisteredCapability:
    contracts = {
        item.action_name: MutationContract(item.persistence, item.operation)
        for item in record.mutation_contracts
    }
    return RegisteredCapability(
        observation=_materialize_observation(record.observation),
        registration_generation=record.registration_generation,
        read_only_actions=frozenset(record.read_only_actions),
        mutation_contracts=MappingProxyType(contracts),
    )


class CapabilityRegistry:
    """Trusted registry with opaque executor/canonicalizer ownership.

    Registration code is part of the trusted setup boundary. After registration, public
    registry views contain only detached routing/contract values; the mutable executor and
    canonicalizer never leave the registry. Provider execution/reconciliation is not a
    public registry API: ActionCoordinator uses module-private invocation helpers with the
    exact registration generation, so ordinary registry holders cannot bypass admission by
    calling a public provider method and re-registration still invalidates stale bindings.
    """

    def __init__(self) -> None:
        self._items: dict[str, _RegisteredCapabilityRecord] = {}
        self._lock = RLock()
        self._generation = 0

    def register(
        self,
        observation: CapabilityObservation,
        executor: Executor,
        *,
        read_only_actions: frozenset[str] | set[str] | tuple[str, ...] | None = None,
        mutation_contracts: Mapping[str, MutationContract] | None = None,
        canonicalize_target: TargetCanonicalizer | None = None,
    ) -> None:
        observation_record = _observation_record(observation)
        read_actions = frozenset(
            _exact_string(action, field_name="read-only action")
            for action in (read_only_actions or ())
        )
        contract_records = tuple(
            sorted(
                (
                    _contract_record(action_name, contract)
                    for action_name, contract in (mutation_contracts or {}).items()
                ),
                key=lambda item: item.action_name,
            )
        )
        contract_actions = {item.action_name for item in contract_records}
        supported = set(observation_record.supported_actions)
        classified = set(read_actions) | contract_actions
        unsupported = classified - supported
        if unsupported:
            raise ValueError(
                f"action contracts reference unsupported actions: {sorted(unsupported)}"
            )
        overlap = set(read_actions) & contract_actions
        if overlap:
            raise ValueError(
                f"actions cannot be both read-only and mutating: {sorted(overlap)}"
            )
        missing = supported - classified
        if missing:
            raise ValueError(
                f"every supported action requires trusted read/mutation classification: {sorted(missing)}"
            )
        durable = any(item.operation is not None for item in contract_records)
        if durable and canonicalize_target is None:
            raise ValueError(
                "durable/external capability registration requires canonicalize_target"
            )

        with self._lock:
            self._generation += 1
            self._items[observation_record.capability_id] = _RegisteredCapabilityRecord(
                observation=observation_record,
                executor=executor,
                registration_generation=self._generation,
                read_only_actions=read_actions,
                mutation_contracts=contract_records,
                canonicalize_target=canonicalize_target,
            )

    def _record_for(
        self,
        capability_id: str,
        *,
        registration_generation: int | None = None,
    ) -> _RegisteredCapabilityRecord:
        key = _exact_string(capability_id, field_name="capability_id")
        with self._lock:
            try:
                record = self._items[key]
            except KeyError as exc:
                raise CapabilityUnavailable(f"capability not registered: {key}") from exc
            if (
                registration_generation is not None
                and record.registration_generation != registration_generation
            ):
                raise CapabilityUnavailable(
                    "capability registration generation changed before trusted adapter invocation"
                )
            return record

    def get(self, capability_id: str) -> RegisteredCapability:
        return _materialize_registration(self._record_for(capability_id))

    def all(self) -> tuple[RegisteredCapability, ...]:
        with self._lock:
            records = tuple(self._items.values())
        return tuple(_materialize_registration(record) for record in records)

    def candidates(self, request: ExecutionRequest) -> tuple[RegisteredCapability, ...]:
        with self._lock:
            records = tuple(self._items.values())
        required_permissions = set(request.required_permissions)
        now = time.time()
        eligible: list[RegisteredCapability] = []
        for record in records:
            obs = record.observation
            if obs.health not in {CapabilityHealth.AVAILABLE, CapabilityHealth.DEGRADED}:
                continue
            if obs.expires_at_epoch is not None and now >= obs.expires_at_epoch:
                continue
            if request.action_name not in obs.supported_actions:
                continue
            if not required_permissions.issubset(obs.permissions):
                continue
            if request.required_capability_id and obs.capability_id != request.required_capability_id:
                continue
            if obs.quality_score < request.quality_floor:
                continue
            if request.cost_ceiling is not None and obs.estimated_cost > request.cost_ceiling:
                continue
            if obs.cost_class is CapabilityCostClass.PAID and not request.allow_paid:
                continue
            if obs.cost_class is CapabilityCostClass.UNKNOWN and not request.allow_unknown_cost:
                continue
            if request.requires_background and obs.availability is not CapabilityAvailability.BACKGROUND:
                continue
            eligible.append(_materialize_registration(record))
        return tuple(eligible)

    def canonicalize_trusted_target(
        self,
        capability_id: str,
        registration_generation: int,
        target: str,
    ) -> str:
        record = self._record_for(
            capability_id,
            registration_generation=registration_generation,
        )
        canonicalizer = record.canonicalize_target
        if canonicalizer is None:
            raise CapabilityUnavailable(
                "capability registration has no trusted target canonicalizer"
            )
        return canonicalizer(target)


def _execute_registered(
    registry: CapabilityRegistry,
    capability_id: str,
    registration_generation: int,
    request: ExecutionRequest,
) -> ExecutionOutcome:
    """Coordinator-internal provider invocation; intentionally absent from registry public API."""
    if type(registry) is not CapabilityRegistry:
        raise CapabilityUnavailable("trusted provider invocation requires CapabilityRegistry")
    record = registry._record_for(capability_id, registration_generation=registration_generation)
    return record.executor.execute(request)


def _reconcile_registered(
    registry: CapabilityRegistry,
    capability_id: str,
    registration_generation: int,
    request: ExecutionRequest,
    unknown: ExecutionOutcome,
) -> ExecutionOutcome | None:
    """Coordinator-internal reconciliation; intentionally absent from registry public API."""
    if type(registry) is not CapabilityRegistry:
        raise CapabilityUnavailable("trusted provider reconciliation requires CapabilityRegistry")
    record = registry._record_for(capability_id, registration_generation=registration_generation)
    reconciler = getattr(record.executor, "reconcile", None)
    if reconciler is None:
        return None
    return reconciler(request, unknown)


class CapabilityRouter:
    """Deterministic zero-cost-first selection with circuit breaking."""

    _cost_rank = {
        CapabilityCostClass.INCLUDED: 0,
        CapabilityCostClass.FREE: 0,
        CapabilityCostClass.UNKNOWN: 1,
        CapabilityCostClass.PAID: 2,
    }

    def __init__(self, *, circuit: CapabilityCircuitBreaker | None = None) -> None:
        self.circuit = circuit or CapabilityCircuitBreaker()

    def ranked(
        self, registry: CapabilityRegistry, request: ExecutionRequest
    ) -> tuple[RegisteredCapability, ...]:
        candidates = tuple(
            item
            for item in registry.candidates(request)
            if self.circuit.allows(item.observation.capability_id)
        )
        return tuple(
            sorted(
                candidates,
                key=lambda item: (
                    self._cost_rank[item.observation.cost_class],
                    -item.observation.quality_score,
                    item.observation.estimated_cost,
                    item.observation.capability_id,
                ),
            )
        )

    def select(
        self, registry: CapabilityRegistry, request: ExecutionRequest
    ) -> RegisteredCapability:
        candidates = self.ranked(registry, request)
        if not candidates:
            raise CapabilityUnavailable(
                f"no executable capability satisfies action={request.action_name!r}, permissions, quality, cost, availability and circuit constraints"
            )
        return candidates[0]

    def record_outcome(
        self, capability_id: str, disposition: ExecutionDisposition
    ) -> None:
        self.circuit.record(capability_id, disposition)
