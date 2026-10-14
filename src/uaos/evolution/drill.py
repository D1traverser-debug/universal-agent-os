from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from uaos.execution import (
    ActionCoordinator,
    ApprovalGrant,
    CapabilityRegistry,
    ExecutionDisposition,
    ExecutionRequest,
    register_local_workspace_capability,
)
from uaos.state import SQLiteAppendOnlyLedger

from .gates import assess_promotion
from .lifecycle import post_promotion_recommendation, transition_proposal
from .models import (
    ChangeProposal,
    ComplexityBudget,
    ComplexityDelta,
    EvaluationResult,
    PostPromotionObservation,
    ProposalState,
)


@dataclass(frozen=True, slots=True)
class SelfChangeDrillResult:
    proposal_id: str
    candidate_hash: str
    restored_hash: str
    recommendation: str
    final_state: ProposalState
    ledger_events: int


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_self_change_drill(
    root: str | Path, *, run_id: str | None = None
) -> SelfChangeDrillResult:
    """Exercise evaluation -> approval -> promotion -> observation -> rollback.

    The drill mutates only an isolated local workspace. It intentionally injects
    a post-promotion regression so the rollback path must execute and restore the
    exact baseline hash.
    """

    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    run_id = run_id or uuid.uuid4().hex
    proposal_id = f"self-change-drill:{run_id}"
    baseline = "mode=stable\n"
    candidate = "mode=candidate\n"
    target = root / "policy.txt"
    target.write_text(baseline, encoding="utf-8")

    proposal = ChangeProposal(
        proposal_id=proposal_id,
        title="Controlled local self-change drill",
        failure_class_ids=("failure:self-change-drill",),
        hypothesis="a candidate can be promoted and rolled back without escaping the governed action path",
        target_scope="local-drill-workspace",
        added_mechanisms=(),
        replaced_mechanisms=("baseline-policy",),
        retired_mechanisms=(),
        why_not_reuse="",
        retirement_rationale="candidate exists only for the drill and is retired after rollback",
        rollback_plan="restore exact baseline bytes by hash",
        expected_benefit="prove promotion/observation/rollback mechanics",
        new_failure_modes=("workspace mutation failure",),
        required_scenarios=("scenario:self-change",),
        complexity_delta=ComplexityDelta(),
        evidence_refs=("drill:baseline",),
    )
    proposal = transition_proposal(proposal, ProposalState.EVALUATED)
    evaluation = EvaluationResult(
        evaluation_id=f"eval:{run_id}",
        proposal_id=proposal_id,
        scenario_refs=("scenario:self-change",),
        metrics_before={"rollback_proven": 0.0},
        metrics_after={"rollback_proven": 1.0},
        acceptance_checks={"candidate_isolated": True, "rollback_defined": True},
        passed=True,
        evidence_refs=("drill:evaluation",),
    )
    authorization = assess_promotion(
        proposal, (evaluation,), budget=ComplexityBudget()
    )
    if not authorization.approved:
        raise RuntimeError(authorization.reasons)
    proposal = transition_proposal(proposal, ProposalState.APPROVED)

    registry = CapabilityRegistry()
    register_local_workspace_capability(registry, root)
    coordinator = ActionCoordinator(registry, authority_context="UAOS")
    now = datetime.now(UTC)

    promote = ExecutionRequest(
        action_id=f"action:promote:{run_id}",
        action_name="local.write_text",
        target="policy.txt",
        payload={
            "content": candidate,
            "expected_current_hash": _sha256(baseline),
        },
        required_permissions=("workspace:write",),
        parameter_hash=_sha256(candidate),
        side_effect_class="WRITE",
        approval_required=True,
        target_authority="UAOS",
    )
    promotion_grant = ApprovalGrant(
        f"approval:promote:{run_id}",
        promote.action_id,
        promote.target,
        promote.parameter_hash,
        now + timedelta(minutes=5),
    )
    promoted_outcome = coordinator.execute(
        promote, approval=promotion_grant, now=now
    ).outcome
    if promoted_outcome.disposition is not ExecutionDisposition.CONFIRMED:
        raise RuntimeError(promoted_outcome.error)
    proposal = transition_proposal(proposal, ProposalState.PROMOTED)

    observation = PostPromotionObservation(
        f"obs:{run_id}",
        proposal_id,
        False,
        {"synthetic_regression": 1.0},
        ("drill:observation",),
        (f"regression:{run_id}",),
    )
    recommendation = post_promotion_recommendation(proposal, (observation,))
    if recommendation != "ROLLBACK":
        raise RuntimeError("drill failed to request rollback")

    rollback = ExecutionRequest(
        action_id=f"action:rollback:{run_id}",
        action_name="local.write_text",
        target="policy.txt",
        payload={
            "content": baseline,
            "expected_current_hash": _sha256(candidate),
        },
        required_permissions=("workspace:write",),
        parameter_hash=_sha256(baseline),
        side_effect_class="WRITE",
        approval_required=True,
        target_authority="UAOS",
    )
    rollback_grant = ApprovalGrant(
        f"approval:rollback:{run_id}",
        rollback.action_id,
        rollback.target,
        rollback.parameter_hash,
        now + timedelta(minutes=5),
    )
    rollback_outcome = coordinator.execute(
        rollback, approval=rollback_grant, now=now
    ).outcome
    if rollback_outcome.disposition is not ExecutionDisposition.CONFIRMED:
        raise RuntimeError(rollback_outcome.error)

    proposal = transition_proposal(proposal, ProposalState.ROLLED_BACK)
    proposal = transition_proposal(proposal, ProposalState.RETIRED)
    if target.read_text(encoding="utf-8") != baseline:
        raise RuntimeError("rollback did not restore baseline")

    ledger = SQLiteAppendOnlyLedger(root / "drill.db")
    for index, event_type in enumerate(
        (
            "EVALUATED",
            "APPROVED",
            "PROMOTED",
            "REGRESSION_OBSERVED",
            "ROLLED_BACK",
            "RETIRED",
        ),
        1,
    ):
        ledger.append(
            event_id=f"{proposal_id}:{index}",
            aggregate_type="change_proposal",
            aggregate_id=proposal_id,
            event_type=event_type,
            payload={"run_id": run_id},
        )

    return SelfChangeDrillResult(
        proposal_id,
        _sha256(candidate),
        _sha256(baseline),
        recommendation,
        proposal.state,
        len(ledger.events_for("change_proposal", proposal_id)),
    )
