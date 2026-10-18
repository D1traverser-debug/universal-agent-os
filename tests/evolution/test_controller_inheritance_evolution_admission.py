"""Exercise the canonical evolution admission for a controller inheritance gap.

This is repository-side admission, not ChatGPT native-session assurance.
"""
import json
from pathlib import Path

from uaos.evolution import (
    ChangeProposal, ComplexityBudget, ComplexityDelta, EvaluationResult,
    EvolutionDepthTrace, EvolutionOrigin, EvolutionOriginKind,
    EvolutionTransaction, EvolutionTransactionStage,
    ProposalState, admit_discovery, admit_evaluation, admit_proposal,
)
from uaos.kernel.problem_space import CapabilityDiscoveryReceipt, DiscoveryLens

ROOT = Path(__file__).resolve().parents[2]


def test_controller_review_discovery_and_evaluation_use_existing_transaction():
    observation = json.loads(
        (ROOT / "state/observations/uaos-controller-five-repo-review-20261018.json")
        .read_text(encoding="utf-8")
    )
    assert observation["counts"]["registered_repositories"] == 5
    assert observation["counts"]["mapped_dimensions"] == 30
    assert observation["counts"]["deep_validated_dimensions"] == 0

    origin_ref = "config/SESSION_INTERACTION_POLICY.json"
    judge_ref = "ci:repository-controller-review-tests"
    tx = EvolutionTransaction(
        transaction_id="EVO-20261018-INHERITANCE-REVIEW",
        origin=EvolutionOrigin(
            kind=EvolutionOriginKind.CAPABILITY_GAP,
            origin_ids=("gap:inheritance-proactive-coverage",),
            evidence_refs=(origin_ref,),
        ),
        depth_trace=EvolutionDepthTrace(
            governing_outcome="Require source-bound all-domain review when UAOS controller is selected",
            raw_evidence_refs=(origin_ref, "state/observations/uaos-controller-five-repo-review-20261018.json"),
            professional_method_refs=(
                "research:architecture-tradeoffs",
                "research:sre-observability",
                "research:risk-management-and-evals",
            ),
            external_judge_refs=(judge_ref,),
            novelty_probe_refs=("probe:unassessed-controller-entry-gaps",),
        ),
    )
    discovery = CapabilityDiscoveryReceipt(
        source_id="registered-uaos-and-independent-research",
        source_axes=("entry-runtime", "outcomes-and-assurance"),
        lenses=(DiscoveryLens.WORKFLOW_OR_HANDOFF, DiscoveryLens.ADJACENT_DOMAIN),
        latent_gap_candidates=("gap:inheritance-proactive-coverage",),
        evidence_refs=(origin_ref, "state/observations/uaos-controller-five-repo-review-20261018.json"),
    )
    tx = admit_discovery(tx, discovery)
    proposal = ChangeProposal(
        proposal_id="proposal:controller-inheritance-review",
        title="Use existing controller selection for active system review",
        failure_class_ids=(),
        hypothesis="Resume-only controller routing misses latent cross-domain gaps",
        target_scope="UAOS controller selection",
        added_mechanisms=(),
        replaced_mechanisms=("resume-only selection semantics",),
        retired_mechanisms=(),
        why_not_reuse="",
        retirement_rationale="",
        rollback_plan="Revert the candidate session-policy and native profile projection",
        expected_benefit="Source coverage gaps stay visible without user reminders",
        new_failure_modes=("High review cost per controller selection",),
        required_scenarios=("scenario:five-repo-review",),
        complexity_delta=ComplexityDelta(),
        evidence_refs=(origin_ref,),
        state=ProposalState.DRAFT,
        capability_gap_ids=("gap:inheritance-proactive-coverage",),
        required_acceptance_checks=("source-coverage-is-not-deep-proof", "projection-under-budget"),
    )
    tx = admit_proposal(tx, proposal)
    profile_len = len(
        (ROOT / "config/NATIVE_SESSION_RUNTIME_PROFILE.json").read_text(encoding="utf-8")
    )
    evaluation = EvaluationResult(
        evaluation_id="eval:controller-inheritance-synthetic-admission",
        proposal_id=proposal.proposal_id,
        scenario_refs=("scenario:five-repo-review",),
        metrics_before={"controller_review_explicit": 0.0},
        metrics_after={"controller_review_explicit": 1.0},
        acceptance_checks={
            "source-coverage-is-not-deep-proof": observation["outcome"].startswith("NOT_GREEN"),
            "projection-under-budget": profile_len <= 12000,
        },
        passed=True,
        evidence_refs=(judge_ref, "test:controller-inheritance-review"),
    )
    tx = admit_evaluation(tx, (evaluation,), budget=ComplexityBudget())
    assert tx.stage is EvolutionTransactionStage.EVALUATED
    assert tx.authorization is not None and tx.authorization.approved
    # Do NOT pretend a test promoted this PR or observed native ChatGPT triggering.
