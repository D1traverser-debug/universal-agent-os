from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
import time
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
    mutation_contracts: Mapping[str, MutationContract] = field(default_factory=dict)
    canonicalize_target: TargetCanonicalizer | None = None


class CapabilityRegistry:
    def __init__(self) -> None:
        self._items: dict[str, RegisteredCapability] = {}
        self._lock = RLock()

    def register(
        self,
        observation: CapabilityObservation,
        executor: Executor,
        *,
        mutation_contracts: Mapping[str, MutationContract] | None = None,
        canonicalize_target: TargetCanonicalizer | None = None,
    ) -> None:
        contracts = dict(mutation_contracts or {})
        unsupported = set(contracts) - set(observation.supported_actions)
        if unsupported:
            raise ValueError(
                f"mutation contracts reference unsupported actions: {sorted(unsupported)}"
            )
        with self._lock:
            self._items[observation.capability_id] = RegisteredCapability(
                observation,
                executor,
                contracts,
                canonicalize_target,
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
