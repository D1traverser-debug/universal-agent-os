"""Blocked tool action != blocked task: controlled finalization negative controls."""
from dataclasses import replace
from hashlib import sha256

import pytest

from uaos.kernel.cognition_case import EvidenceItem, EvidenceKind
from uaos.runtime.epistemic_entry import (
    ControllerEpistemicEntry, EntryObservation, EntrySignal,
    TurnEvolutionCoverage, TurnUtteranceAssessment, UtteranceOrigin,
)
from uaos.runtime.finalization import (
    BlockedOperationContinuity, FinalizationBlocked, FinalizationContext,
    PermittedContinuationStep, admit_final_response,
)


def _entry():
    return ControllerEpistemicEntry(
        objective_ref="source:goal",
        state_ref="source:task",
        governing_assumption_review_ref="source:causal-challenge",
        next_action_ref="source:next-action",
        observations=(
            EntryObservation(
                EntrySignal.NO_MATERIAL_GAP,
                EvidenceItem(
                    "e:current", EvidenceKind.REPOSITORY_FACT,
                    "The controlled runtime has current authority.", "source:main",
                ),
            ),
        ),
    )


def _report():
    return """当前 Agent：UAOS
当前范围或任务：controlled blocked-operation test
Authority：UAOS
状态：RUNNING
当前阶段：blocked operation with independent safe continuation
下一动作或阻塞：安全阻断保留；已完成独立只读研究并记录后续恢复点
Evolution：NO_EVOLUTION_TRIGGER
Deliberation：NOT_TRIGGERED
版本：controlled fixture
进度时间：2026-10-18
"""


def _turn_coverage():
    return TurnEvolutionCoverage(
        observed_source_refs=("test:blocked-user", "test:blocked-agent"),
        assessments=(
            TurnUtteranceAssessment(
                source_ref="test:blocked-user", origin=UtteranceOrigin.USER,
                source_sha256=sha256(b"blocked operation current user input").hexdigest(),
                signal=EntrySignal.NO_MATERIAL_GAP,
                judgment_evidence_ref="test:user-judgment",
                alternative_or_no_gap_reason_ref="test:user-counterexample",
            ),
            TurnUtteranceAssessment(
                source_ref="test:blocked-agent", origin=UtteranceOrigin.ASSISTANT,
                source_sha256=sha256(_report().encode()).hexdigest(),
                signal=EntrySignal.NO_MATERIAL_GAP,
                judgment_evidence_ref="test:assistant-judgment",
                alternative_or_no_gap_reason_ref="test:assistant-counterexample",
            ),
        ),
        assistant_final_ref="test:blocked-agent",
        evolution_routing_ref="test:blocked-operation-evolution-triage",
    )


def _step(*, attempted=False, outcome_ref=None, read_only=True):
    return PermittedContinuationStep(
        action_ref="action:read-current-authority",
        admission_ref="admission:read-only-authorized",
        read_only=read_only,
        attempted=attempted,
        outcome_evidence_ref=outcome_ref,
    )


def _case(*steps, safety_denial=True):
    return BlockedOperationContinuity(
        blocked_operation_ref="action:write-branch",
        blocker_evidence_ref="tool:safety-denial",
        checkpoint_ref="state:resumable-task",
        safety_denial=safety_denial,
        remaining_permitted_steps=steps,
    )


def _ctx(case=None, **changes):
    values = {
        "context_selected": True,
        "controller_selected": True,
        "controller_epistemic_entry": _entry(),
        "entry_evidence_verifier": lambda _: True,
        "turn_evolution_coverage": _turn_coverage(),
        "observed_turn_source_refs": ("test:blocked-user", "test:blocked-agent"),
        "observed_turn_source_origins": {"test:blocked-user": UtteranceOrigin.USER, "test:blocked-agent": UtteranceOrigin.ASSISTANT},
        "turn_source_digest_verifier": lambda ref, digest: ref == "test:blocked-user" and digest == sha256(b"blocked operation current user input").hexdigest(),
        "turn_judgment_verifier": lambda ref: ref.startswith("test:"),
        "blocked_tool_operation_observed": True,
        "blocked_operation_continuity": case,
    }
    values.update(changes)
    return FinalizationContext(**values)


def test_blocked_write_cannot_end_turn_while_permitted_read_remains_unattempted():
    with pytest.raises(FinalizationBlocked, match="PERMITTED_INDEPENDENT_WORK_UNATTEMPTED"):
        admit_final_response(_report(), _ctx(_case(_step())))


def test_blocked_write_cannot_switch_to_other_mutating_provider_after_safety_denial():
    with pytest.raises(FinalizationBlocked, match="SAFETY_DENIED_MUTATION_MUST_NOT_BE_REROUTED"):
        admit_final_response(
            _report(), _ctx(_case(_step(read_only=False, attempted=True, outcome_ref="tool:mutation")))
        )


def test_unverified_or_self_attested_alternative_does_not_count_as_followthrough():
    case = _case(_step(attempted=True, outcome_ref="tool:read-outcome"))
    with pytest.raises(FinalizationBlocked, match="PERMITTED_INDEPENDENT_WORK_OUTCOME_UNVERIFIED"):
        admit_final_response(
            _report(),
            _ctx(case, entry_evidence_verifier=lambda ref: ref != "tool:read-outcome"),
        )
    with pytest.raises(FinalizationBlocked, match="BLOCKED_OPERATION_ALTERNATIVE_NOT_ADMITTED"):
        admit_final_response(
            _report(),
            _ctx(case, entry_evidence_verifier=lambda ref: ref != "admission:read-only-authorized"),
        )


def test_missing_blocked_write_evidence_is_not_replaced_by_blind_final_answer():
    with pytest.raises(FinalizationBlocked, match="MISSING_BLOCKED_OPERATION_CONTINUATION_EVIDENCE"):
        admit_final_response(_report(), _ctx())
    with pytest.raises(FinalizationBlocked, match="BLOCKED_OPERATION_EVIDENCE_UNVERIFIED"):
        admit_final_response(
            _report(), _ctx(_case(), entry_evidence_verifier=lambda ref: ref != "tool:safety-denial")
        )


def test_actual_read_only_followthrough_then_checkpoint_is_admissible():
    receipt = admit_final_response(
        _report(), _ctx(_case(_step(attempted=True, outcome_ref="tool:read-outcome")))
    )
    assert receipt.adherence.passed
    assert receipt.closure_decision.value == "CLEAN_NO_PROBLEM"


def test_genuine_no_alternative_blocker_can_keep_task_open_with_checkpoint():
    receipt = admit_final_response(_report(), _ctx(_case()))
    assert receipt.adherence.passed


def test_no_spurious_blocker_ceremony_on_simple_controller_turn():
    receipt = admit_final_response(
        _report(),
        _ctx(
            None,
            blocked_tool_operation_observed=False,
            blocked_operation_continuity=None,
        ),
    )
    assert receipt.adherence.passed


def test_one_blocker_cannot_be_forged_into_an_unrelated_clean_turn():
    with pytest.raises(FinalizationBlocked, match="BLOCKED_OPERATION_EVIDENCE_WITHOUT_CONTROLLED_TRIGGER"):
        admit_final_response(
            _report(),
            _ctx(_case(), blocked_tool_operation_observed=False),
        )


def test_continuation_attempt_requires_real_outcome_reference():
    with pytest.raises(ValueError, match="attempt and outcome evidence"):
        _step(attempted=True)
    with pytest.raises(ValueError, match="duplicate continuation"):
        _case(_step(), _step())
