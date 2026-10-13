from __future__ import annotations
from .models import ChangeProposal, ComplexityBudget, EvaluationResult, PromotionAuthorization, ProposalState


def assess_promotion(
    proposal: ChangeProposal,
    evaluations: tuple[EvaluationResult, ...],
    *,
    budget: ComplexityBudget,
) -> PromotionAuthorization:
    reasons: list[str] = []
    if proposal.state is not ProposalState.EVALUATED:
        reasons.append(f"proposal must be EVALUATED before promotion: {proposal.state}")
    relevant = tuple(e for e in evaluations if e.proposal_id == proposal.proposal_id)
    if not relevant:
        reasons.append("no evaluation for proposal")
    if relevant and not all(e.passed for e in relevant):
        reasons.append("one or more evaluations failed")
    covered = {scenario for evaluation in relevant for scenario in evaluation.scenario_refs}
    missing_scenarios = set(proposal.required_scenarios) - covered
    if missing_scenarios:
        reasons.append(f"required evaluation scenarios missing: {sorted(missing_scenarios)}")
    if any(e.regression_failures for e in relevant):
        reasons.append("regression failures remain")
    if proposal.complexity_delta.net_components > budget.max_net_components:
        reasons.append("component complexity budget exceeded")
    if proposal.complexity_delta.net_state_surfaces > budget.max_net_state_surfaces:
        reasons.append("state-surface complexity budget exceeded")
    if proposal.complexity_delta.maintenance_cost_delta > budget.max_maintenance_cost_delta:
        reasons.append("maintenance-cost budget exceeded")
    if proposal.added_mechanisms and not (proposal.replaced_mechanisms or proposal.retired_mechanisms):
        if proposal.retirement_rationale.strip().lower() in {"", "none", "n/a"}:
            reasons.append("new mechanism has no credible overlap/retirement analysis")
    return PromotionAuthorization(proposal.proposal_id, not reasons, tuple(reasons))
