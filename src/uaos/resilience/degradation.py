from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum

class DependencyClass(StrEnum):
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"
    OPTIONAL = "OPTIONAL"

class OperatingState(StrEnum):
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    WAITING_CAPABILITY = "WAITING_CAPABILITY"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    PAUSED_NO_HOST = "PAUSED_NO_HOST"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
    BLOCKED = "BLOCKED"

@dataclass(frozen=True, slots=True)
class DegradationDecision:
    state: OperatingState
    may_continue: bool
    reason: str
    retry_when_capabilities_refresh: bool = False

def decide_missing_capability(
    dependency: DependencyClass,
    *,
    fallback_available: bool,
    fallback_safe: bool = True,
    requires_background: bool = False,
    background_host_available: bool = True,
    optional_outputs_required_downstream: bool = False,
) -> DegradationDecision:
    if fallback_available and fallback_safe:
        return DegradationDecision(
            OperatingState.DEGRADED, True,
            "preferred capability unavailable; verified fallback will be used"
        )
    if requires_background and not background_host_available:
        return DegradationDecision(
            OperatingState.PAUSED_NO_HOST, False,
            "background execution requested but no background host is currently available",
            retry_when_capabilities_refresh=True,
        )
    if dependency is DependencyClass.OPTIONAL and not optional_outputs_required_downstream:
        return DegradationDecision(
            OperatingState.DEGRADED, True,
            "optional capability unavailable; optional work may be skipped"
        )
    return DegradationDecision(
        OperatingState.WAITING_CAPABILITY, False,
        f"{dependency.value.lower()} capability unavailable",
        retry_when_capabilities_refresh=True,
    )

_STATE_PRIORITY = {
    OperatingState.NORMAL: 0,
    OperatingState.DEGRADED: 1,
    OperatingState.PAUSED_NO_HOST: 2,
    OperatingState.WAITING_CAPABILITY: 3,
    OperatingState.WAITING_APPROVAL: 4,
    OperatingState.RECOVERY_REQUIRED: 5,
    OperatingState.BLOCKED: 6,
}

def combine_operating_states(states: tuple[OperatingState, ...]) -> OperatingState:
    if not states:
        return OperatingState.NORMAL
    return max(states, key=_STATE_PRIORITY.__getitem__)
