import pytest

agents = pytest.importorskip("agents")

from uaos.execution import build_uaos_output_guardrail
from uaos.runtime import FinalizationContext


def _clean_progress_report():
    return """Completed.

当前 Agent：UAOS
当前范围或任务：installed OpenAI guardrail compatibility
Authority：UAOS
状态：DONE
当前阶段：FINALIZATION
下一动作或阻塞：none
Evolution：NO_EVOLUTION_TRIGGER
Deliberation：NOT_TRIGGERED
版本：UAOS live compatibility
进度时间：2026-10-16 14:07:00（北京时间）
"""


def test_installed_agents_sdk_accepts_uaos_output_guardrail_and_admits_clean_output():
    guardrail = build_uaos_output_guardrail(
        lambda _run_context, _agent, _output: FinalizationContext(context_selected=True)
    )
    assert guardrail.get_name() == "uaos_finalization_gate"
    outcome = guardrail.guardrail_function(None, None, _clean_progress_report())
    assert isinstance(outcome, agents.GuardrailFunctionOutput)
    assert outcome.tripwire_triggered is False
    assert outcome.output_info["uaos_finalization"] == "ADMITTED"


def test_installed_agents_sdk_guardrail_trips_when_actionable_work_remains():
    guardrail = build_uaos_output_guardrail(
        lambda _run_context, _agent, _output: FinalizationContext(
            context_selected=True,
            work_remaining_without_user_input=True,
        )
    )
    outcome = guardrail.guardrail_function(None, None, _clean_progress_report())
    assert isinstance(outcome, agents.GuardrailFunctionOutput)
    assert outcome.tripwire_triggered is True
    assert "ACTIONABLE_WORK_REMAINS_WITHOUT_USER_INPUT" in outcome.output_info["uaos_finalization_blocked"]
