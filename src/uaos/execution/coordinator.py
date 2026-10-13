from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .approvals import ApprovalGate, ApprovalGrant
from .models import ExecutionDisposition, ExecutionOutcome, ExecutionRequest
from .registry import CapabilityRegistry, CapabilityRouter


@dataclass(frozen=True, slots=True)
class CoordinatedExecution:
    capability_id: str
    outcome: ExecutionOutcome


class ActionCoordinator:
    """Policy boundary around executor adapters.

    ActionRecord persistence belongs to the authoritative state/action
    repository. UNKNOWN is preserved explicitly and never guessed into success
    or failure.
    """

    def __init__(self, registry: CapabilityRegistry, *, router: CapabilityRouter | None = None, approval_gate: ApprovalGate | None = None) -> None:
        self.registry = registry
        self.router = router or CapabilityRouter()
        self.approval_gate = approval_gate or ApprovalGate()

    def execute(self, request: ExecutionRequest, *, approval: ApprovalGrant | None = None, now: datetime | None = None) -> CoordinatedExecution:
        now = now or datetime.now(UTC)
        self.approval_gate.require(request, approval, now=now)
        registered = self.router.select(self.registry, request)
        outcome = registered.executor.execute(request)
        if outcome.disposition not in {
            ExecutionDisposition.CONFIRMED,
            ExecutionDisposition.FAILED,
            ExecutionDisposition.UNKNOWN,
        }:
            raise RuntimeError("executor returned unsupported disposition")
        return CoordinatedExecution(registered.observation.capability_id, outcome)

    def reconcile(self, request: ExecutionRequest, unknown: CoordinatedExecution) -> CoordinatedExecution:
        if unknown.outcome.disposition is not ExecutionDisposition.UNKNOWN:
            raise ValueError("only UNKNOWN execution may be reconciled")
        registered = self.registry.get(unknown.capability_id)
        reconciler = getattr(registered.executor, "reconcile", None)
        if reconciler is None:
            return unknown
        outcome = reconciler(request, unknown.outcome)
        if outcome.disposition is ExecutionDisposition.UNKNOWN:
            return CoordinatedExecution(unknown.capability_id, outcome)
        if outcome.disposition not in {ExecutionDisposition.CONFIRMED, ExecutionDisposition.FAILED}:
            raise RuntimeError("reconciler must return CONFIRMED, FAILED or UNKNOWN")
        return CoordinatedExecution(unknown.capability_id, outcome)
