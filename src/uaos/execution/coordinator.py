from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .approvals import ApprovalGate, ApprovalGrant
from .models import ExecutionDisposition, ExecutionOutcome, ExecutionRequest
from .registry import CapabilityRegistry, CapabilityRouter, CapabilityUnavailable

@dataclass(frozen=True, slots=True)
class CoordinatedExecution:
    capability_id: str
    outcome: ExecutionOutcome

class ActionCoordinator:
    """Policy boundary around executor adapters and safe fallback."""
    def __init__(self, registry: CapabilityRegistry, *, router: CapabilityRouter | None = None, approval_gate: ApprovalGate | None = None) -> None:
        self.registry = registry
        self.router = router or CapabilityRouter()
        self.approval_gate = approval_gate or ApprovalGate()
    def execute(self, request: ExecutionRequest, *, approval: ApprovalGrant | None = None, now: datetime | None = None) -> CoordinatedExecution:
        now = now or datetime.now(UTC)
        self.approval_gate.require(request, approval, now=now)
        registered = self.router.select(self.registry, request)
        outcome = registered.executor.execute(request)
        self.router.record_outcome(registered.observation.capability_id, outcome.disposition)
        if outcome.disposition not in {ExecutionDisposition.CONFIRMED, ExecutionDisposition.FAILED, ExecutionDisposition.UNKNOWN}:
            raise RuntimeError("executor returned unsupported disposition")
        return CoordinatedExecution(registered.observation.capability_id, outcome)
    def execute_with_fallback(self, request: ExecutionRequest, *, approval: ApprovalGrant | None = None, now: datetime | None = None) -> CoordinatedExecution:
        if request.side_effect_class not in {"NONE", "READ"}:
            return self.execute(request, approval=approval, now=now)
        now = now or datetime.now(UTC)
        self.approval_gate.require(request, approval, now=now)
        ranked = self.router.ranked(self.registry, request)
        if not ranked:
            raise CapabilityUnavailable(f"no executable capability satisfies action={request.action_name!r}")
        last: CoordinatedExecution | None = None
        for registered in ranked:
            outcome = registered.executor.execute(request)
            self.router.record_outcome(registered.observation.capability_id, outcome.disposition)
            current = CoordinatedExecution(registered.observation.capability_id, outcome)
            if outcome.disposition is ExecutionDisposition.CONFIRMED: return current
            if outcome.disposition is ExecutionDisposition.UNKNOWN: return current
            last = current
        if last is None:
            raise CapabilityUnavailable(f"no executable capability for action={request.action_name!r}")
        return last
    def reconcile(self, request: ExecutionRequest, unknown: CoordinatedExecution) -> CoordinatedExecution:
        if unknown.outcome.disposition is not ExecutionDisposition.UNKNOWN:
            raise ValueError("only UNKNOWN execution may be reconciled")
        registered = self.registry.get(unknown.capability_id)
        reconciler = getattr(registered.executor, "reconcile", None)
        if reconciler is None: return unknown
        outcome = reconciler(request, unknown.outcome)
        self.router.record_outcome(unknown.capability_id, outcome.disposition)
        if outcome.disposition is ExecutionDisposition.UNKNOWN: return CoordinatedExecution(unknown.capability_id, outcome)
        if outcome.disposition not in {ExecutionDisposition.CONFIRMED, ExecutionDisposition.FAILED}:
            raise RuntimeError("reconciler must return CONFIRMED, FAILED or UNKNOWN")
        return CoordinatedExecution(unknown.capability_id, outcome)
