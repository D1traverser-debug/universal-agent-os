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
    ExecutionRequest,
    Executor,
)
from .persistent_assets import MutationContract


class CapabilityUnavailable(RuntimeError):
    pass


TargetCanonicalizer = Callable[[str], str]


@dataclass(frozen=True, slots=True)
class RegisteredCapability:
    observation: CapabilityObservation
    executor: Executor
    registration_generation: int
    read_only_actions: frozenset[str] = frozenset()
    mutation_contracts: Mapping[str, MutationContract] = field(default_factory=dict)
    canonicalize_target: TargetCanonicalizer | None = None

    def mutation_contract_for(self, action_name: str) -> MutationContract | None:
        if action_name in self.read_only_actions:
            return None
        try:
            return self.mutation_contracts[action_name]
        except KeyError as exc:
            raise CapabilityUnavailable(
                f"action={action_name!r} has no trusted read/mutation classification"
            ) from exc


class CapabilityRegistry:
    def __init__(self) -> None:
        self._items: dict[str, RegisteredCapability] = {}
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
        read_actions = frozenset(read_only_actions or ())
        contracts_dict = dict(mutation_contracts or {})
        supported = set(observation.supported_actions)
        classified = set(read_actions) | set(contracts_dict)
        unsupported = classified - supported
        if unsupported:
            raise ValueError(
                f"action contracts reference unsupported actions: {sorted(unsupported)}"
            )
        overlap = set(read_actions) & set(contracts_dict)
        if overlap:
            raise ValueError(
                f"actions cannot be both read-only and mutating: {sorted(overlap)}"
            )
        missing = supported - classified
        if missing:
            raise ValueError(
                f"every supported action requires trusted read/mutation classification: {sorted(missing)}"
            )
        durable = any(contract.operation is not None for contract in contracts_dict.values())
        if durable and canonicalize_target is None:
            raise ValueError(
                "durable/external capability registration requires canonicalize_target"
            )

        # Registration is the sole mutation point for trusted action semantics. Exposed
        # RegisteredCapability objects must not let callers alter contracts in place
        # without a new generation, so freeze the mapping before publishing it.
        contracts: Mapping[str, MutationContract] = MappingProxyType(contracts_dict)
        with self._lock:
            self._generation += 1
            self._items[observation.capability_id] = RegisteredCapability(
                observation=observation,
                executor=executor,
                registration_generation=self._generation,
                read_only_actions=read_actions,
                mutation_contracts=contracts,
                canonicalize_target=canonicalize_target,
            )

    def get(self, capability_id: str) -> RegisteredCapability:
        with self._lock:
            try:
                return self._items[capability_id]
            except KeyError as exc:
                raise CapabilityUnavailable(f"capability not registered: {capability_id}") from exc

    def all(self) -> tuple[RegisteredCapability, ...]:
        with self._lock:
            return tuple(self._items.values())

    def candidates(self, request: ExecutionRequest) -> tuple[RegisteredCapability, ...]:
        with self._lock:
            values = tuple(self._items.values())
        required_permissions = set(request.required_permissions)
        now = time.time()
        eligible = []
        for item in values:
            obs = item.observation
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
            eligible.append(item)
        return tuple(eligible)


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
