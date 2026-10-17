# ChatGPT Fresh-Chat Bootstrap Pointer

UAOS repository authority remains the source of truth. ChatGPT Custom Instructions are bootstrap-only and non-authoritative. The bootstrap pointer may assign the acting session a lightweight self-classification responsibility, but it is not a policy authority, classifier owner, or application-level execution gate.

## Recommended Custom Instructions

Use this single compact pointer on every ChatGPT plan. It is intentionally kept within the current 1,500-character Free/Go limit, so UAOS does not maintain separate account-instruction variants by subscription tier:

> For every request, independently assess the minimum sufficient investigation, deliberation, verification, and execution needed for the underlying goal. Do not require me to label a task complex, systemic, architectural, uncertain, or ask for deeper/better work. Keep simple tasks lightweight; an explicit depth request is a mandatory escalation signal, not the only trigger.
>
> When I ask to continue, inherit, resume, or work with persistent Agent projects, bootstrap from `D1traverser-debug/universal-agent-os@main:ENTRYPOINT.md` and `CURRENT_SYSTEM.json`. Interpret wording semantically; do not require exact aliases or create aliases from casual wording. Resolve through UAOS, reread the selected domain's current authority, and never treat retired repositories or old continuity files as current authority.
>
> After a UAOS controller/domain is selected, load `config/NATIVE_SESSION_RUNTIME_PROFILE.json` and use it as the compiled hot-path projection for problem/depth routing, cognition, mutation, closure and progress. It is not authority: on profile drift or system maintenance, reread its canonical source policies. If authorized work can continue without missing user input, continue now; never use `next` or another no-op user message as the workflow clock. Repository authority overrides this pointer.

Do not paste the full UAOS policy or the Deep Task evidence dimensions into Custom Instructions. Duplicating policy there creates drift, prompt bloat, and a second stale source of behavior. The bootstrap-only pointer's job is to recover current authority and direct the acting native session to one compiled effective hot-path projection; the repository remains responsible for the detailed semantics and evidence admission.

## Why this split

- Custom Instructions are account-level direct guidance applied across chats, so they are useful as a persistent bootstrap surface.
- Memory is not a replacement for this pointer because remembered context is relevance-selected and does not guarantee that every historical detail is used on every response.
- The repository owns the changing UAOS policies. `config/NATIVE_SESSION_RUNTIME_PROFILE.json` is generated from current Session/Deliberation/Host authority and is CI-checked against those sources, so the native session does not have to reconstruct effective behavior from several large policy files.
- The compiled profile is a read model, not another source of truth. When it drifts, generation/CI must fail and canonical source policy wins.
- User wording may force escalation, but the user is not the classifier. The selected Agent/session is responsible for independently recognizing when ordinary execution depth is insufficient.

## Enforcement boundary

Custom Instructions and the compiled native profile improve bootstrap consistency and reduce runtime policy-assembly burden, but they do not prove that the ChatGPT product runs a UAOS pre-send validator before every response. They also do not prove a repository-controlled pre-tool hook or non-bypassable semantic-signal injector. Hosts controlled by UAOS should use `src/uaos/runtime/finalization.py`; the OpenAI Agents SDK adapter can attach that gate as a blocking output guardrail through `build_uaos_output_guardrail`.

For native ChatGPT, the strongest accurate claim remains behavioral: with personalization enabled, this bootstrap pointer instructs the session to recover current authority and consume the compiled effective runtime projection. It is not a repository-controlled physical complete-mediation guarantee.
