import json
from pathlib import Path

from uaos.kernel.deliberation import (
    DeliberationEvidence,
    DeliberationSignals,
    HypothesisDisposition,
    ProblemHypothesis,
    ProblemLayer,
    RootScopeAssessment,
    require_root_scope_admission,
)
from uaos.kernel.problem_closure import EvolutionDisposition
from uaos.observability.session_adherence import (
    POLICY_REQUIRED_PROGRESS_FIELDS,
    POLICY_TO_CANONICAL_FIELD,
    REQUIRED_PROGRESS_FIELDS,
    SessionAdherenceViolation,
    SessionProgressExpectation,
    evaluate_session_progress_response,
    summarize_session_adherence,
)

ROOT = Path(__file__).resolve().parents[2]


def _policy():
    return json.loads((ROOT / "config/SESSION_INTERACTION_POLICY.json").read_text(encoding="utf-8"))


def _good_report(*, problem: bool, next_action: str = "continue scenario replay") -> str:
    evolution = "EVALUATED_NO_DURABLE_EVOLUTION" if problem else "NO_EVOLUTION_TRIGGER"
    deliberation = "TRIGGERED__USER_CORRECTION_VERIFIED" if problem else "NOT_TRIGGERED"
    return f"""Work completed.

当前 Agent：UAOS
当前范围：session adherence replay
Authority：UAOS
状态：OBSERVING
当前阶段：LIVE_DOGFOOD
下一动作：{next_action}
Evolution：{evolution}
Deliberation：{deliberation}
版本：UAOS 2.5.2 / Session 1.9.0
进度时间：2026-10-16 10:45:00（北京时间）
"""


def _verified_problem_admission():
    signals = DeliberationSignals(user_correction=True, repeated_failure_count=2)
    evidence = DeliberationEvidence(
        by_dimension={
            "MICRO_DIAGNOSIS": ("live-output-review",),
            "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT": ("session-policy-review",),
            "GOVERNING_ASSUMPTION_CHALLENGE": ("self-report-is-not-proof",),
            "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH": ("external-assurance-method",),
            "COUNTEREXAMPLE_SEARCH": ("existing-kernel-receipt-path",),
        }
    )
    assessment = RootScopeAssessment(
        hypotheses=(
            ProblemHypothesis(
                hypothesis_id="H_LOCAL_ONLY",
                layer=ProblemLayer.LOCAL_IMPLEMENTATION,
                statement="The failure is only a one-off wording omission.",
                disposition=HypothesisDisposition.REJECTED,
                supporting_evidence_refs=("single-output-slip",),
                falsification_or_rejection_refs=("repeated-user-correction",),
            ),
            ProblemHypothesis(
                hypothesis_id="H_ASSURANCE_BINDING",
                layer=ProblemLayer.COMMON_CAPABILITY,
                statement="Reported cognition state is not bound to verified admission evidence.",
                disposition=HypothesisDisposition.SELECTED,
                supporting_evidence_refs=("session-adherence-parser",),
                falsification_or_rejection_refs=("kernel-receipt-requirements",),
            ),
        ),
        selected_hypothesis_id="H_ASSURANCE_BINDING",
        architecture_reassessment_refs=("session-policy-and-kernel-review",),
    )
    receipt = require_root_scope_admission(signals, evidence, assessment)
    return receipt, EvolutionDisposition.DURABLE_EVOLUTION_UPDATED


def test_evaluator_required_fields_match_session_policy_contract():
    report = _policy()["inherited_session_progress_report"]
    assert tuple(report["fields"]) == POLICY_REQUIRED_PROGRESS_FIELDS
    assert set(POLICY_TO_CANONICAL_FIELD) == set(POLICY_REQUIRED_PROGRESS_FIELDS)
    assert tuple(POLICY_TO_CANONICAL_FIELD[field] for field in report["fields"]) == REQUIRED_PROGRESS_FIELDS


def test_missing_progress_report_is_observable_failure():
    result = evaluate_session_progress_response(
        "The answer stops without any progress report.",
        SessionProgressExpectation(context_selected=True),
    )
    assert not result.passed
    assert SessionAdherenceViolation.MISSING_PROGRESS_REPORT in result.violations
    assert set(result.missing_fields) == set(REQUIRED_PROGRESS_FIELDS)


def test_clean_turn_can_report_not_triggered_and_no_evolution():
    result = evaluate_session_progress_response(
        _good_report(problem=False),
        SessionProgressExpectation(context_selected=True, problem_signal_observed=False),
    )
    assert result.passed


def test_problem_signal_cannot_report_not_triggered_or_no_evolution_trigger():
    result = evaluate_session_progress_response(
        _good_report(problem=False),
        SessionProgressExpectation(context_selected=True, problem_signal_observed=True),
    )
    assert not result.passed
    assert SessionAdherenceViolation.PROBLEM_SIGNAL_REPORTED_NOT_TRIGGERED in result.violations
    assert SessionAdherenceViolation.PROBLEM_SIGNAL_REPORTED_NO_EVOLUTION_TRIGGER in result.violations


def test_problem_claim_cannot_self_prove_cognition_or_evolution():
    result = evaluate_session_progress_response(
        _good_report(problem=True),
        SessionProgressExpectation(
            context_selected=True,
            problem_signal_observed=True,
            cognition_admission_required=True,
        ),
    )
    assert not result.passed
    assert SessionAdherenceViolation.CLAIMED_COGNITION_WITHOUT_ROOT_SCOPE_RECEIPT in result.violations
    assert SessionAdherenceViolation.CLAIMED_EVOLUTION_WITHOUT_VERIFIED_DISPOSITION in result.violations


def test_problem_claim_with_verified_admission_and_record_passes():
    receipt, disposition = _verified_problem_admission()
    result = evaluate_session_progress_response(
        _good_report(problem=True),
        SessionProgressExpectation(
            context_selected=True,
            problem_signal_observed=True,
            cognition_admission_required=True,
            root_scope_receipt=receipt,
            evolution_disposition=disposition,
            problem_record_ref="state/evolution/verified-problem.json",
        ),
    )
    assert result.passed


def test_required_durable_problem_record_cannot_be_omitted():
    receipt, disposition = _verified_problem_admission()
    assert receipt.durable_problem_record_required is True
    result = evaluate_session_progress_response(
        _good_report(problem=True),
        SessionProgressExpectation(
            context_selected=True,
            problem_signal_observed=True,
            cognition_admission_required=True,
            root_scope_receipt=receipt,
            evolution_disposition=disposition,
        ),
    )
    assert not result.passed
    assert SessionAdherenceViolation.MISSING_DURABLE_PROBLEM_RECORD_EVIDENCE in result.violations


def test_no_op_next_turn_handoff_is_observable_failure_when_user_input_is_not_required():
    result = evaluate_session_progress_response(
        _good_report(problem=False, next_action="本条完成后，下一轮继续记录一个 completed sample"),
        SessionProgressExpectation(
            context_selected=True,
            no_op_continuation_disallowed=True,
            user_input_required=False,
        ),
    )
    assert not result.passed
    assert SessionAdherenceViolation.UNNECESSARY_USER_CONTINUATION_HANDOFF in result.violations


def test_real_user_input_requirement_allows_future_turn_handoff():
    result = evaluate_session_progress_response(
        _good_report(problem=False, next_action="下一轮等待用户提供缺失的授权范围"),
        SessionProgressExpectation(
            context_selected=True,
            no_op_continuation_disallowed=True,
            user_input_required=True,
        ),
    )
    assert result.passed


def test_unselected_context_does_not_invent_a_progress_requirement():
    result = evaluate_session_progress_response(
        "Simple standalone answer.",
        SessionProgressExpectation(context_selected=False),
    )
    assert result.passed
    assert result.report_required is False


def test_multi_turn_summary_measures_evidence_gaps_and_handoffs():
    receipt, disposition = _verified_problem_admission()
    samples = [
        (_good_report(problem=False), SessionProgressExpectation(context_selected=True)),
        ("No report here.", SessionProgressExpectation(context_selected=True, problem_signal_observed=True)),
        (
            _good_report(problem=False),
            SessionProgressExpectation(context_selected=True, problem_signal_observed=True),
        ),
        (
            _good_report(problem=True),
            SessionProgressExpectation(
                context_selected=True,
                problem_signal_observed=True,
                cognition_admission_required=True,
            ),
        ),
        (
            _good_report(problem=True),
            SessionProgressExpectation(
                context_selected=True,
                problem_signal_observed=True,
                cognition_admission_required=True,
                root_scope_receipt=receipt,
                evolution_disposition=disposition,
                problem_record_ref="state/evolution/verified-problem.json",
            ),
        ),
        (
            _good_report(problem=False, next_action="下一轮继续采样"),
            SessionProgressExpectation(
                context_selected=True,
                no_op_continuation_disallowed=True,
                user_input_required=False,
            ),
        ),
    ]
    summary = summarize_session_adherence(samples)
    assert summary.sample_count == 6
    assert summary.required_report_count == 6
    assert summary.pass_count == 2
    assert summary.fail_count == 4
    assert summary.missing_report_count == 1
    assert summary.problem_state_contradiction_count == 1
    assert summary.unnecessary_continuation_handoff_count == 1
    assert summary.cognition_evidence_gap_count == 1
    assert summary.durable_problem_record_gap_count == 0
    assert summary.adherence_rate == 2 / 6


def test_existing_session_policy_already_requires_cognition_before_problem_closure():
    transaction = _policy()["problem_cognition_action_transaction"]
    closure = _policy()["problem_to_action_closure_gate"]
    assert transaction["required"] is True
    assert "root-scope" in closure["rule"]
    assert "evolution disposition" in closure["rule"]
    assert "current work cycle" in closure["rule"]
