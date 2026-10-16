import pytest

from uaos.kernel.deliberation import ProblemLayer, RootScopeReceipt
from uaos.kernel.problem_closure import EvolutionDisposition, ProblemClosureDecision, ProblemClosureSignals
from uaos.runtime import FinalizationBlocked, FinalizationContext, admit_final_response


def _report(*, problem: bool = False, next_action: str = "none") -> str:
    evolution = "DURABLE_EVOLUTION_UPDATED__EVO-X" if problem else "NO_EVOLUTION_TRIGGER"
    deliberation = "TRIGGERED__ROOT_SCOPE_ADMITTED" if problem else "NOT_TRIGGERED"
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


def _receipt(*, durable: bool = True) -> RootScopeReceipt:
    return RootScopeReceipt(
        selected_hypothesis_id="H-selected",
        selected_layer=ProblemLayer.COMMON_CAPABILITY,
        hypothesis_count=2,
        compared_layers=(ProblemLayer.COMMON_CAPABILITY, ProblemLayer.HOST),
        architecture_reassessment_performed=True,
        durable_problem_record_required=durable,
        evidence_refs=("evidence:1",),
    )


def test_clean_selected_turn_can_finalize_when_no_work_remains():
    receipt = admit_final_response(
        _report(),
        FinalizationContext(context_selected=True),
    )
    assert receipt.closure_decision is ProblemClosureDecision.CLEAN_NO_PROBLEM
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


def test_problem_turn_requires_verified_terminal_closure_and_cognition_evidence():
    closure = ProblemClosureSignals(
        problem_detected=True,
        repair_attempted=True,
        repair_verified=True,
        root_scope_receipt=_receipt(durable=True),
        evolution_disposition=EvolutionDisposition.DURABLE_EVOLUTION_UPDATED,
        problem_record_ref="state/evolution/EVO-X.json",
    )
    receipt = admit_final_response(
        _report(problem=True),
        FinalizationContext(
            context_selected=True,
            problem_signal_observed=True,
            closure_signals=closure,
        ),
    )
    assert receipt.closure_decision is ProblemClosureDecision.REPAIR_EXECUTED
    assert receipt.adherence.passed


def test_problem_turn_cannot_finalize_on_self_report_without_root_scope_receipt():
    closure = ProblemClosureSignals(
        problem_detected=True,
        repair_attempted=True,
        repair_verified=True,
        evolution_disposition=EvolutionDisposition.DURABLE_EVOLUTION_UPDATED,
        problem_record_ref="state/evolution/EVO-X.json",
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
    assert any("root-scope cognitive admission is missing" in reason for reason in exc.value.reasons)


def test_repairable_problem_cannot_finalize_before_repair_attempt():
    closure = ProblemClosureSignals(
        problem_detected=True,
        repair_path_available=True,
        repair_authorized=True,
        root_scope_receipt=_receipt(durable=False),
        evolution_disposition=EvolutionDisposition.NO_DURABLE_EVOLUTION_WITH_EVIDENCE,
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
    assert any("recommendation-only finalization is forbidden" in reason for reason in exc.value.reasons)


def test_real_user_choice_can_be_a_terminal_blocker_without_fake_cognition_receipt():
    closure = ProblemClosureSignals(
        problem_detected=True,
        user_choice_required=True,
    )
    response = _report(
        problem=True,
        next_action="下一轮等待用户提供真正缺失的授权范围",
    ).replace(
        "Evolution：DURABLE_EVOLUTION_UPDATED__EVO-X",
        "Evolution：PENDING__BLOCKED_BY_USER_FACT",
    ).replace(
        "Deliberation：TRIGGERED__ROOT_SCOPE_ADMITTED",
        "Deliberation：TRIGGERED__BLOCKED_BEFORE_ROOT_SCOPE",
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
    assert receipt.closure_decision is ProblemClosureDecision.BLOCKED_WITH_REASON
    assert receipt.adherence.passed
