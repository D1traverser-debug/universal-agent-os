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


class FakeOutputGuardrail:
    def __init__(self, guardrail_function, name):
        self.guardrail_function = guardrail_function
        self.name = name

    def get_name(self):
        return self.name


def _install_fake_agents_module(monkeypatch):
    module = ModuleType("agents")
    module.GuardrailFunctionOutput = FakeGuardrailFunctionOutput

    def output_guardrail(*, name=None):
        def decorate(fn):
            return FakeOutputGuardrail(fn, name or fn.__name__)
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
    outcome = guardrail.guardrail_function(None, None, _clean_progress_report())
    assert guardrail.get_name() == "uaos_finalization_gate"
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
    outcome = guardrail.guardrail_function(None, None, _clean_progress_report())
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


class UserVisibleRunner:
    @staticmethod
    def run_sync(agent, payload):
        return SimpleNamespace(final_output=_clean_progress_report(), last_agent=SimpleNamespace(name="Researcher"))


def test_user_visible_host_requires_real_finalization_context():
    import pytest
    with pytest.raises(ValueError, match="USER_VISIBLE_REQUIRES_FINALIZATION_CONTEXT_PROVIDER"):
        OpenAIAgentsExecutor(
            agent_spec=OpenAIAgentSpec("Researcher", "x"),
            agent_factory=Agent, runner=Runner, user_visible=True,
        )
    with pytest.raises(ValueError, match="FINALIZATION_CONTEXT_ONLY_ALLOWED_FOR_USER_VISIBLE"):
        OpenAIAgentsExecutor(
            agent_spec=OpenAIAgentSpec("Researcher", "x"),
            agent_factory=Agent, runner=Runner,
            finalization_context_provider=lambda _request, _run: FinalizationContext(context_selected=True),
        )


def test_user_visible_sdk_success_requires_actual_finalization_admission():
    seen = []
    def provide(request, result):
        seen.append((request.action_id, "当前 Agent" in result.final_output))
        return FinalizationContext(context_selected=True)
    executor = OpenAIAgentsExecutor(
        agent_spec=OpenAIAgentSpec("Researcher", "x"), agent_factory=Agent,
        runner=UserVisibleRunner, user_visible=True,
        finalization_context_provider=provide,
    )
    response = executor.execute(ExecutionRequest("real-user-run", "read", "repo", "x"))
    assert seen == [("real-user-run", True)]
    assert response.disposition is ExecutionDisposition.CONFIRMED
    assert response.evidence["uaos_finalization"] == "ADMITTED"
    assert response.evidence["delivery_scope"] == "USER_VISIBLE"


def test_user_visible_sdk_missing_progress_fails_before_delivery_even_if_sdk_runner_returns():
    executor = OpenAIAgentsExecutor(
        agent_spec=OpenAIAgentSpec("Researcher", "x"), agent_factory=Agent,
        runner=Runner, user_visible=True,
        finalization_context_provider=lambda _request, _run: FinalizationContext(context_selected=True),
    )
    response = executor.execute(ExecutionRequest("miss-progress", "read", "repo", "input"))
    assert response.disposition is ExecutionDisposition.FAILED
    assert "USER_VISIBLE_FINALIZATION_REJECTED" in response.error
    assert "MISSING_PROGRESS_REPORT" in response.error
    assert response.output is None


def test_user_visible_sdk_unfinished_work_blocks_clean_progress_output():
    executor = OpenAIAgentsExecutor(
        agent_spec=OpenAIAgentSpec("Researcher", "x"), agent_factory=Agent,
        runner=UserVisibleRunner, user_visible=True,
        finalization_context_provider=lambda _request, _run: FinalizationContext(
            context_selected=True, work_remaining_without_user_input=True,
        ),
    )
    response = executor.execute(ExecutionRequest("unfinished", "read", "repo", "x"))
    assert response.disposition is ExecutionDisposition.FAILED
    assert "ACTIONABLE_WORK_REMAINS_WITHOUT_USER_INPUT" in response.error
    assert response.output is None


def test_sdk_keeps_independent_work_open_despite_unrelated_user_choice():
    executor = OpenAIAgentsExecutor(
        agent_spec=OpenAIAgentSpec("Researcher", "x"), agent_factory=Agent,
        runner=UserVisibleRunner, user_visible=True,
        finalization_context_provider=lambda _request, _run: FinalizationContext(
            context_selected=True,
            user_input_required=True,
            work_remaining_without_user_input=True,
        ),
    )
    response = executor.execute(ExecutionRequest("parallel-work", "read", "repo", "x"))
    assert response.disposition is ExecutionDisposition.FAILED
    assert "ACTIONABLE_WORK_REMAINS_WITHOUT_USER_INPUT" in response.error
    assert response.output is None


def test_user_visible_sdk_rejects_failed_or_untrusted_context_provider():
    for provider in (
        lambda _request, _run: None,
        lambda _request, _run: (_ for _ in ()).throw(RuntimeError("context unavailable")),
    ):
        executor = OpenAIAgentsExecutor(
            agent_spec=OpenAIAgentSpec("Researcher", "x"), agent_factory=Agent,
            runner=UserVisibleRunner, user_visible=True, finalization_context_provider=provider,
        )
        response = executor.execute(ExecutionRequest("bad-context", "read", "repo", "x"))
        assert response.disposition is ExecutionDisposition.FAILED
        assert "USER_VISIBLE_FINALIZATION_REJECTED" in response.error
        assert response.output is None


def test_internal_sdk_result_remains_allowed_as_internal_only():
    executor = OpenAIAgentsExecutor(
        agent_spec=OpenAIAgentSpec("Researcher", "x"), agent_factory=Agent, runner=Runner,
    )
    response = executor.execute(ExecutionRequest("internal", "read", "repo", "x"))
    assert response.disposition is ExecutionDisposition.CONFIRMED
    assert response.evidence["delivery_scope"] == "INTERNAL_ONLY"
