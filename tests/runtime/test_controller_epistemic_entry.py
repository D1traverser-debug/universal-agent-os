"""Controlled UAOS entry tests: user/model assertions are not causal authority.

These tests prove the local admission wiring when invoked. They do NOT prove
native ChatGPT automatically intercepts every turn.
"""
from dataclasses import replace

import pytest

from uaos.kernel.cognition_case import EvidenceItem, EvidenceKind

from uaos.runtime.epistemic_entry import (
    ControllerEpistemicEntry,
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


def _context(entry=None, **overrides):
    base = dict(
        context_selected=True,
        controller_selected=True,
        controller_epistemic_entry=entry,
        entry_evidence_verifier=lambda _ref: True,
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
