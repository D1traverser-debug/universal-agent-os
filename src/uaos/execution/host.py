from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable

from .models import (
    CapabilityAvailability,
    CapabilityCostClass,
    CapabilityHealth,
    CapabilityObservation,
    ExecutionDisposition,
    ExecutionOutcome,
    ExecutionRequest,
)
from .registry import CapabilityRegistry


HostCallback = Callable[[ExecutionRequest], Any]


class HostCallableExecutor:
    """Wrap a capability supplied by the current host/session.

    The callback may represent a built-in tool, connected plugin, free API,
    browser/search capability, local script or another host-provided executor.
    UAOS does not assume that it is available outside the current session.
    """

    def __init__(self, callback: HostCallback) -> None:
        self._callback = callback

    def execute(self, request: ExecutionRequest) -> ExecutionOutcome:
        try:
            result = self._callback(request)
        except Exception as exc:
            return ExecutionOutcome(
                disposition=ExecutionDisposition.FAILED,
                error=f"{type(exc).__name__}: {exc}",
            )
        if isinstance(result, ExecutionOutcome):
            return result
        return ExecutionOutcome(
            disposition=ExecutionDisposition.CONFIRMED,
            output=result,
            evidence={"executor_kind": "host_callback"},
        )


@dataclass(frozen=True, slots=True)
class HostCapabilitySpec:
    capability_id: str
    supported_actions: tuple[str, ...]
    callback: HostCallback
    permissions: tuple[str, ...] = ()
    quality_score: float = 0.8
    estimated_cost: float = 0.0
    cost_class: CapabilityCostClass = CapabilityCostClass.INCLUDED
    availability: CapabilityAvailability = CapabilityAvailability.SESSION
    health: CapabilityHealth = CapabilityHealth.AVAILABLE
    ttl_seconds: float | None = None
    provider: str = "host"

    def __post_init__(self) -> None:
        if not self.capability_id.strip():
            raise ValueError("capability_id is required")
        if not self.supported_actions:
            raise ValueError("supported_actions is required")
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost cannot be negative")
        if self.ttl_seconds is not None and self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")


def register_host_capability(
    registry: CapabilityRegistry,
    spec: HostCapabilitySpec,
    *,
    observed_at_epoch: float | None = None,
) -> CapabilityObservation:
    observed_at_epoch = observed_at_epoch if observed_at_epoch is not None else time.time()
    expires_at = None if spec.ttl_seconds is None else observed_at_epoch + spec.ttl_seconds
    observation = CapabilityObservation(
        capability_id=spec.capability_id,
        health=spec.health,
        observed_at_epoch=observed_at_epoch,
        supported_actions=spec.supported_actions,
        permissions=spec.permissions,
        quality_score=spec.quality_score,
        estimated_cost=spec.estimated_cost,
        executor_kind="host_callback",
        expires_at_epoch=expires_at,
        metadata={"provider": spec.provider},
        cost_class=spec.cost_class,
        availability=spec.availability,
    )
    registry.register(observation, HostCallableExecutor(spec.callback))
    return observation
