from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .models import ExecutionDisposition, ExecutionOutcome, ExecutionRequest


@dataclass(frozen=True, slots=True)
class OpenAIAgentSpec:
    name: str
    instructions: str
    model: str | None = None


class OpenAIAgentsExecutor:
    """Bounded reasoning/generation adapter over OpenAI Agents SDK.

    This baseline adapter intentionally receives no side-effecting tools. UAOS
    durable task state, approvals, artifact identity and authoritative effects
    remain outside the Agents SDK run.
    """

    def __init__(self, *, agent_spec: OpenAIAgentSpec, agent_factory: Callable[..., Any], runner: Any) -> None:
        self.agent_spec = agent_spec
        self._agent_factory = agent_factory
        self._runner = runner

    @classmethod
    def from_installed(cls, *, agent_spec: OpenAIAgentSpec) -> "OpenAIAgentsExecutor":
        from agents import Agent, Runner
        return cls(agent_spec=agent_spec, agent_factory=Agent, runner=Runner)

    def execute(self, request: ExecutionRequest) -> ExecutionOutcome:
        if request.side_effect_class.upper() not in {"READ", "NONE"}:
            return ExecutionOutcome(
                disposition=ExecutionDisposition.FAILED,
                error="reasoning-only OpenAI Agents executor cannot perform authoritative side effects",
            )
        kwargs: dict[str, Any] = {
            "name": self.agent_spec.name,
            "instructions": self.agent_spec.instructions,
        }
        if self.agent_spec.model is not None:
            kwargs["model"] = self.agent_spec.model
        agent = self._agent_factory(**kwargs)
        try:
            result = self._runner.run_sync(agent, request.payload)
        except Exception as exc:
            return ExecutionOutcome(
                disposition=ExecutionDisposition.FAILED,
                error=f"{type(exc).__name__}: {exc}",
            )
        return ExecutionOutcome(
            disposition=ExecutionDisposition.CONFIRMED,
            output=result.final_output,
            evidence={"last_agent": getattr(getattr(result, "last_agent", None), "name", None)},
        )
