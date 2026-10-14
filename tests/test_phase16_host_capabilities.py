import time
import pytest

from uaos.execution import (
    CapabilityAvailability,
    CapabilityCostClass,
    CapabilityRegistry,
    CapabilityRouter,
    CapabilityUnavailable,
    ExecutionRequest,
    HostCapabilitySpec,
    register_host_capability,
)


def test_zero_cost_first_and_paid_blocked_by_default():
    registry = CapabilityRegistry()
    register_host_capability(registry, HostCapabilitySpec("free", ("research",), lambda req: "free", quality_score=0.8, cost_class=CapabilityCostClass.FREE))
    register_host_capability(registry, HostCapabilitySpec("paid", ("research",), lambda req: "paid", quality_score=1.0, estimated_cost=0.01, cost_class=CapabilityCostClass.PAID))
    assert CapabilityRouter().select(registry, ExecutionRequest("a", "research", "x", {})).observation.capability_id == "free"
    assert CapabilityRouter().select(registry, ExecutionRequest("a", "research", "x", {}, allow_paid=True)).observation.capability_id == "free"


def test_unknown_cost_is_not_auto_called():
    registry = CapabilityRegistry()
    register_host_capability(registry, HostCapabilitySpec("unknown", ("research",), lambda req: "x", cost_class=CapabilityCostClass.UNKNOWN))
    with pytest.raises(CapabilityUnavailable):
        CapabilityRouter().select(registry, ExecutionRequest("a", "research", "x", {}))
    assert CapabilityRouter().select(registry, ExecutionRequest("a", "research", "x", {}, allow_unknown_cost=True)).observation.capability_id == "unknown"


def test_background_requirement_does_not_use_session_plugin():
    registry = CapabilityRegistry()
    register_host_capability(registry, HostCapabilitySpec("session", ("research",), lambda req: "x", availability=CapabilityAvailability.SESSION))
    with pytest.raises(CapabilityUnavailable):
        CapabilityRouter().select(registry, ExecutionRequest("a", "research", "x", {}, requires_background=True))


def test_expired_session_capability_is_not_routable():
    registry = CapabilityRegistry()
    register_host_capability(registry, HostCapabilitySpec("short", ("research",), lambda req: "x", ttl_seconds=0.01), observed_at_epoch=time.time() - 1)
    assert not registry.candidates(ExecutionRequest("a", "research", "x", {}))
