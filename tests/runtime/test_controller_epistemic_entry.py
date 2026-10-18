"""Controlled UAOS entry tests: user/model assertions are not causal authority.

These tests prove the local admission wiring when invoked. They do NOT prove
native ChatGPT automatically intercepts every turn.
"""
from dataclasses import replace
from hashlib import sha256

import pytest

from uaos.kernel.cognition_case import EvidenceItem, EvidenceKind

from uaos.runtime.epistemic_entry import (
    ControllerEpistemicEntry,
    TurnEvolutionCoverage,
    TurnUtteranceAssessment,
    UtteranceOrigin,
    EntryAdmissionError,
    EntryObservation,
    EntrySignal,
    assess_controller_epistemic_entry,
)
from uaos.runtime.finalization import (
    FinalizationBlocked,
    FinalizationContext,
    admit_final_response,
)


def _entry(signal=EntrySignal.NO_MATERIAL_GAP, kind=EvidenceKind.REPOSITORY_FACT):
    return ControllerEpistemicEntry(
        objective_ref="main:state/tasks/controller.json#goal",
        state_ref="main:state/TASK_INDEX.json#controller_tasks",
        observations=(EntryObservation(
            signal=signal,
            evidence=EvidenceItem(
                "entry:current", kind,
                "Current selected-controller source observation",
                "main:config/SESSION_INTERACTION_POLICY.json",
            ),
        ),),
        governing_assumption_review_ref="review:assumptions-vs-evidence",
        next_action_ref="state:next-executable-action",
    )


def _report():
    return """Controller entry sampled.

当前 Agent：UAOS
当前范围或任务：controlled epistemic entry test
Authority：UAOS
状态：VERIFIED_CONTROLLED_ONLY
当前阶段：FINALIZATION
下一动作或阻塞：no remaining action on this controlled synthetic turn
Evolution：NO_EVOLUTION_TRIGGER
Deliberation：NOT_TRIGGERED
版本：UAOS test
进度时间：2026-10-18 16:38:00（北京时间）
"""


def _review(response: str):
    user_text = "controlled synthetic current user input"
    return TurnEvolutionCoverage(
        observed_source_refs=("test:current-user", "test:assistant-final"),
        assessments=(
            TurnUtteranceAssessment(
                source_ref="test:current-user", origin=UtteranceOrigin.USER,
                source_sha256=sha256(user_text.encode()).hexdigest(),
                signal=EntrySignal.NO_MATERIAL_GAP,
                judgment_evidence_ref="test:judged-user",
                alternative_or_no_gap_reason_ref="test:challenge-user",
            ),
            TurnUtteranceAssessment(
                source_ref="test:assistant-final", origin=UtteranceOrigin.ASSISTANT,
                source_sha256=sha256(response.encode()).hexdigest(),
                signal=EntrySignal.NO_MATERIAL_GAP,
                judgment_evidence_ref="test:judged-assistant",
                alternative_or_no_gap_reason_ref="test:challenge-assistant",
            ),
        ),
        assistant_final_ref="test:assistant-final",
        evolution_routing_ref="test:no-durable-evolution-trigger",
    )


def _turn_source_verifier(ref: str, digest: str) -> bool:
    return ref == "test:current-user" and digest == sha256(
        b"controlled synthetic current user input"
    ).hexdigest()


def _context(entry=None, **overrides):
    base = dict(
        context_selected=True,
        controller_selected=True,
        controller_epistemic_entry=entry,
        entry_evidence_verifier=lambda _ref: True,
        turn_evolution_coverage=_review(_report()),
        observed_turn_source_refs=("test:current-user", "test:assistant-final"),
        turn_source_digest_verifier=_turn_source_verifier,
        turn_judgment_verifier=lambda ref: ref.startswith("test:"),
    )
    base.update(overrides)
    return FinalizationContext(**base)


def test_selected_controller_cannot_skip_the_canonical_entry():
    with pytest.raises(FinalizationBlocked, match="MISSING_CONTROLLER_EPISTEMIC_ENTRY"):
        admit_final_response(_report(), _context())


def test_selected_controller_needs_verifiable_runtime_observations():
    with pytest.raises(FinalizationBlocked, match="MISSING_CONTROLLER_ENTRY_EVIDENCE_VERIFIER"):
        admit_final_response(_report(), _context(_entry(), entry_evidence_verifier=None))
    with pytest.raises(FinalizationBlocked, match="CONTROLLER_ENTRY_EVIDENCE_UNVERIFIED"):
        admit_final_response(
            _report(),
            _context(_entry(), entry_evidence_verifier=lambda _ref: False),
        )


def test_user_proposed_fix_is_not_automatically_a_confirmed_defect():
    item = _entry(
        EntrySignal.SYSTEM_OR_RULE_CONTRADICTION, EvidenceKind.USER_CLAIM,
    )
    receipt = assess_controller_epistemic_entry(item)
    assert receipt.hypothesis_challenge_required
    assert not receipt.problem_signal_observed
    assert not receipt.deep_learning_required
    admit_final_response(_report(), _context(item))


def test_source_only_governing_rule_contradiction_forces_cognition_without_user_reminder():
    item = _entry(EntrySignal.SYSTEM_OR_RULE_CONTRADICTION)
    assessment = assess_controller_epistemic_entry(item)
    assert assessment.problem_signal_observed and assessment.hypothesis_challenge_required
    with pytest.raises(FinalizationBlocked, match="UNROUTED_RULE_OR_SYSTEM_CONTRADICTION"):
        admit_final_response(_report(), _context(item))
    with pytest.raises(FinalizationBlocked, match="MISSING_PROBLEM_CLOSURE_SIGNALS"):
        admit_final_response(_report(), _context(item, problem_signal_observed=True))


def test_material_knowledge_gap_cannot_be_downgraded_to_simple_query():
    item = _entry(EntrySignal.MATERIAL_KNOWLEDGE_GAP, EvidenceKind.TEST_RESULT)
    assert assess_controller_epistemic_entry(item).deep_learning_required
    with pytest.raises(FinalizationBlocked, match="UNROUTED_MATERIAL_KNOWLEDGE_GAP"):
        admit_final_response(_report(), _context(item))
    with pytest.raises(FinalizationBlocked, match="MISSING_DEEP_TASK_EVIDENCE_CASE"):
        admit_final_response(_report(), _context(item, deep_task_required=True))


def test_unfinished_controller_work_forces_actual_continuation():
    item = _entry(EntrySignal.UNFINISHED_AUTHORIZED_WORK)
    assert assess_controller_epistemic_entry(item).work_remaining
    with pytest.raises(FinalizationBlocked, match="UNROUTED_UNFINISHED_AUTHORIZED_WORK"):
        admit_final_response(_report(), _context(item))
    with pytest.raises(FinalizationBlocked, match="ACTIONABLE_WORK_REMAINS_WITHOUT_USER_INPUT"):
        admit_final_response(
            _report(), _context(item, work_remaining_without_user_input=True)
        )


def test_clean_entry_reaches_existing_finalization_without_extra_ceremony():
    receipt = admit_final_response(_report(), _context(_entry()))
    assert receipt.adherence.passed


def test_missing_or_conflicting_evidence_cannot_dress_as_clean():
    with pytest.raises(ValueError, match="evidence identity, statement and source_ref"):
        EntryObservation(
            signal=EntrySignal.NO_MATERIAL_GAP,
            evidence=EvidenceItem("bad", EvidenceKind.REPOSITORY_FACT, "claim", ""),
        )
    base = _entry()
    with pytest.raises(EntryAdmissionError, match="distinct"):
        assess_controller_epistemic_entry(
            replace(base, observations=(base.observations[0], base.observations[0]))
        )
    with pytest.raises(EntryAdmissionError, match="contradicts"):
        assess_controller_epistemic_entry(
            replace(base, observations=(
                base.observations[0],
                EntryObservation(
                    EntrySignal.SYSTEM_OR_RULE_CONTRADICTION,
                    EvidenceItem(
                        "entry:counterexample", EvidenceKind.TEST_RESULT,
                        "Actual contradictory contract",
                        "test://fresh-counterexample",
                    ),
                ),
            ))
        )

def test_fresh_tool_observation_escalates_unprompted_system_failure():
    # Tool observations are a first-class fact when the host verifies provenance.
    contradiction = _entry(EntrySignal.SYSTEM_OR_RULE_CONTRADICTION, EvidenceKind.TOOL_RESULT)
    receipt = assess_controller_epistemic_entry(contradiction)
    assert receipt.problem_signal_observed and receipt.hypothesis_challenge_required
    with pytest.raises(FinalizationBlocked, match="UNROUTED_RULE_OR_SYSTEM_CONTRADICTION"):
        admit_final_response(_report(), _context(contradiction))
    with pytest.raises(FinalizationBlocked, match="CONTROLLER_ENTRY_EVIDENCE_UNVERIFIED"):
        admit_final_response(
            _report(), _context(contradiction, entry_evidence_verifier=lambda ref: not ref.startswith("main:config")),
        )


def test_tool_found_material_method_gap_forces_deep_research_without_user_request():
    gap = _entry(EntrySignal.MATERIAL_KNOWLEDGE_GAP, EvidenceKind.TOOL_RESULT)
    receipt = assess_controller_epistemic_entry(gap)
    assert receipt.deep_learning_required and not receipt.problem_signal_observed
    with pytest.raises(FinalizationBlocked, match="UNROUTED_MATERIAL_KNOWLEDGE_GAP"):
        admit_final_response(_report(), _context(gap))


def test_model_only_analysis_or_synthetic_scenario_cannot_self_certify_tool_findings():
    for kind in (EvidenceKind.ANALYSIS_RESULT, EvidenceKind.SCENARIO_RESULT, EvidenceKind.USER_CLAIM):
        item = _entry(EntrySignal.SYSTEM_OR_RULE_CONTRADICTION, kind)
        receipt = assess_controller_epistemic_entry(item)
        assert not receipt.problem_signal_observed
        assert receipt.hypothesis_challenge_required


def test_exact_controller_entry_requires_owner_source_and_rejects_false_done():
    import json
    from pathlib import Path
    ref = "state/tasks/uaos-inheritance-review-20261018.json"
    state = json.loads((Path(__file__).resolve().parents[2] / ref).read_text(encoding="utf-8"))
    entry = replace(_entry(), state_ref=ref)
    report = _report().replace(
        "当前范围或任务：controlled epistemic entry test",
        f"当前范围或任务：{state['task_id']}",
    ).replace("状态：VERIFIED_CONTROLLED_ONLY", f"状态：{state['status']}").replace(
        "当前阶段：FINALIZATION", f"当前阶段：{state['current_stage']}"
    )

    with pytest.raises(FinalizationBlocked, match="CONTROLLER_TASK_PROGRESS_SOURCE_NOT_BOUND"):
        admit_final_response(report, _context(entry))

    with pytest.raises(FinalizationBlocked, match="CONTROLLER_TASK_PROGRESS_READER_MISSING"):
        admit_final_response(report, _context(entry, authoritative_task_ref=ref))

    bound = _context(entry, authoritative_task_ref=ref, read_authoritative_task=lambda _: state,
                     turn_evolution_coverage=_review(report))
    assert admit_final_response(report, bound).adherence.passed
    with pytest.raises(FinalizationBlocked, match="AUTHORITATIVE_PROGRESS_MISMATCH"):
        admit_final_response(report.replace(f"状态：{state['status']}", "状态：COMPLETE"), bound)


def test_controlled_finalization_requires_evolution_review_of_actual_user_and_assistant_turn():
    with pytest.raises(FinalizationBlocked, match="MISSING_ALL_UTTERANCE_EVOLUTION_REVIEW"):
        admit_final_response(
            _report(), _context(_entry(), turn_evolution_coverage=None)
        )

    incomplete = replace(
        _review(_report()),
        assessments=(_review(_report()).assessments[-1],),
    )
    with pytest.raises(FinalizationBlocked, match="not every user/assistant/tool/state utterance"):
        admit_final_response(
            _report(), _context(_entry(), turn_evolution_coverage=incomplete)
        )


def test_post_output_new_problem_cannot_be_silently_marked_clean():
    reviewed = _review(_report())
    contradictory_assistant = replace(
        reviewed.assessments[1],
        signal=EntrySignal.SYSTEM_OR_RULE_CONTRADICTION,
    )
    review = replace(reviewed, assessments=(reviewed.assessments[0], contradictory_assistant))
    with pytest.raises(FinalizationBlocked, match="UNROUTED_POST_DRAFT_SYSTEM_OR_RULE_CONTRADICTION"):
        admit_final_response(
            _report(), _context(_entry(), turn_evolution_coverage=review)
        )


def test_user_claim_cannot_pass_as_unquestioned_clean_without_canonical_challenge():
    reviewed = _review(_report())
    user_claim = replace(
        reviewed.assessments[0],
        signal=EntrySignal.CLAIM_OR_CAUSAL_SUGGESTION,
    )
    review = replace(reviewed, assessments=(user_claim, reviewed.assessments[1]))
    with pytest.raises(FinalizationBlocked, match="UNROUTED_POST_DRAFT_CHALLENGE_SIGNAL"):
        admit_final_response(
            _report(), _context(_entry(), turn_evolution_coverage=review)
        )


def test_post_output_unfinished_work_cannot_close_as_clean_challenge():
    reviewed = _review(_report())
    output_work = replace(
        reviewed.assessments[1],
        signal=EntrySignal.UNFINISHED_AUTHORIZED_WORK,
    )
    review = replace(reviewed, assessments=(reviewed.assessments[0], output_work))
    with pytest.raises(FinalizationBlocked, match="UNROUTED_POST_DRAFT_UNFINISHED_AUTHORIZED_WORK"):
        admit_final_response(_report(), _context(_entry(), turn_evolution_coverage=review))
