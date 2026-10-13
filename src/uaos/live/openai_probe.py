from __future__ import annotations

from dataclasses import dataclass

from uaos.execution.models import ExecutionDisposition, ExecutionRequest
from uaos.execution.openai_agents import OpenAIAgentSpec, OpenAIAgentsExecutor


@dataclass(frozen=True, slots=True)
class OpenAIProbeResult:
    disposition: str
    output: str
    last_agent: str | None


def run_openai_probe(model: str) -> OpenAIProbeResult:
    executor = OpenAIAgentsExecutor.from_installed(
        agent_spec=OpenAIAgentSpec(
            name="UAOS live provider probe",
            model=model,
            instructions="Return exactly the token UAOS_LIVE_OK and nothing else.",
        )
    )
    outcome = executor.execute(
        ExecutionRequest(
            action_id="live-openai-probe",
            action_name="provider_read_probe",
            target="openai-agents-sdk",
            payload="Return the required probe token.",
            side_effect_class="READ",
            cost_ceiling=0.10,
        )
    )
    if outcome.disposition is not ExecutionDisposition.CONFIRMED:
        raise RuntimeError(f"OpenAI executor probe failed: {outcome.error or outcome.disposition}")
    output = str(outcome.output).strip()
    if output != "UAOS_LIVE_OK":
        raise RuntimeError(f"OpenAI executor returned unexpected probe output: {output!r}")
    return OpenAIProbeResult(
        disposition=outcome.disposition.value,
        output=output,
        last_agent=outcome.evidence.get("last_agent"),
    )
