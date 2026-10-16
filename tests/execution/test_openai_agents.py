import sys
from types import ModuleType, SimpleNamespace

from uaos.execution import (
    ExecutionDisposition,
    ExecutionRequest,
    OpenAIAgentSpec,
    OpenAIAgentsExecutor,
    build_uaos_output_guardrail,
)
from uaos.runtime import FinalizationContext


class Agent:
    last_kwargs = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        Agent.last_kwargs = kwargs


class Runner:
    @staticmethod
    def run_sync(agent, payload):
        assert agent.kwargs["name"] == "Researcher"
        return SimpleNamespace(final_output=f"done:{payload}", last_agent=SimpleNamespace(name="Researcher"))


class FailingRunner:
    @staticmethod
    def run_sync(agent, payload):
        raise TimeoutError("lost")


class FakeGuardrailFunctionOutput:
    def __init__(self, *, output_info, tripwire_triggered):
        self.output_info = output_info
        self.tripwire_triggered = tripwire_triggered


def _install_fake_agents_module(monkeypatch):
    module = ModuleType("agents")
    module.GuardrailFunctionOutput = FakeGuardrailFunctionOutput

    def output_guardrail(*, name):
        def decorate(fn):
            fn.guardrail_name = name
            return fn
        return decorate

    module.output_guardrail = output_guardrail
    monkeypatch.setitem(sys.modules, "agents", module)


def _clean_progress_report():
    return """Completed.

当前 Agent：UAOS
当前范围或任务：OpenAI guardrail test
Authority：UAOS
状态：DONE
当前阶段：FINALIZATION
下一动作或阻塞：none
Evolution：NO_EVOLUTION_TRIGGER
Deliberation：NOT_TRIGGERED
版本：UAOS test
进度时间：2026-10-16 14:07:00（北京时间）
"""


def test_openai_adapter_returns_bounded_run_output():
    executor = OpenAIAgentsExecutor(agent_spec=OpenAIAgentSpec("Researcher", "research carefully", "gpt-x"), agent_factory=Agent, runner=Runner)
    result = executor.execute(ExecutionRequest("a", "research", "topic", "input"))
    assert result.disposition is ExecutionDisposition.CONFIRMED
    assert result.output == "done:input"


def test_openai_adapter_forwards_output_guardrails_to_agent():
    guardrail = object()
    executor = OpenAIAgentsExecutor(
        agent_spec=OpenAIAgentSpec(
            "Researcher",
            "research carefully",
            "gpt-x",
            output_guardrails=(guardrail,),
        ),
        agent_factory=Agent,
        runner=Runner,
    )
    result = executor.execute(ExecutionRequest("a", "research", "topic", "input"))
    assert result.disposition is ExecutionDisposition.CONFIRMED
    assert Agent.last_kwargs["output_guardrails"] == [guardrail]


def test_uaos_output_guardrail_builder_admits_clean_final_output(monkeypatch):
    _install_fake_agents_module(monkeypatch)
    guardrail = build_uaos_output_guardrail(
        lambda _run_context, _agent, _output: FinalizationContext(context_selected=True)
    )
    outcome = guardrail(None, None, _clean_progress_report())
    assert guardrail.guardrail_name == "uaos_finalization_gate"
    assert outcome.tripwire_triggered is False
    assert outcome.output_info["uaos_finalization"] == "ADMITTED"


def test_uaos_output_guardrail_builder_trips_when_actionable_work_remains(monkeypatch):
    _install_fake_agents_module(monkeypatch)
    guardrail = build_uaos_output_guardrail(
        lambda _run_context, _agent, _output: FinalizationContext(
            context_selected=True,
            work_remaining_without_user_input=True,
        )
    )
    outcome = guardrail(None, None, _clean_progress_report())
    assert outcome.tripwire_triggered is True
    assert "ACTIONABLE_WORK_REMAINS_WITHOUT_USER_INPUT" in outcome.output_info["uaos_finalization_blocked"]


def test_model_failure_is_known_failure_for_read_work():
    executor = OpenAIAgentsExecutor(agent_spec=OpenAIAgentSpec("Researcher", "x"), agent_factory=Agent, runner=FailingRunner)
    result = executor.execute(ExecutionRequest("a", "research", "topic", "input", side_effect_class="READ"))
    assert result.disposition is ExecutionDisposition.FAILED


def test_reasoning_executor_refuses_authoritative_side_effects():
    executor = OpenAIAgentsExecutor(agent_spec=OpenAIAgentSpec("Worker", "x"), agent_factory=Agent, runner=FailingRunner)
    result = executor.execute(ExecutionRequest("a", "publish", "target", "input", side_effect_class="WRITE"))
    assert result.disposition is ExecutionDisposition.FAILED
    assert "cannot perform authoritative side effects" in result.error
