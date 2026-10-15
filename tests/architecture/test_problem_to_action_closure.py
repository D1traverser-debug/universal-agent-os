import json
from pathlib import Path

import pytest

from uaos.kernel import (
    ProblemClosureDecision,
    ProblemClosureError,
    ProblemClosureSignals,
    assess_problem_closure,
    require_problem_finalization_admission,
)

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


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


def test_session_policy_makes_problem_to_action_gate_mandatory():
    policy = _json("config/SESSION_INTERACTION_POLICY.json")
    gate = policy["problem_to_action_closure_gate"]
    assert gate["required"] is True
    assert gate["executable_ref"] == "src/uaos/kernel/problem_closure.py"
    assert "REPAIR_EXECUTED" in gate["terminal_states"]
    assert "recommendation-only" in gate["rule"].lower()
    assert "recommendation-only" in policy["inherited_session_progress_report"]["action_closure_rule"].lower()


def test_common_behavior_contract_requires_repair_or_block_not_declaration_only():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    closure = policy["problem_to_action_closure"]
    assert policy["contract_version"] == "1.2.0"
    assert closure["executable_ref"] == "src/uaos/kernel/problem_closure.py"
    assert "REPAIR_EXECUTED" in closure["terminal_states"]
    assert "RECOMMENDATION_ONLY" in policy["parent_decisions"]["PROBLEM_TO_ACTION_CLOSURE_GAP"]


def test_binding_and_current_system_expose_action_closure_contract():
    binding = _json("config/BINDING_POLICY.json")
    current = _json("CURRENT_SYSTEM.json")
    assert "MUST_ATTEMPT_THE_REPAIR_BEFORE_FINALIZING" in binding["problem_action_closure_rule"]
    assert "COMMON_BEHAVIOR_ASSURANCE_1_2" in current["common_behavior_assurance_contract"]
    assert "RECOMMENDATION_ONLY_FORBIDDEN" in current["problem_action_closure_assurance"]
