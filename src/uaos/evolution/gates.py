from __future__ import annotations
from collections.abc import Mapping

from uaos.contracts.enums import KnowledgeState
from uaos.contracts.models import KnowledgeItem

from .models import ChangeProposal, ComplexityBudget, EvaluationResult, PromotionAuthorization, ProposalState


def assess_promotion(
    proposal: ChangeProposal,
    evaluations: tuple[EvaluationResult, ...],
    *,
    budget: ComplexityBudget,
    knowledge_by_id: Mapping[str, KnowledgeItem] | None = None,
) -> PromotionAuthorization:
    reasons: list[str] = []
    if proposal.state is not ProposalState.EVALUATED:
        reasons.append(f"proposal must be EVALUATED before promotion: {proposal.state}")

    if proposal.knowledge_ids:
        knowledge_by_id = knowledge_by_id or {}
        missing = tuple(item_id for item_id in proposal.knowledge_ids if item_id not in knowledge_by_id)
        if missing:
            reasons.append(f"knowledge-origin proposal has unresolved knowledge ids: {list(missing)}")
        immature = tuple(
            item_id
            for item_id in proposal.knowledge_ids
            if item_id in knowledge_by_id
            and knowledge_by_id[item_id].state not in {KnowledgeState.EVALUATED, KnowledgeState.CANONICAL}
        )
        if immature:
            reasons.append(f"knowledge-origin proposal requires EVALUATED or CANONICAL knowledge: {list(immature)}")

    relevant = tuple(e for e in evaluations if e.proposal_id == proposal.proposal_id)
    if not relevant:
        reasons.append("no evaluation for proposal")
    if relevant and not all(e.passed for e in relevant):
        reasons.append("one or more evaluations failed")

    covered = {scenario for evaluation in relevant for scenario in evaluation.scenario_refs}
    missing_scenarios = set(proposal.required_scenarios) - covered
    if missing_scenarios:
        reasons.append(f"required evaluation scenarios missing: {sorted(missing_scenarios)}")

    acceptance_covered = {name for evaluation in relevant for name in evaluation.acceptance_checks}
    missing_acceptance = set(proposal.required_acceptance_checks) - acceptance_covered
    if missing_acceptance:
        reasons.append(f"required acceptance checks missing: {sorted(missing_acceptance)}")

    if any(e.regression_failures for e in relevant):
        reasons.append("regression failures remain")
    if any(e.blocking_findings for e in relevant):
        reasons.append("blocking verification findings remain")

    max_round = max((e.verification_round for e in relevant), default=0)
    if max_round > proposal.verification_round_limit:
        reasons.append("verification round budget exceeded")
    paid_reviews = sum(e.independent_paid_reviews_used for e in relevant)
    if paid_reviews > proposal.independent_paid_review_budget:
        reasons.append("independent paid review budget exceeded")

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
