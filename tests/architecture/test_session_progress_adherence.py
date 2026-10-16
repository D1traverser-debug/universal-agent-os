import json
from pathlib import Path

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


def _good_report(*, problem: bool) -> str:
    evolution = (
        "EVALUATED_NO_DURABLE_EVOLUTION"
        if problem
        else "NO_EVOLUTION_TRIGGER"
    )
    deliberation = "TRIGGERED__USER_CORRECTION_VERIFIED" if problem else "NOT_TRIGGERED"
    return f"""Work completed.

当前 Agent：UAOS
当前范围：session adherence replay
Authority：UAOS
状态：OBSERVING
当前阶段：LIVE_DOGFOOD
下一动作：continue scenario replay
Evolution：{evolution}
Deliberation：{deliberation}
版本：UAOS 2.5.2 / Session 1.9.0
进度时间：2026-10-16 10:45:00（北京时间）
"""


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


def test_problem_signal_with_triggered_deliberation_and_evaluated_evolution_passes():
    result = evaluate_session_progress_response(
        _good_report(problem=True),
        SessionProgressExpectation(context_selected=True, problem_signal_observed=True),
    )
    assert result.passed


def test_unselected_context_does_not_invent_a_progress_requirement():
    result = evaluate_session_progress_response(
        "Simple standalone answer.",
        SessionProgressExpectation(context_selected=False),
    )
    assert result.passed
    assert result.report_required is False


def test_multi_turn_summary_measures_missing_reports_and_state_contradictions():
    samples = [
        (_good_report(problem=False), SessionProgressExpectation(context_selected=True)),
        (
            "No report here.",
            SessionProgressExpectation(context_selected=True, problem_signal_observed=True),
        ),
        (
            _good_report(problem=False),
            SessionProgressExpectation(context_selected=True, problem_signal_observed=True),
        ),
        (
            _good_report(problem=True),
            SessionProgressExpectation(context_selected=True, problem_signal_observed=True),
        ),
    ]
    summary = summarize_session_adherence(samples)
    assert summary.sample_count == 4
    assert summary.required_report_count == 4
    assert summary.pass_count == 2
    assert summary.fail_count == 2
    assert summary.missing_report_count == 1
    assert summary.problem_state_contradiction_count == 1
    assert summary.adherence_rate == 0.5
