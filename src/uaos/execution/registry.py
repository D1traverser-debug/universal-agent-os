from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
import time

from .models import CapabilityHealth, CapabilityObservation, ExecutionRequest, Executor


class CapabilityUnavailable(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RegisteredCapability:
    observation: CapabilityObservation
    executor: Executor


class CapabilityRegistry:
    def __init__(self) -> None:
        self._items: dict[str, RegisteredCapability] = {}
        self._lock = RLock()

    def register(self, observation: CapabilityObservation, executor: Executor) -> None:
        with self._lock:
            self._items[observation.capability_id] = RegisteredCapability(observation, executor)

    def get(self, capability_id: str) -> RegisteredCapability:
        with self._lock:
            try:
                return self._items[capability_id]
            except KeyError as exc:
                raise CapabilityUnavailable(f"capability not registered: {capability_id}") from exc

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
            eligible.append(item)
        return tuple(eligible)


class CapabilityRouter:
    """Deterministic selection after mandatory constraints are satisfied."""

    def select(self, registry: CapabilityRegistry, request: ExecutionRequest) -> RegisteredCapability:
        candidates = registry.candidates(request)
        if not candidates:
            raise CapabilityUnavailable(
                f"no executable capability satisfies action={request.action_name!r}, permissions, quality and cost constraints"
            )
        return sorted(
            candidates,
            key=lambda item: (
                -item.observation.quality_score,
                item.observation.estimated_cost,
                item.observation.capability_id,
            ),
        )[0]
