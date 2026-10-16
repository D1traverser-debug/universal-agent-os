from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from uaos.runtime.finalization import FinalizationBlocked, FinalizationContext, admit_final_response

from .models import ExecutionDisposition, ExecutionOutcome, ExecutionRequest


@dataclass(frozen=True, slots=True)
class OpenAIAgentSpec:
    name: str
    instructions: str
    model: str | None = None
    output_guardrails: tuple[Any, ...] = ()


def build_uaos_output_guardrail(
    context_provider: Callable[[Any, Any, Any], FinalizationContext],
) -> Any:
    """Build a blocking OpenAI Agents SDK output guardrail around UAOS finalization.

    The import is lazy so the base package remains dependency-light. When this adapter
    is used by an Agents SDK host, a failed UAOS finalization admission trips the SDK
    output guardrail before the final output is returned to the caller.
    """

    from agents import GuardrailFunctionOutput, output_guardrail

    @output_guardrail(name="uaos_finalization_gate")
    def _guardrail(run_context: Any, agent: Any, agent_output: Any) -> Any:
        context = context_provider(run_context, agent, agent_output)
        try:
            receipt = admit_final_response(str(agent_output), context)
        except FinalizationBlocked as exc:
            return GuardrailFunctionOutput(
                output_info={"uaos_finalization_blocked": list(exc.reasons)},
                tripwire_triggered=True,
            )
        return GuardrailFunctionOutput(
            output_info={
                "uaos_finalization": "ADMITTED",
                "closure_decision": receipt.closure_decision.value,
            },
            tripwire_triggered=False,
        )

    return _guardrail


class OpenAIAgentsExecutor:
    """Bounded reasoning/generation adapter over OpenAI Agents SDK.

    This baseline adapter intentionally receives no side-effecting tools. UAOS
    durable task state, approvals, artifact identity and authoritative effects
    remain outside the Agents SDK run. Callers that use this executor for a final
    user-visible answer may attach the UAOS output guardrail through OpenAIAgentSpec.
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
        if self.agent_spec.output_guardrails:
            kwargs["output_guardrails"] = list(self.agent_spec.output_guardrails)
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
