import pytest

from uaos.contracts.context import ContextPacket, GovernanceFrame, ParentGuidance, ParentUpcall
from uaos.contracts.context_budget import ContextBudget, validate_context_budget
from uaos.kernel import CognitiveSearchMode, DeliberationSignals, assess_deliberation


def test_low_risk_familiar_work_does_not_force_meta_process():
    d=assess_deliberation(DeliberationSignals())
    assert not d.required
    assert not d.external_research_required
    assert not d.independent_verification_required
    assert d.search_mode is CognitiveSearchMode.LIGHTWEIGHT


def test_single_failure_keeps_reflection_compact_without_mandatory_external_research():
    d=assess_deliberation(DeliberationSignals(repeated_failure_count=1))
    assert d.required and d.micro_diagnosis_required
    assert d.macro_alignment_required
    assert d.governing_assumptions_challenge_required
    assert not d.external_research_required
    assert d.search_mode is CognitiveSearchMode.LIGHTWEIGHT


def test_user_correction_uses_contrastive_search_and_counterexamples():
    d=assess_deliberation(DeliberationSignals(user_correction=True,change_proposal=True))
    assert d.required and d.micro_diagnosis_required and d.macro_alignment_required
    assert d.governing_assumptions_challenge_required
    assert d.counterexample_search_required
    assert d.search_mode is CognitiveSearchMode.CONTRASTIVE
    assert d.min_hypotheses == 2 and d.min_action_candidates == 2


def test_architecture_gap_forces_structured_external_research():
    d=assess_deliberation(DeliberationSignals(architecture_gap=True))
    assert d.external_research_required
    assert d.macro_alignment_required
    assert d.governing_assumptions_challenge_required
    assert d.search_mode is CognitiveSearchMode.STRUCTURED


def test_conflicting_evidence_has_structured_search_and_independent_verification():
    d=assess_deliberation(DeliberationSignals(conflicting_evidence=True))
    assert d.external_research_required
    assert d.macro_alignment_required
    assert d.governing_assumptions_challenge_required
    assert d.independent_verification_required and d.counterexample_search_required
    assert d.no_change_baseline_required


def test_high_risk_without_detected_problem_escalates_verification_and_structured_search():
    d=assess_deliberation(DeliberationSignals(high_risk=True))
    assert d.independent_verification_required and d.counterexample_search_required
    assert d.external_research_required
    assert d.search_mode is CognitiveSearchMode.STRUCTURED


def test_repeated_failure_uses_structured_search_instead_of_another_local_patch():
    d=assess_deliberation(DeliberationSignals(repeated_failure_count=2,complexity_increasing=True))
    assert d.macro_alignment_required
    assert d.governing_assumptions_challenge_required
    assert d.external_research_required
    assert d.counterexample_search_required
    assert d.min_action_candidates == 3
    assert d.max_deliberation_rounds == 3


def test_parent_upcall_preserves_child_identity_and_carries_unknowns():
    upcall=ParentUpcall(
        task_id="video:ip",
        child_authority="DOMAIN:video",
        problem_statement="local fix keeps increasing complexity",
        requested_outcome="parent diagnosis and replan guidance",
        evidence_refs=("e1",),
        unknowns=("whether architecture is wrong",),
    )
    guidance=ParentGuidance(
        parent_authority="UAOS",
        task_id=upcall.task_id,
        directive="challenge governing assumption before another repair",
        goal_link="preserve final project objective",
        external_research_required=True,
        child_may_resume=True,
    )
    assert upcall.child_authority=="DOMAIN:video"
    assert guidance.task_id==upcall.task_id and guidance.child_may_resume


def test_context_packet_carries_bounded_governance_frame():
    frame=GovernanceFrame(
        parent_goal="ship the correct product",
        local_goal_link="this work removes the current blocker",
        non_goals=("do not redesign unrelated systems",),
        invariants=("single controller",),
        autonomy_bounds=("local reversible repair",),
        escalation_conditions=("scope crosses subsystem",),
        stop_conditions=("done-condition is demonstrably closer",),
        verification_expectations=("counterexample test",),
    )
    packet=ContextPacket("t","w","goal","done",(),(),(),(),(),{},frame)
    validate_context_budget(packet,ContextBudget(max_governance_items=8))
    with pytest.raises(ValueError,match="governance items"):
        validate_context_budget(packet,ContextBudget(max_governance_items=7))
