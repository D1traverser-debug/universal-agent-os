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
    """Reasoning-only SDK adapter with explicit, mandatory user-visible admission.

    For internal model results, default behavior remains read-only and lightweight.
    A caller delivering the SDK output to a user MUST opt into user_visible=True,
    provide a trusted FinalizationContext callback, and pass UAOS finalization
    *inside this adapter* before a CONFIRMED output is returned. SDK guardrails
    may provide another check but are not a substitute for this emission gate.
    This only mediates invocations using this adapter; it does not intercept
    ChatGPT product-native responses or raw GitHub connector calls.
    """

    def __init__(
        self, *,
        agent_spec: OpenAIAgentSpec,
        agent_factory: Callable[..., Any],
        runner: Any,
        user_visible: bool = False,
        finalization_context_provider: Callable[[ExecutionRequest, Any], FinalizationContext] | None = None,
    ) -> None:
        if user_visible and finalization_context_provider is None:
            raise ValueError("USER_VISIBLE_REQUIRES_FINALIZATION_CONTEXT_PROVIDER")
        if not user_visible and finalization_context_provider is not None:
            raise ValueError("FINALIZATION_CONTEXT_ONLY_ALLOWED_FOR_USER_VISIBLE")
        self.agent_spec = agent_spec
        self._agent_factory = agent_factory
        self._runner = runner
        self._user_visible = user_visible
        self._finalization_context_provider = finalization_context_provider

    @classmethod
    def from_installed(
        cls, *,
        agent_spec: OpenAIAgentSpec,
        user_visible: bool = False,
        finalization_context_provider: Callable[[ExecutionRequest, Any], FinalizationContext] | None = None,
    ) -> "OpenAIAgentsExecutor":
        from agents import Agent, Runner
        return cls(
            agent_spec=agent_spec, agent_factory=Agent, runner=Runner,
            user_visible=user_visible, finalization_context_provider=finalization_context_provider,
        )

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
        evidence: dict[str, Any] = {
            "last_agent": getattr(getattr(result, "last_agent", None), "name", None),
            "delivery_scope": "USER_VISIBLE" if self._user_visible else "INTERNAL_ONLY",
        }
        if self._user_visible:
            # The trusted caller must derive context from observed host facts, not
            # from the model's own statements about completion or Progress.
            assert self._finalization_context_provider is not None
            try:
                context = self._finalization_context_provider(request, result)
                if not isinstance(context, FinalizationContext):
                    raise TypeError("INVALID_FINALIZATION_CONTEXT")
                receipt = admit_final_response(str(result.final_output), context)
            except Exception as exc:
                # Fail closed: an output may not escape simply because its checker
                # crashed or rejected it. No potentially unvalidated model output
                # is attached to the failure receipt.
                return ExecutionOutcome(
                    disposition=ExecutionDisposition.FAILED,
                    error=f"USER_VISIBLE_FINALIZATION_REJECTED:{type(exc).__name__}:{exc}",
                )
            evidence["uaos_finalization"] = "ADMITTED"
            evidence["closure_decision"] = receipt.closure_decision.value
        return ExecutionOutcome(
            disposition=ExecutionDisposition.CONFIRMED,
            output=result.final_output,
            evidence=evidence,
        )
