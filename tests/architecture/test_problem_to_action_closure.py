import pytest

from uaos.kernel import (
    ProblemClosureDecision,
    ProblemClosureError,
    ProblemClosureSignals,
    assess_problem_closure,
    require_problem_finalization_admission,
)


def test_clean_turn_stays_lightweight():
    decision = assess_problem_closure(ProblemClosureSignals(problem_detected=False))
    assert decision is ProblemClosureDecision.CLEAN_NO_PROBLEM


def test_authorized_feasible_repair_cannot_end_as_recommendation_only():
    signals = ProblemClosureSignals(
        problem_detected=True,
        repair_path_available=True,
        repair_authorized=True,
    )
    assert assess_problem_closure(signals) is ProblemClosureDecision.REPAIR_NOW
    with pytest.raises(ProblemClosureError, match="recommendation-only finalization is forbidden"):
        require_problem_finalization_admission(signals)


def test_verified_repair_is_an_admissible_terminal_state():
    signals = ProblemClosureSignals(
        problem_detected=True,
        repair_path_available=True,
        repair_authorized=True,
        repair_attempted=True,
        repair_verified=True,
    )
    assert require_problem_finalization_admission(signals) is ProblemClosureDecision.REPAIR_EXECUTED


def test_real_blocker_or_required_user_choice_allows_escalation():
    blocked = ProblemClosureSignals(
        problem_detected=True,
        repair_path_available=True,
        repair_authorized=False,
        hard_blocker="domain owner permission unavailable",
    )
    assert require_problem_finalization_admission(blocked) is ProblemClosureDecision.BLOCKED_WITH_REASON

    choice = ProblemClosureSignals(problem_detected=True, user_choice_required=True)
    assert require_problem_finalization_admission(choice) is ProblemClosureDecision.BLOCKED_WITH_REASON


def test_no_change_requires_explicit_evidence_backed_reason():
    no_change = ProblemClosureSignals(
        problem_detected=True,
        no_change_reason="counterexample search shows the apparent defect is expected behavior under the governing contract",
    )
    assert require_problem_finalization_admission(no_change) is ProblemClosureDecision.NO_CHANGE_WITH_EVIDENCE


def test_ambiguous_problem_cannot_be_silently_finalized():
    with pytest.raises(ProblemClosureError, match="no admissible terminal disposition"):
        require_problem_finalization_admission(ProblemClosureSignals(problem_detected=True))
