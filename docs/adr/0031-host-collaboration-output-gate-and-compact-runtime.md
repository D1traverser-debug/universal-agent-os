# ADR-0031 — ChatGPT / GitHub / controlled SDK: real execution boundary and compact native entry

Status: **ACCEPTED for the repository-controlled scope; native ChatGPT deployment and semantic reliability remain UNVERIFIED.**
Owner: UAOS; exact task `state/tasks/uaos-inheritance-review-20261018.json`; same evolution `state/evolution/EVO-20261018-INHERITANCE-REVIEW.json`.
Production sources: PR #149 (merged `c177a015926a8b0c659a236ed2f888491032a515`) and PR #150 (merged `51308cf85558f6dd99f45f95e51f60b5bc0c77b4`).

## Context and architecture problem

The old operating model conflated (1) ChatGPT's native model/tool route, (2) repository-defined Python admission functions, and (3) documents that describe intended operation. A Python gate can be correct while the ChatGPT reply, GitHub connector mutation or installed account Skill bypasses it. Report formatting and green CI were presented as native behavioral improvement. The installable Skill duplicated long authority prose and its existence did not prove actual activation.

These are interacting factors, not grounds for treating the user's suspected single root cause as established: no confirmed native product interception; guarded SDK run was optional; long native Skill context; knowledge retrieval and goal-fit remain behavioral/unverified; actual autonomous evolution has not run in this host.

## Decision: one authority, two explicitly different execution contracts

**A. ChatGPT-native + GitHub connector (current conversational host)**

- ChatGPT interprets requests and calls available connectors. The product decides whether to invoke its installed Skill. This GitHub repository **cannot** install that Skill, wrap every connector call or intercept every native final answer.
- The user-selected authority is GitHub `main`, not prior assistant replies or the generated Skill. Use the live task and owner paths; read large full bootstrap only on cold start/inheritance, exact task on continuation, affected policies on demand.
- `skills/uaos-controller-runtime/SKILL.md` remains **non-authoritative and generated**, and now keeps a compact high-signal entry (11,270 → 7,870 chars, 30% reduction). It preserves actor/goal checks, uncertainty, provenance, mutation workflow and all ten mandatory Progress fields. Source owners remain `config/*`, `state/tasks/*`, the single `EvolutionTransaction` and business owners.
- This route has **model-behavior assurance only** until product-host invocation/pre-send evidence exists. It must never be marked mechanically gated by Python.

**B. Repository-controlled OpenAI Agents SDK adapter (independently hosted, opt-in)**

- `src/uaos/execution/openai_agents.py#OpenAIAgentsExecutor` now has separate contracts for **INTERNAL_ONLY** (default) and **USER_VISIBLE** output.
- To choose USER_VISIBLE, the integrating host **must** provide `user_visible=True` and `finalization_context_provider(request, model_result)` at construction. Provider supplies its observed authority and task/Progress/closure facts; model self-claims cannot substitute.
- For USER_VISIBLE results, the adapter itself calls the existing canonical `src/uaos/runtime/finalization.py#admit_final_response` **before** returning CONFIRMED. It rejects missing Progress, unfinished work, malformed context and provider exceptions. A failed result carries no proposed model answer.
- Optional SDK output guardrail is supplementary. No second controller, policy engine or new knowledge database was introduced. `ActionCoordinator` retains trusted action/authority governance for hosts that actually route mutating actions through it.
- The adapter remains **reasoning-only** with no side-effecting model tools. It does not establish a real GitHub-writing GPT app, deploy the host, consume a paid API, or intercept current ChatGPT responses.

## Verification, counterexamples and falsification

- PR #149 candidate promotion gate: 658 passed / 2 skipped; live integration Postgres and object store passed, provider run skipped. Tests: missing context fails construction, invalid callback fails, plain SDK output with missing Progress cannot be delivered, unfinished-work clean-looking output fails, compliant output succeeds, internal-only read path remains.
- PR #150 candidate promotion gate: 660 passed / 2 skipped; native Skill regenerated exactly from its canonical builder; six retained host/progress/intent guarantees remain covered and new context-length tests hold. Live integration checks passed, OpenAI provider run skipped. `main` readback verifies 7,870-char generated Skill and SDK host profile.
- `OPENAI_AGENTS_SDK` host-controlled output admission is now enforced **only when a caller invokes the new `user_visible` route**. No independent production caller trace has been observed, so it remains runtime unit/integration evidence, not a user-product deployment guarantee.
- Positive counterexample: internal model steps legitimately emit intermediate text without a human-facing Progress; those are explicitly INTERNAL_ONLY and not approved for direct delivery.
- Negative counterexamples: native ChatGPT reply still omits Progress; SDK caller uses default INTERNAL_ONLY result as an externally visible response; self-selected current task is wrong; action has evidence references but does not solve the user's target. These remain failures requiring actual host/evaluation ownership, not ruled out by this ADR.
- A real native-session A/B assessment should compare concise vs previous Skill on blind unfamiliar goal semantics, full behavior traces, tool actions, and final user outcomes. No such production run was completed in this release.

## Rejected alternatives

- A second monitor/controller, a rewritten duplicate state machine or a new knowledge store: duplicates authority without native execution.
- Always copying 28K+ bootstrap and every policy verbatim into the Skill: wastes attention, creates source drift and still does not prove native compliance.
- Treating GitHub PR/CI as proof of native self-governance: invalid evidence promotion.
- Disabling child-repository work to fix controller understanding: unrelated to the failing capability and already retracted.
- Claiming the SDK guard covers ChatGPT product-native messages: false host-boundary assertion.

## Next technical work; not completed here

1. Confirm which account-specific Skill/Custom Instructions bytes are actually installed (GitHub source changes do not deploy).
2. Run genuine host-connected traces for selected ChatGPT sessions and separately for controlled SDK user-facing runs, including negative semantic goal-fit cases.
3. Use transcript **and environment end state** to assess independent judgment, knowledge reuse and autonomous evolution, not just progress formatting; preserve user input as a requirement, not unquestionable causal truth.
4. Independently check that simplifying the Skill reduces real invocation context/latency and does not regress capability on blind cases.
5. Continue legitimate business owner work while addressing controller defects; no blanket child audit suspension.

External architectural sources: OpenAI Agents SDK (`https://developers.openai.com/api/docs/guides/agents/sdk`), Anthropic agent evaluation (`https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents`), GitHub/VS Code harness-specific instructions (`https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/custom-instructions.md`). Methods are adapted where the host actually supports them.