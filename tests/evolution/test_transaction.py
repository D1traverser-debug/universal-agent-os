import pytest

from uaos.evolution import (
    ChangeProposal,
    ComplexityBudget,
    ComplexityDelta,
    EvaluationResult,
    EvolutionDepthTrace,
    EvolutionOrigin,
    EvolutionOriginKind,
    EvolutionTransaction,
    EvolutionTransactionError,
    EvolutionTransactionStage,
    PostPromotionObservation,
    ProposalState,
    admit_discovery,
    admit_evaluation,
    admit_proposal,
    authorize,
    observe,
    record_promotion,
)
from uaos.kernel.problem_space import CapabilityDiscoveryReceipt, DiscoveryLens


def depth(*, novelty=("probe:unknown-signal",), stretch=None, feasibility=()):
    return EvolutionDepthTrace(
        governing_outcome="discover useful missing capabilities before incidents",
        raw_evidence_refs=("raw:repo", "raw:runtime"),
        professional_method_refs=("method:nist-monitoring", "method:atam"),
        external_judge_refs=("judge:ci", "judge:holdout"),
        novelty_probe_refs=novelty,
        stretch_target=stretch,
        stretch_target_feasibility_refs=feasibility,
    )


def tx():
    return EvolutionTransaction(
        transaction_id="evo:proactive",
        origin=EvolutionOrigin(
            EvolutionOriginKind.CAPABILITY_GAP,
            ("gap:proactive-learning",),
            ("evidence:workflow-scan",),
        ),
        depth_trace=depth(),
    )


def discovery():
    return CapabilityDiscoveryReceipt(
        source_id="uaos+external-methods",
        source_axes=("workflow", "assurance"),
        lenses=(DiscoveryLens.WORKFLOW_OR_HANDOFF, DiscoveryLens.ADJACENT_DOMAIN),
        latent_gap_candidates=("gap:proactive-learning",),
        evidence_refs=("evidence:workflow-scan", "evidence:external-methods"),
    )


def proposal(*, gap_ids=("gap:proactive-learning",)):
    return ChangeProposal(
        proposal_id="p:proactive-evolution",
        title="canonical proactive evolution transaction",
        failure_class_ids=(),
        hypothesis="gap:proactive-learning exists because discovery and promotion have no transaction owner",
        target_scope="uaos.evolution",
        added_mechanisms=(),
        replaced_mechanisms=("fragmented evolution orchestration",),
        retired_mechanisms=(),
        why_not_reuse="existing helpers remain reusable but cannot own the end-to-end transaction",
        retirement_rationale="helpers become compatibility/internal mechanisms under one transaction owner",
        rollback_plan="revert transaction integration and restore helper-first routing",
        expected_benefit="proactive learning cannot stop between discovery, evaluation, promotion and observation",
        new_failure_modes=("transaction admission too strict",),
        required_scenarios=("scenario:proactive-gap-to-promotion",),
        complexity_delta=ComplexityDelta(added_components=1, removed_components=1),
        evidence_refs=("evidence:workflow-scan", "evidence:external-methods"),
        state=ProposalState.DRAFT,
        capability_gap_ids=gap_ids,
    )


def evaluation():
    return EvaluationResult(
        evaluation_id="eval:proactive",
        proposal_id="p:proactive-evolution",
        scenario_refs=("scenario:proactive-gap-to-promotion",),
        metrics_before={"orphaned_gap_path": 1.0},
        metrics_after={"orphaned_gap_path": 0.0},
        acceptance_checks={
            "gap_is_first_class_origin": True,
            "stages_cannot_be_skipped": True,
            "independent_judge_declared": True,
        },
        passed=True,
        evidence_refs=("test:transaction", "judge:ci"),
    )


def test_depth_trace_requires_raw_method_and_external_judge():
    with pytest.raises(ValueError, match="raw evidence"):
        EvolutionDepthTrace("goal", (), ("method:x",), ("judge:x",))
    with pytest.raises(ValueError, match="professional method"):
        EvolutionDepthTrace("goal", ("raw:x",), (), ("judge:x",))
    with pytest.raises(ValueError, match="external judge"):
        EvolutionDepthTrace("goal", ("raw:x",), ("method:x",), ())


def test_stretch_target_is_search_constraint_not_unverified_assertion():
    with pytest.raises(ValueError, match="feasibility"):
        depth(stretch="reduce decision latency by 10x")
    trace = depth(stretch="reduce decision latency by 10x", feasibility=("benchmark:baseline",))
    assert trace.stretch_target is not None


def test_capability_gap_requires_broad_discovery_and_novelty_probe():
    no_novelty = EvolutionTransaction(
        "evo:no-novelty",
        EvolutionOrigin(EvolutionOriginKind.CAPABILITY_GAP, ("gap:x",), ("evidence:x",)),
        depth(novelty=()),
    )
    with pytest.raises(EvolutionTransactionError, match="novelty"):
        admit_discovery(no_novelty, discovery())
    with pytest.raises(EvolutionTransactionError, match="outside-in"):
        admit_discovery(tx(), None)


def test_discovered_gap_is_first_class_proposal_origin():
    discovered = admit_discovery(tx(), discovery())
    proposed = admit_proposal(discovered, proposal())
    assert proposed.proposal.capability_gap_ids == ("gap:proactive-learning",)
    assert proposed.stage is EvolutionTransactionStage.PROPOSED


def test_proposal_cannot_invent_gap_not_present_in_discovery():
    discovered = admit_discovery(tx(), discovery())
    with pytest.raises(EvolutionTransactionError, match="not traceable"):
        admit_proposal(discovered, proposal(gap_ids=("gap:invented",)))


def test_transaction_cannot_skip_discovery_or_evaluation():
    with pytest.raises(EvolutionTransactionError, match="expected stage"):
        admit_proposal(tx(), proposal())
    discovered = admit_discovery(tx(), discovery())
    proposed = admit_proposal(discovered, proposal())
    with pytest.raises(EvolutionTransactionError, match="expected stage"):
        authorize(proposed)


def test_proactive_evolution_reaches_observation_only_through_full_transaction():
    current = admit_discovery(tx(), discovery())
    current = admit_proposal(current, proposal())
    current = admit_evaluation(current, (evaluation(),), budget=ComplexityBudget())
    current = authorize(current)
    current = record_promotion(current, execution_evidence_refs=("execution:pr-merge",))
    current = observe(
        current,
        (
            PostPromotionObservation(
                "obs:proactive",
                "p:proactive-evolution",
                True,
                {"orphaned_gap_path": 0.0},
                ("runtime:post-promotion",),
            ),
        ),
    )
    assert current.stage is EvolutionTransactionStage.OBSERVED
    assert current.recommendation == "KEEP_OBSERVING"
