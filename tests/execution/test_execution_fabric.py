from datetime import UTC, datetime, timedelta
import pytest

from uaos.execution import (
    ActionCoordinator, ApprovalGrant, ApprovalRequired, CapabilityHealth,
    CapabilityObservation, CapabilityRegistry, CapabilityUnavailable,
    ExecutionDisposition, ExecutionOutcome, ExecutionRequest
)


class Executor:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []

    def execute(self, request):
        self.calls.append(request)
        return self.outcome


class ReconcilingExecutor(Executor):
    def reconcile(self, request, unknown):
        return ExecutionOutcome(ExecutionDisposition.CONFIRMED, output="found", provider_ref="r1")


def observation(capability_id, *, actions=("research",), permissions=(), quality=0.8, cost=1.0, health=CapabilityHealth.AVAILABLE):
    return CapabilityObservation(capability_id, health, 1.0, actions, permissions, quality, cost, "agent")


def test_router_filters_mandatory_permissions_quality_and_cost():
    registry = CapabilityRegistry()
    registry.register(observation("cheap", permissions=("web",), quality=0.8, cost=1), Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED)))
    registry.register(observation("best", permissions=("web",), quality=0.95, cost=2), Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED)))
    request = ExecutionRequest("a1", "research", "topic", {}, required_permissions=("web",), quality_floor=0.9, cost_ceiling=3)
    result = ActionCoordinator(registry).execute(request)
    assert result.capability_id == "best"


def test_router_never_silently_downgrades_mandatory_floor():
    registry = CapabilityRegistry()
    registry.register(observation("weak", quality=0.4), Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED)))
    request = ExecutionRequest("a1", "research", "topic", {}, quality_floor=0.9)
    with pytest.raises(CapabilityUnavailable):
        ActionCoordinator(registry).execute(request)


def test_side_effect_can_require_exact_action_approval():
    registry = CapabilityRegistry()
    registry.register(observation("writer", actions=("write",), permissions=("repo:write",)), Executor(ExecutionOutcome(ExecutionDisposition.CONFIRMED)))
    request = ExecutionRequest("a1", "write", "repo:file", {}, required_permissions=("repo:write",), parameter_hash="p1", side_effect_class="WRITE", approval_required=True)
    coordinator = ActionCoordinator(registry)
    with pytest.raises(ApprovalRequired):
        coordinator.execute(request)
    now = datetime.now(UTC)
    wrong = ApprovalGrant("g", "a1", "repo:other", "p1", now + timedelta(minutes=5))
    with pytest.raises(ApprovalRequired):
        coordinator.execute(request, approval=wrong, now=now)
    right = ApprovalGrant("g", "a1", "repo:file", "p1", now + timedelta(minutes=5))
    assert coordinator.execute(request, approval=right, now=now).outcome.disposition is ExecutionDisposition.CONFIRMED


def test_unknown_outcome_is_not_guessed_and_can_reconcile():
    registry = CapabilityRegistry()
    registry.register(observation("remote"), ReconcilingExecutor(ExecutionOutcome(ExecutionDisposition.UNKNOWN, error="timeout")))
    request = ExecutionRequest("a1", "research", "remote", {})
    coordinator = ActionCoordinator(registry)
    unknown = coordinator.execute(request)
    assert unknown.outcome.disposition is ExecutionDisposition.UNKNOWN
    resolved = coordinator.reconcile(request, unknown)
    assert resolved.outcome.disposition is ExecutionDisposition.CONFIRMED
