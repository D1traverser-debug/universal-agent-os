import json
from pathlib import Path

import pytest

from uaos.kernel import (
    EvolutionDisposition,
    ProblemClosureDecision,
    ProblemClosureError,
    ProblemClosureSignals,
    ProblemLayer,
    RootScopeReceipt,
    assess_problem_closure,
    require_problem_finalization_admission,
)

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _receipt(*, durable: bool = True) -> RootScopeReceipt:
    return RootScopeReceipt(
        selected_hypothesis_id="root",
        selected_layer=ProblemLayer.CONTROL_PLANE,
        hypothesis_count=2,
        compared_layers=(ProblemLayer.CONTROL_PLANE, ProblemLayer.LOCAL_IMPLEMENTATION),
        architecture_reassessment_performed=True,
        durable_problem_record_required=durable,
        evidence_refs=("evidence://root-scope",),
    )


def _admitted(**overrides) -> ProblemClosureSignals:
    values = dict(
        problem_detected=True,
        root_scope_receipt=_receipt(),
        evolution_disposition=EvolutionDisposition.DURABLE_EVOLUTION_UPDATED,
        problem_record_ref="state/evolution/EVO-PROBLEM.json",
    )
    values.update(overrides)
    return ProblemClosureSignals(**values)


def test_clean_turn_stays_lightweight():
    decision = assess_problem_closure(ProblemClosureSignals(problem_detected=False))
    assert decision is ProblemClosureDecision.CLEAN_NO_PROBLEM


def test_authorized_feasible_repair_is_blocked_until_root_scope_and_evolution_are_admitted():
    with pytest.raises(ProblemClosureError, match="root-scope cognitive admission"):
        assess_problem_closure(
            ProblemClosureSignals(
                problem_detected=True,
                repair_path_available=True,
                repair_authorized=True,
            )
        )

    signals = _admitted(repair_path_available=True, repair_authorized=True)
    assert assess_problem_closure(signals) is ProblemClosureDecision.REPAIR_NOW
    with pytest.raises(ProblemClosureError, match="recommendation-only finalization is forbidden"):
        require_problem_finalization_admission(signals)


def test_arbitrary_string_cannot_impersonate_evolution_disposition():
    signals = ProblemClosureSignals(
        problem_detected=True,
        repair_path_available=True,
        repair_authorized=True,
        root_scope_receipt=_receipt(durable=False),
        evolution_disposition="DURABLE_FAILURE_CLASS_UPDATED",  # type: ignore[arg-type]
    )
    with pytest.raises(ProblemClosureError, match="valid evolution/learning disposition"):
        assess_problem_closure(signals)


def test_repair_attempt_before_cognitive_admission_is_rejected_even_if_it_later_looks_successful():
    with pytest.raises(ProblemClosureError, match="root-scope cognitive admission"):
        assess_problem_closure(
            ProblemClosureSignals(
                problem_detected=True,
                repair_attempted=True,
                repair_verified=True,
            )
        )


def test_verified_repair_is_an_admissible_terminal_state_after_cognitive_and_evolution_admission():
    signals = _admitted(
        repair_path_available=True,
        repair_authorized=True,
        repair_attempted=True,
        repair_verified=True,
    )
    assert require_problem_finalization_admission(signals) is ProblemClosureDecision.REPAIR_EXECUTED


def test_root_scope_derived_durable_requirement_cannot_be_downgraded_by_caller():
    signals = ProblemClosureSignals(
        problem_detected=True,
        repair_path_available=True,
        repair_authorized=True,
        root_scope_receipt=_receipt(durable=True),
        evolution_disposition=EvolutionDisposition.DURABLE_EVOLUTION_CANDIDATE,
        problem_record_required=False,
    )
    with pytest.raises(ProblemClosureError, match="durable problem evidence"):
        assess_problem_closure(signals)


def test_caller_may_request_stronger_durable_record_for_otherwise_local_problem():
    signals = ProblemClosureSignals(
        problem_detected=True,
        repair_path_available=True,
        repair_authorized=True,
        root_scope_receipt=_receipt(durable=False),
        evolution_disposition=EvolutionDisposition.LOCAL_LEARNING_ONLY,
        problem_record_required=True,
    )
    with pytest.raises(ProblemClosureError, match="durable problem evidence"):
        assess_problem_closure(signals)


def test_real_blocker_or_required_user_choice_allows_escalation_without_fake_root_cause_claim():
    blocked = ProblemClosureSignals(
        problem_detected=True,
        repair_path_available=True,
        repair_authorized=False,
        hard_blocker="domain owner permission unavailable",
    )
    assert require_problem_finalization_admission(blocked) is ProblemClosureDecision.BLOCKED_WITH_REASON

    choice = ProblemClosureSignals(problem_detected=True, user_choice_required=True)
    assert require_problem_finalization_admission(choice) is ProblemClosureDecision.BLOCKED_WITH_REASON


def test_no_change_requires_explicit_evidence_backed_reason_plus_cognitive_admission():
    no_change = _admitted(
        no_change_reason="counterexample search shows the apparent defect is expected behavior under the governing contract",
    )
    assert require_problem_finalization_admission(no_change) is ProblemClosureDecision.NO_CHANGE_WITH_EVIDENCE


def test_ambiguous_problem_cannot_be_silently_finalized():
    with pytest.raises(ProblemClosureError, match="no admissible terminal disposition"):
        require_problem_finalization_admission(ProblemClosureSignals(problem_detected=True))


def test_session_policy_makes_problem_cognition_and_action_gate_mandatory():
    policy = _json("config/SESSION_INTERACTION_POLICY.json")
    deliberation = _json("config/DELIBERATION_POLICY.json")
    gate = policy["problem_to_action_closure_gate"]
    cognition = policy["problem_cognition_action_transaction"]
    assert gate["required"] is True
    assert gate["executable_ref"] == "src/uaos/kernel/problem_closure.py"
    assert cognition["required"] is True
    assert cognition["root_scope_executable_ref"] == "src/uaos/kernel/deliberation.py"
    assert cognition["canonical_cognition_policy_ref"] == "config/DELIBERATION_POLICY.json#cognition_kernel"
    assert "ordered_stages" not in cognition
    assert "root_scope_admission" in deliberation
    assert "COMMIT_ROOT_SCOPE_AND_LEARNING_DISPOSITION" in deliberation["cognition_kernel"]["hot_path"]
    assert "REPAIR_EXECUTED" in gate["terminal_states"]
    assert "recommendation-only" in gate["rule"].lower()


def test_common_behavior_contract_requires_cognition_before_repair_or_block():
    policy = _json("config/COMMON_BEHAVIOR_ASSURANCE.json")
    closure = policy["problem_to_action_closure"]
    cognition = policy["problem_cognition_action_transaction"]
    assert policy["contract_version"] == "1.3.0"
    assert closure["executable_ref"] == "src/uaos/kernel/problem_closure.py"
    assert cognition["root_scope_executable_ref"] == "src/uaos/kernel/deliberation.py"
    assert cognition["canonical_cognition_policy_ref"] == "config/DELIBERATION_POLICY.json#cognition_kernel"
    assert "REPAIR_EXECUTED" in closure["terminal_states"]
    assert "PREMATURE_REPAIR_BEFORE_ROOT_SCOPE" in policy["parent_decisions"]


def test_binding_and_current_system_expose_cognitive_action_contract():
    binding = _json("config/BINDING_POLICY.json")
    current = _json("CURRENT_SYSTEM.json")
    assert "ROOT_SCOPE_ADMISSION" in binding["problem_cognition_action_rule"]
    assert current["owners"]["common_behavior_assurance"] == "config/COMMON_BEHAVIOR_ASSURANCE.json"
    assert "ROOT_SCOPE_ADMISSION" in current["assurance"]["problem_action_closure"]
