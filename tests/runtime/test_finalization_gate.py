import pytest

from uaos.kernel import (
    ActionCandidate,
    CausalFactor,
    CausalFactorDisposition,
    CognitionCase,
    DeliberationEvidence,
    DeliberationSignals,
    EngineeringTrace,
    EvidenceItem,
    EvidenceKind,
    EvolutionDisposition,
    ProblemClosureSignals,
    ProblemLayer,
    RootScopeReceipt,
)
from uaos.runtime import FinalizationBlocked, FinalizationContext, admit_final_response


def _report(*, problem: bool = False, next_action: str = "none") -> str:
    evolution = "DURABLE_EVOLUTION_UPDATED__EVO-X" if problem else "NO_EVOLUTION_TRIGGER"
    deliberation = "TRIGGERED__CAUSAL_INTERVENTION_ADMITTED" if problem else "NOT_TRIGGERED"
    return f"""Completed.

当前 Agent：UAOS
当前范围或任务：finalization gate test
Authority：UAOS
状态：DONE
当前阶段：FINALIZATION
下一动作或阻塞：{next_action}
Evolution：{evolution}
Deliberation：{deliberation}
版本：UAOS test
进度时间：2026-10-16 14:07:00（北京时间）
"""


def _legacy_receipt(*, durable: bool = True) -> RootScopeReceipt:
    return RootScopeReceipt(
        selected_hypothesis_id="H-selected",
        selected_layer=ProblemLayer.COMMON_CAPABILITY,
        hypothesis_count=2,
        compared_layers=(ProblemLayer.COMMON_CAPABILITY, ProblemLayer.HOST),
        architecture_reassessment_performed=True,
        durable_problem_record_required=durable,
        evidence_refs=("evidence:1",),
    )


def _cognition_case() -> CognitionCase:
    items = (
        EvidenceItem("goal", EvidenceKind.USER_CLAIM, "Fix the detected problem without mirroring user framing.", "conversation://goal"),
        EvidenceItem("micro", EvidenceKind.REPOSITORY_FACT, "Local implementation fact.", "repo://micro"),
        EvidenceItem("macro", EvidenceKind.ANALYSIS_RESULT, "Macro alignment checked.", "analysis://macro"),
        EvidenceItem("assumption", EvidenceKind.ANALYSIS_RESULT, "Governing assumption challenged.", "analysis://assumption"),
        EvidenceItem("counter", EvidenceKind.TEST_RESULT, "Competing explanation was probed.", "test://counter"),
        EvidenceItem("action-local", EvidenceKind.REPOSITORY_FACT, "Local repair candidate evidence.", "repo://action-local"),
        EvidenceItem("action-no", EvidenceKind.ANALYSIS_RESULT, "No-change candidate evidence.", "analysis://action-no"),
        EvidenceItem("trade-local", EvidenceKind.ANALYSIS_RESULT, "Local repair tradeoff.", "analysis://trade-local"),
        EvidenceItem("trade-no", EvidenceKind.ANALYSIS_RESULT, "No-change tradeoff.", "analysis://trade-no"),
        EvidenceItem("verify", EvidenceKind.TEST_RESULT, "Repair passed its deterministic verification.", "test://verify", method_ref="deterministic regression test"),
        EvidenceItem("wrong-verify", EvidenceKind.TEST_RESULT, "An unrelated test passed.", "test://unrelated", method_ref="unrelated check"),
    )
    evidence = DeliberationEvidence({
        "MICRO_DIAGNOSIS": ("micro",),
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT": ("macro",),
        "GOVERNING_ASSUMPTION_CHALLENGE": ("assumption",),
        "COUNTEREXAMPLE_SEARCH": ("counter",),
    })
    return CognitionCase(
        case_id="runtime-finalization-case",
        signals=DeliberationSignals(user_correction=True),
        evidence=evidence,
        evidence_items=items,
        causal_factors=(
            CausalFactor(
                "local-factor",
                ProblemLayer.LOCAL_IMPLEMENTATION,
                "A local implementation defect contributes to the observed failure.",
                CausalFactorDisposition.SUPPORTED,
                ("micro",),
                ("counter",),
            ),
            CausalFactor(
                "control-factor",
                ProblemLayer.CONTROL_PLANE,
                "The control plane is the primary cause.",
                CausalFactorDisposition.REJECTED,
                ("macro",),
                ("assumption",),
            ),
        ),
        action_candidates=(
            ActionCandidate("local-repair", ProblemLayer.LOCAL_IMPLEMENTATION, "Repair the local defect.", ("action-local",), ("trade-local",)),
            ActionCandidate("no-change", ProblemLayer.CONTROL_PLANE, "Do not change the system.", ("action-no",), ("trade-no",), True),
        ),
        selected_action_candidate_id="local-repair",
        engineering_trace=EngineeringTrace(
            governing_outcome="Correct the reproduced behavior without adopting the user's causal theory as authority.",
            requirement_or_goal_evidence_ids=("goal",),
            mechanism_candidate_id="local-repair",
            verification_methods=("deterministic regression test",),
        ),
    )


def _successful_closure(**overrides) -> ProblemClosureSignals:
    values = dict(
        problem_detected=True,
        repair_attempted=True,
        repair_verified=True,
        evolution_disposition=EvolutionDisposition.DURABLE_EVOLUTION_UPDATED,
        terminal_action_candidate_id="local-repair",
        verification_evidence_refs=("verify",),
    )
    values.update(overrides)
    return ProblemClosureSignals(**values)


def test_clean_selected_turn_can_finalize_when_no_work_remains():
    receipt = admit_final_response(
        _report(),
        FinalizationContext(context_selected=True),
    )
    assert receipt.closure_decision.value == "CLEAN_NO_PROBLEM"
    assert receipt.adherence.passed


def test_runtime_blocks_finalization_while_actionable_work_remains():
    with pytest.raises(FinalizationBlocked) as exc:
        admit_final_response(
            _report(),
            FinalizationContext(
                context_selected=True,
                work_remaining_without_user_input=True,
            ),
        )
    assert "ACTIONABLE_WORK_REMAINS_WITHOUT_USER_INPUT" in exc.value.reasons


def test_problem_turn_recomputes_cognition_case_and_requires_verified_terminal_closure():
    receipt = admit_final_response(
        _report(problem=True),
        FinalizationContext(
            context_selected=True,
            problem_signal_observed=True,
            cognition_case=_cognition_case(),
            closure_signals=_successful_closure(),
        ),
    )
    assert receipt.closure_decision.value == "REPAIR_EXECUTED"
    assert receipt.adherence.passed


def test_precomputed_root_scope_receipt_cannot_substitute_for_full_cognition_case():
    closure = ProblemClosureSignals(
        problem_detected=True,
        repair_attempted=True,
        repair_verified=True,
        root_scope_receipt=_legacy_receipt(durable=False),
        evolution_disposition=EvolutionDisposition.NO_DURABLE_EVOLUTION_WITH_EVIDENCE,
        terminal_action_candidate_id="local-repair",
        verification_evidence_refs=("verify",),
    )
    with pytest.raises(FinalizationBlocked) as exc:
        admit_final_response(
            _report(problem=True),
            FinalizationContext(
                context_selected=True,
                problem_signal_observed=True,
                closure_signals=closure,
            ),
        )
    assert "MISSING_EVIDENCE_TRACED_COGNITION_CASE" in exc.value.reasons


def test_boolean_repair_verified_claim_without_verification_evidence_is_blocked():
    closure = _successful_closure(verification_evidence_refs=())
    with pytest.raises(FinalizationBlocked) as exc:
        admit_final_response(
            _report(problem=True),
            FinalizationContext(
                context_selected=True,
                problem_signal_observed=True,
                cognition_case=_cognition_case(),
                closure_signals=closure,
            ),
        )
    assert any("VERIFICATION_METHOD_EVIDENCE" in reason or "verification evidence" in reason for reason in exc.value.reasons)


def test_unrelated_green_test_cannot_satisfy_planned_verification_method():
    closure = _successful_closure(verification_evidence_refs=("wrong-verify",))
    with pytest.raises(FinalizationBlocked) as exc:
        admit_final_response(
            _report(problem=True),
            FinalizationContext(
                context_selected=True,
                problem_signal_observed=True,
                cognition_case=_cognition_case(),
                closure_signals=closure,
            ),
        )
    assert any("UNPLANNED_VERIFICATION_EVIDENCE_METHOD" in reason for reason in exc.value.reasons)


def test_terminal_repair_must_match_the_admitted_intervention_candidate():
    closure = _successful_closure(terminal_action_candidate_id="no-change")
    with pytest.raises(FinalizationBlocked) as exc:
        admit_final_response(
            _report(problem=True),
            FinalizationContext(
                context_selected=True,
                problem_signal_observed=True,
                cognition_case=_cognition_case(),
                closure_signals=closure,
            ),
        )
    assert any("terminal action does not match" in reason for reason in exc.value.reasons)


def test_no_change_cannot_close_a_case_whose_admitted_intervention_is_repair():
    closure = ProblemClosureSignals(
        problem_detected=True,
        no_change_reason="leave it unchanged",
        evolution_disposition=EvolutionDisposition.NO_DURABLE_EVOLUTION_WITH_EVIDENCE,
        terminal_action_candidate_id="local-repair",
    )
    with pytest.raises(FinalizationBlocked) as exc:
        admit_final_response(
            _report(problem=True),
            FinalizationContext(
                context_selected=True,
                problem_signal_observed=True,
                cognition_case=_cognition_case(),
                closure_signals=closure,
            ),
        )
    assert any("NO_CHANGE closure is invalid" in reason for reason in exc.value.reasons)


def test_repairable_problem_cannot_finalize_before_repair_attempt():
    closure = ProblemClosureSignals(
        problem_detected=True,
        repair_path_available=True,
        repair_authorized=True,
        evolution_disposition=EvolutionDisposition.NO_DURABLE_EVOLUTION_WITH_EVIDENCE,
    )
    with pytest.raises(FinalizationBlocked) as exc:
        admit_final_response(
            _report(problem=True),
            FinalizationContext(
                context_selected=True,
                problem_signal_observed=True,
                cognition_case=_cognition_case(),
                closure_signals=closure,
            ),
        )
    assert any("recommendation-only finalization is forbidden" in reason for reason in exc.value.reasons)


def test_real_user_choice_can_be_a_terminal_blocker_without_fake_cognition_case():
    closure = ProblemClosureSignals(
        problem_detected=True,
        user_choice_required=True,
    )
    response = _report(
        problem=True,
        next_action="等待用户提供真正缺失的授权范围",
    ).replace(
        "Evolution：DURABLE_EVOLUTION_UPDATED__EVO-X",
        "Evolution：PENDING__BLOCKED_BY_USER_FACT",
    ).replace(
        "Deliberation：TRIGGERED__CAUSAL_INTERVENTION_ADMITTED",
        "Deliberation：TRIGGERED__BLOCKED_BEFORE_CAUSAL_ADMISSION",
    )
    receipt = admit_final_response(
        response,
        FinalizationContext(
            context_selected=True,
            problem_signal_observed=True,
            user_input_required=True,
            closure_signals=closure,
        ),
    )
    assert receipt.closure_decision.value == "BLOCKED_WITH_REASON"
    assert receipt.adherence.passed
