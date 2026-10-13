from types import SimpleNamespace
from uaos.execution import ExecutionDisposition, ExecutionRequest, OpenAIAgentSpec, OpenAIAgentsExecutor


class Agent:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class Runner:
    @staticmethod
    def run_sync(agent, payload):
        assert agent.kwargs["name"] == "Researcher"
        return SimpleNamespace(final_output=f"done:{payload}", last_agent=SimpleNamespace(name="Researcher"))


class FailingRunner:
    @staticmethod
    def run_sync(agent, payload):
        raise TimeoutError("lost")


def test_openai_adapter_returns_bounded_run_output():
    executor = OpenAIAgentsExecutor(agent_spec=OpenAIAgentSpec("Researcher", "research carefully", "gpt-x"), agent_factory=Agent, runner=Runner)
    result = executor.execute(ExecutionRequest("a", "research", "topic", "input"))
    assert result.disposition is ExecutionDisposition.CONFIRMED
    assert result.output == "done:input"


def test_model_failure_is_known_failure_for_read_work():
    executor = OpenAIAgentsExecutor(agent_spec=OpenAIAgentSpec("Researcher", "x"), agent_factory=Agent, runner=FailingRunner)
    result = executor.execute(ExecutionRequest("a", "research", "topic", "input", side_effect_class="READ"))
    assert result.disposition is ExecutionDisposition.FAILED


def test_reasoning_executor_refuses_authoritative_side_effects():
    executor = OpenAIAgentsExecutor(agent_spec=OpenAIAgentSpec("Worker", "x"), agent_factory=Agent, runner=FailingRunner)
    result = executor.execute(ExecutionRequest("a", "publish", "target", "input", side_effect_class="WRITE"))
    assert result.disposition is ExecutionDisposition.FAILED
    assert "cannot perform authoritative side effects" in result.error
