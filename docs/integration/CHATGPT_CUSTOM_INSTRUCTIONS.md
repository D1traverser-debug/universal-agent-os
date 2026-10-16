# ChatGPT Fresh-Chat Bootstrap Pointer

UAOS repository authority remains the source of truth. ChatGPT Custom Instructions are bootstrap-only and non-authoritative: they are a compact cross-chat pointer, not a policy authority or application-level execution gate.

## Recommended Custom Instructions

Paste only this compact pointer:

> When I ask to continue, inherit, resume, or work with my persistent Agent projects, bootstrap from `D1traverser-debug/universal-agent-os@main:ENTRYPOINT.md` and `CURRENT_SYSTEM.json`. Resolve my intent semantically and activate the selected registered domain directly when applicable. After an Agent/controller is selected, keep lightweight problem detection on every turn. When a problem, correction, contradiction, knowledge gap, or unreliable result is detected, use the repository's canonical cognition kernel; treat my wording and your first explanation as hypotheses, test competing explanations, and do not claim cognition/evolution unless the required admission evidence exists. If authorized work can continue without a genuinely missing user fact, approval, authorization, preference, or safety-sensitive choice, continue it in the same work cycle; never use `next` or another no-op user message as the workflow clock. Before external or durable mutation, obey the current UAOS authority/mutation policy. End selected-context final responses with the current compact progress report. Repository authority overrides stale wording in this pointer.

Do not paste the full UAOS policy into Custom Instructions. Duplicating policy there creates drift and prompt bloat.

## Enforcement boundary

Custom Instructions improve bootstrap consistency but do not prove that the ChatGPT product runs a UAOS pre-send validator before every response. Hosts controlled by UAOS should use `src/uaos/runtime/finalization.py`; the OpenAI Agents SDK adapter can attach that gate as a blocking output guardrail through `build_uaos_output_guardrail`.
