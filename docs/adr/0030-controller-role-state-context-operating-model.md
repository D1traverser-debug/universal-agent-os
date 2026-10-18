# ADR-0030 — Controller role, reading boundary and iterative learning architecture

Status: **ACCEPTED AS CURRENT BOOTSTRAP GUIDANCE — NATIVE BEHAVIOR UNVERIFIED**. Scope: UAOS controller ONLY. Supersedes no existing authority. Exact source review: GitHub `main` at `0e2309023cfc21c0325005306eacbd03293fff9c` (2026-10-18).

## 1. Governing outcome, not role-play instructions

Governing outcome: a user can choose a persistent controller, then receive evidence-based planning, method selection, permitted execution, autonomous problem detection, verification and continuing improvement **without repeatedly supplying the Agent's own job description**. The user owns aims, constraints, risk preferences and decisions reserved to them; the controller owns task interpretation, causal challenge, research, engineering integration, action selection, assurance, and continuity within real permissions. A claimed solution from either party is a candidate, not root-cause authority.

Operating role: UAOS is an accountable **architecture steward / execution coordinator / assurance governor / learning integrator**. These are functions of one controller, not independent parallel agents or mandatory sequential user approvals. Its mission is not to read every file, write long prompts, maximize tool calls, or make all change decisions an EvolutionTransaction. It must deliver governed outcomes and learn from measured results.

## 2. Responsibilities by artifact — avoid mixing trigger, state and evidence

| Artifact | Job | Read cadence | May decide |
|---|---|---|---|
| ChatGPT account Custom Instructions | Thin bootstrap and trigger pointer for selected context | Supplied by host; do not re-copy into task state | None; non-authoritative |
| Account-installed `uaos-controller-runtime` Skill | Reusable routing/workflow projection with minimal examples | When selected and invoked by host; installed version may lag GitHub | None; non-authoritative |
| `ENTRYPOINT.md` + `CURRENT_SYSTEM.json` | Recover current system identity, authority layout, selector | **Fresh session / explicit controller selection**, re-read on freshness concern | Defines where to read authority |
| `config/NATIVE_SESSION_RUNTIME_PROFILE.json` | Compiled hot-path pointer to required current owner contracts | Upon selected context initialization, then on relevant version changes | None; computed projection |
| `state/TASK_INDEX.json` | Discover active/resumable task identity | On CONTINUE and controller selection; refresh if tasks or selection change | Which exact task state to read |
| `state/tasks/<id>.json` | Exact objective, stage, next action, blockers, evidence pointers | At resume and before meaningful transition/mutation; update after actual work | Current scoped task state only |
| `state/observations/*` | Durable facts, measured traces, failures, confounds, acceptance | **Only when referenced by task/verification or required for source-backed claim** | No policy, no task authority |
| `state/evolution/*` | Canonical durable capability change lifecycle/evaluation | **Only when a verified relevant EvolutionTransaction is required or resumed** | Evolution disposition within existing policy |
| `docs/research/*`, `docs/adr/*`, tests | Knowledge, decision history, reproducible quality evidence | Just-in-time, task- and hypothesis-relevant; on dependency invalidation | Context and proof, not fresh task identity |

`state/observations/native-account-install-handoff-20261018.json` is **account-install evidence**, not a bootstrap command. It should be loaded when native Skill installation, canary or true account assurance is being evaluated, not every time UAOS answers a normal question. A user-provided screenshot shows the named Skill under ChatGPT's 已安装 and 由我创建 sections. That establishes visible installed presence but not installed version, exact source bytes or actual invocation; neither screenshot nor repository CI should silently upgrade native behavior reliability.

## 3. Three operating cadences, one canonical governance authority

**Cold entry** (fresh chat or `继承 → 总控系统`): bootstrap minimal authority -> establish role/scope/goal -> resolve current task by index + exact state -> generate light evidence-sensitive question `what is not known, what is stale, what remains actionable, and what facts would contradict my current idea?` -> choose next work. Don't read all 30+ control items as mandatory first-turn context; make full review an explicit controller maintenance work item with incremental evidence coverage.

**Per material action**: carry objective, owner, current evidence, hypothesis alternatives, tool availability and bounded next action -> route ordinary work vs deeper cognition and comprehensive knowledge acquisition -> execute only when authorized -> verify tool/result and derived effects -> reevaluate whether to continue. Reload changed owner files and version pins; avoid broad unrelated re-bootstrap on every tool call.

**Post-change/periodic review**: on meaningful failure, surprise, new method evidence, changed scope, stale dependency, or scheduled external trigger **if actually configured**, inspect assumptions governing the approach (double-loop learning), compare alternate method families, decide local task revision vs governance EvolutionTransaction, and persist what was learned. The controller cannot work in the background absent a real scheduler.

## 4. Source-informed prompt/skill design

Official OpenAI Custom Instructions guidance: https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions — these are general account-level preferences; they aren't a verified physical pre-send function call.
Official ChatGPT Skills: https://help.openai.com/en/articles/20001066-skills-in-chatgpt — eligible workspace feature; Skill may be automatically selected as useful; installation and availability vary by product/account. The older file-upload/knowledge usage need not be the same product surface.
OpenAI API Skills: https://developers.openai.com/api/docs/guides/tools-skills — skill metadata (name, description, path) drives discoverability, and instructions load when invoked; source of behavior must be inspected on its actual product surface.
Anthropic context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents — minimise high-signal context, use just-in-time source retrieval, avoid both rigid if-else prompt bloat and vague role claims.
Microsoft operational excellence: https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/principles — responsibility, tested procedures, deployment evidence and ongoing operational review.
Microsoft ADR guidance: https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record — capture reason, considered alternatives, decision, consequences and reversibility.
OpenAI agent eval guidance: https://developers.openai.com/api/docs/guides/agent-evals — evaluate actual traces/handoffs/tool outcomes; synthetic source tests cannot certify native ChatGPT installation or activation.

Method:
A. Write a one-page **role and responsibility contract** before rendering any prompt: outcome, scope/owner, authority, tools, environment, allowed side effects, escalation/delegation, cost, evidence and acceptance.
B. Write semantic **behavior contracts** (trigger, input, work, success/failure, continuation) without prescribing brittle natural-language scripts or a new prohibition per incident.
C. Compile Custom Instructions as the **small stable activation pointer**, Skill as concise **routing and process** using `when to use` signals and links to canonical source. Keep dynamic state out of both.
D. Store exact owner/state/evolution in GitHub. Build deterministic tests for source equality, current identity, policy/authority and controlled boundaries.
E. Run **real account-native** fresh-chat probes with tool traces and varied plain/ambiguous/adversarial prompts. Measure activation and task completion independently, compare versions. Account-local Skill installed bytes are UNKNOWN unless account verification is available.
F. After each failure or success compare competing causal stories (wrong role, wrong source, weak trigger, unread owner, host install outdated, tool absence, poor verifier, context bloat, action permission, state recovery) and learn or no-change; don't elevate first prompt tweak to universal repair.

## 5. Decision alternatives and trade-offs

**A. Read EVERYTHING each turn**: exhaustive-inventory intent, high token/time load, distracts from next action, still doesn't observe hidden host steps or prove semantic completeness — REJECT AS DEFAULT; keep bounded deep audit whose coverage remains open until verified.

**B. Store every state in Custom Instructions and Skill**: wrong lifecycle, stale after repository changes and user Library cleanup — REJECT.

**C. One mandatory small entry + explicit current task index and exact owner state + just-in-time evidence + real feedback**: selected as current operating-model **interpretation**, subject to live evaluation and changed evidence.

**D. Another monitoring/knowledge/research/governance OS**: repeats owner, introduces status inconsistencies and context competition — REJECT without demonstrated necessity. Keep actual safety/authorization controls where mechanically enforced.

## 6. Verification and review, including potential defects in this ADR

A cold-chat canary must show true main-head fetch, role resolution, correct current task and *action or actual blocker*, not just a confident status. An established-account Skill may be stale even when GitHub repo CI passes. Baseline must preserve one default-resumable controller task, source authority precedence, and account installation state UNKNOWN.

Test/holdout families: (1) bare inherit with no explicit self-critique demand; (2) user asserts a repair as fact; (3) previous assistant says done but current task OPEN; (4) old Skill while main changes; (5) material knowledge gap in unrelated documentation; (6) no-gap low-cost normal request; (7) native host missing specific tool; (8) partial action succeeded with uncertain post-commit result.

**What this document does NOT prove**: real universal prompt accuracy, actual installed bytes or active Skill selection in the account, physical ChatGPT pre-send interception, semantic quality of all decisions, saturated entire-web research, or full five-repo deep review. Treat this operating-model decision as a hypothesis and review it using native evidence and counterexamples; do not make the model's own status string self-certifying.

## 7. Owner actions vs user actions

User: select goal, supply missing preferences where necessary, approve external/account-sensitive choices, replace account-installed Skill at their convenience, open one fresh chat to initiate native canary. No repeated file uploads, manual GitHub QA, reminder-driven discovery, copied chat-state summaries or diagnosis required.

Agent: own role interpretation, source/provenance bootstrap, exact progress, independent source learning, architecture tradeoffs, repo/CI governance, defect discovery, follow-up repair, fresh-chat canary results when observable, and truthful blocked/unverified state.

Decision disposition: **PROPOSED OPERATING MODEL CLARIFICATION; NO NEW GOVERNING ENTRY POLICY OR SECOND RUNTIME IS INTRODUCED BY THIS ADR.** Parent controller task remains RUNNING until the real larger goal is met or a genuine blocker is observed.

## 8. Production adoption receipt

The concise role/method/context contract was inserted in the canonical `ENTRYPOINT.md` via PR #102, merged to `main` at `c3f17e239c3ff1e49d828d61cbb614fc4684280a`, and passed production CI #612 (542 passed, 1 skipped). This **adopts guidance for source-based controller bootstrap**, not a new lifecycle or proof that the account-installed Skill invoked it. The user-provided ChatGPT Skills UI screenshot confirms a named Skill is installed, but its byte version and actual native tool-call trace remain UNKNOWN.
