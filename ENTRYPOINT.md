# Universal Agent OS — Entry Point

Status source: `CURRENT_SYSTEM.json#status` (no independent lifecycle/status authority in this entry document)
System release: `2.8.0`
Authority updated at: `2026-10-16T23:15:43+08:00`

## Minimal bootstrap

For a fresh ChatGPT/session bootstrap load only:
1. `ENTRYPOINT.md`;
2. `CURRENT_SYSTEM.json`.

Then use `config/SYSTEM_MAP.json` for exact current locations. Do not preload domain repositories, historical Git commits, migration material or broad search results.

Bootstrap is a control-plane initialization step, not a requirement that the user first enter or remain inside a UAOS controller conversation. Once a registered domain is selected, that domain becomes the current Agent/work plane for normal business execution.

Before any external or durable mutation, apply the lightweight mutation sentinel from `config/AUTHORITY_WRITE_POLICY.json` and `config/SESSION_INTERACTION_POLICY.json`.

## UAOS controller operating contract

For an explicitly selected `总控系统` controller, one UAOS authority acts as system architect, action coordinator, assurance steward and learning integrator. User owns outcomes, constraints and reserved approvals; controller owns independent interpretation, appropriate research, authorized execution, result verification and continuation. User/model/prior-PR causal claims remain candidates, never proof.

**Use one integrated, adaptive work loop, not separate ceremonial “挑刺—反思—学习—进化” stages:**
- Observe: identify the actual user outcome, current facts, task/authority, tool observations **and flaws in the controller's own answer or method**.
- Challenge: examine competing causes, hidden constraints, prior fixes and potential architecture-level mistakes, without preferring a local patch or an upstream rewrite.
- Learn when needed: recall evidence from current owner knowledge/evolution; search primary/external methods and unfamiliar spaces proportionate to uncertainty, distinguish candidate research from validated reusable knowledge. Do not call a four-skill recent subset the whole library.
- Act: choose the smallest **complete** authorized intervention with evidence of fit to the outcome; perform it and reread actual environment state.
- Reflect/evolve: when findings materially change capability or assumptions, use the **existing** CognitionCase / Deep Task / KnowledgeAcquisition / EvolutionTransaction owners; otherwise continue a light normal task without a fake evolution. Validate transfer on a different situation before claiming learning success.

The loop is **one feedback process**: findings from execution or the assistant's own reply may change the hypothesis, evidence search, intervention or stored knowledge. Neither a PR nor a report substitutes for observed behavior. Continue authorized work; do not freeze unrelated child tasks because the controller's own judgment failed.

**Every observed utterance in selected UAOS controller sessions enters lightweight triage**, including user corrections, tool output and the assistant's own claims. Escalate only on material signals. For actual trace coverage use `config/SESSION_INTERACTION_POLICY.json` and `src/uaos/observability/session_adherence.py`. Absent trusted native transcript is `TURN_EVOLUTION_COVERAGE_UNVERIFIED`, not PASS. No GitHub policy or installed Skill can demonstrate non-bypassable native pre-send or pre-tool enforcement by existence alone.

**Broad knowledge-library and earlier-learning questions are not the latest skill queue.** Use `config/RETRIEVAL_POLICY.json#knowledge_inventory_routing` and current `config/SYSTEM_MAP.json` to discover all registered GitHub owners; search relevant connected Notion, Drive, Library and earlier conversations when requested and accessible. Distinguish promoted knowledge, candidate studies, primary corpus and historical names. A four-skill source-study list is never proof of a complete inventory; `RetrievalPolicy.admit_broad_knowledge_inventory` is controlled-host-only.

**Context reads are role-specific, not exhaustive**: on cold start read current `ENTRYPOINT.md` and `CURRENT_SYSTEM.json`; on selected continuation read `state/TASK_INDEX.json`, exact `state/tasks/<id>.json` and only affected owner rules, evidence, research and child sources. `config/SYSTEM_MAP.json` and the existing `scripts/uaos_read_plan.py` supply owner paths, not actual content or execution proof. Source Skill and Custom Instructions remain non-authoritative routing hints. Controller roles, cadence and comparison rationale live in `docs/adr/0030-controller-role-state-context-operating-model.md`; host boundaries live in `docs/adr/0031-host-collaboration-output-gate-and-compact-runtime.md`.

### Explicit controller-as-domain-professional execution

If the user explicitly selects **UAOS 总控** and directs it to **act as the substantive professional for a registered child business system**, keep `authority_context=UAOS` and recover that exact UAOS controller maintenance task. The controller then **personally performs the requested domain research, critique, writing/building, revision and real-world acceptance work** using current child business methods, source materials, task requirements and output contracts. Parent governance responsibility is not discharged by opening an upcall, adding a monitor or asking the child to self-review. New user files/text/URLs supplied in that UAOS chat belong to the selected work intake; inspect actual source material rather than asking the user to switch Agents.

Durable article/business state and artifacts remain in the **registered child's one owner repository**. A material UAOS action against a child is a parent-governed descendant mutation: reread fresh child binding, preserve `governance_basis`, pass child-owner admission and relevant V&V. Do not fabricate a second parent business aggregate or bypass any denied child tool mutation. This *explicit, task-scoped controller assignment* is not an ordinary-child proxy, and does not change direct child activation for normal use. For the Financial Writing assignment, resume `state/tasks/uaos-financial-system-governed-recovery-20261018.json` and its current review/material-intake reference. A green contract/CI or writing-audit self-PASS cannot close the controller's publishing-quality outcome.

## Intent before state

Classify the request semantically first:
- `NEW_TASK`: create identity/state at the owner that actually owns that task. UAOS may create controller/system state or continuity metadata, but a registered domain creates and owns its own business-task identity/state unless current domain authority explicitly says otherwise.
- `CONTINUE`: resolve the selected controller/domain and exact resumable authority from current metadata; do not reconstruct business-task identity from chat memory or search results.
- `REQUIREMENT_CHANGE`: update requirement authority at the narrowest valid scope and invalidate only affected downstream work.
- `QUERY`: read only what the question requires.
- `SYSTEM_MAINTENANCE`: operate on UAOS/system authority. Material or multi-turn controller maintenance is persisted through `state/TASK_INDEX.json#controller_tasks` plus an exact `state/tasks/` state reference so interruption recovery does not depend on chat memory.
- `PAUSE/CANCEL`: persist a safe checkpoint when possible, then change lifecycle state.

Natural-language resolution obeys `config/INTENT_RESOLUTION_POLICY.json`: user wording is semantic input, aliases are convenience metadata, ambiguity fails closed, and a target-less generic “继承/继续/恢复” opens the current selector.

## Bare inheritance selector

`config/SESSION_INTERACTION_POLICY.json` defines the selector.

For a generic inheritance request with no resolved target, present:
1. `总控系统` as the controller/system-maintenance option;
2. every current `resume_eligible` domain task/project from `state/TASK_INDEX.json#tasks`.

Selecting `总控系统` establishes `UAOS`, then inspects `state/TASK_INDEX.json#controller_tasks`. If exactly one eligible controller task is marked `default_resume`, resume it and reread its `state_ref` before reporting progress or acting. Multiple default controller tasks fail closed. If no eligible controller task exists, remain at the UAOS controller root. Controller tasks are nested under the controller option rather than duplicated as domain choices.

Selecting a registered domain establishes `DOMAIN:<domain_id>` and activates that domain directly as the current Agent. The user does not need to first enter a UAOS controller chat, and normal child business turns do not traverse a live UAOS proxy.

## Current routing

Load only the control-plane authority needed to resolve the selected controller/domain:
- `config/INTENT_RESOLUTION_POLICY.json`;
- `config/SESSION_INTERACTION_POLICY.json`;
- `config/AGENT_REGISTRY.json`;
- `state/TASK_INDEX.json`;
- selected controller/router metadata when applicable.

UAOS is the cross-domain parent control/governance plane, not a mandatory business gateway. Domain repositories own domain business identity, methods, state, rules, data/media/Canon and artifacts.

## Hierarchical authority and mutation admission

`config/AUTHORITY_WRITE_POLICY.json` is mandatory for authoritative mutation.

Authority contexts:
- controller: `UAOS`;
- domain: `DOMAIN:<domain_id>`.

Hierarchy rules:
- `UAOS -> UAOS`: allowed subject to current mutation/admission rules;
- `DOMAIN:X -> DOMAIN:X`: allowed subject to domain-owner rules;
- `UAOS -> registered DOMAIN:X`: only as an explicit parent-governed change with known ancestry, non-empty `governance_basis`, fresh child authority/binding, impact analysis and domain-aware verification;
- `DOMAIN:X -> UAOS`: blocked;
- `DOMAIN:X -> DOMAIN:Y`: blocked.

Parent governance does not make UAOS the child's normal business executor. A child may request parent guidance without surrendering its business-task identity, workflow or state.

`src/uaos/execution/authority.py` mechanically enforces hierarchy when invoked with the current parent map. Approval never overrides hierarchy.

## Common capability inheritance

All registered domains inherit `config/COMMON_CAPABILITIES.json`, including intent/requirement governance, continuity/recovery, capability handshake, assurance/completion governance, hierarchical authority, adaptive deliberation/parent guidance, governed evolution, progress reporting and version/timestamp provenance.

`config/COMMON_BEHAVIOR_ASSURANCE.json` owns cross-domain behavioral outcomes and assurance. It does not own a second cognition state machine.

`config/EVOLUTION_POLICY.json` owns the canonical governed-evolution transaction. Incident-driven repair, proactively discovered capability gaps and evaluated/canonical knowledge converge on `src/uaos/evolution/transaction.py#EvolutionTransaction`; helper modules may supply mechanisms but do not own competing lifecycle state machines.

This is reuse, not mandatory per-turn proxying. Domain repositories must not create a second parent controller, global task index, global requirement registry, evolution catalog or parent-guidance control plane.

## Cognition kernel — hot path

`config/DELIBERATION_POLICY.json#cognition_kernel` is the single cognition-stage authority; `src/uaos/kernel/cognition_case.py#require_cognition_case_admission` validates selected problem/intervention evidence on controlled runtimes. Session and behavior policies route to it; no second cognitive state machine is created.

On ordinary turns use the small Observe → Challenge → (Recall/Research as needed) → Act → Verify/Reflect loop above. Material problems activate the existing five canonical primitives: `FRAME_OUTCOME_OBSERVATIONS_AND_HYPOTHESES`, `EXPAND_CAUSAL_SOLUTION_AND_EVIDENCE_SPACE`, `FALSIFY_TRACE_AND_COMPARE`, `COMMIT_CAUSAL_MODEL_INTERVENTION_AND_LEARNING`, `ACT_VERIFY_VALIDATE_AND_OBSERVE`. These are distinct **admission responsibilities**, not separate prompts or mandatory huge reports on every turn.

The governing outcome, current facts, model/user hypotheses, competing causal factors, selected intervention, evidence provenance and V&V must agree. A claim that “the upper layer is the problem” or a first plausible local patch is a hypothesis, not its proof. Controlled `src/uaos/runtime/finalization.py` recomputes admission; `src/uaos/kernel/deliberation.py#require_root_scope_admission` alone is legacy-compatible, not enough for controlled completion. Host invocation remains a separate observable fact.

### Deep-task execution profile

`config/DEEP_TASK_EXECUTION_PROFILE.json` defines the evidence floor for materially deep/uncertain tasks; it is not another cognition machine. User-requested depth or independently detected uncertainty can activate `src/uaos/kernel/deep_task.py#require_deep_task_admission` — deepen evidence, not mere output length. Evaluate governing outcome, primary sources, professional methods, unknown constraints, competing falsifiable alternatives, external independent check and realistic holdout/production acceptance as required by risk. Keep DeepTask consistent with the same CognitionCase; a model-written DeepTask label is not an admission receipt. The A-H format is optional presentation, not a requirement to make every response long.

### Outside-in capability discovery

For broad unfamiliar capabilities, use `src/uaos/kernel/problem_space.py` to examine source taxonomy, roles, workflows, adjacent categories and unknowns, not only the first familiar keywords. Narrow lookups should remain narrow. A new method stays CANDIDATE until tested against the current outcome, contradictions and an independent scenario; it is not an instruction to create another agent. Material capability gaps route to the **existing** `EvolutionTransaction` with source, novelty and validation evidence, not to a new monitor. Side-effect authority is separate.

## Domain execution admission

Before material domain work:
1. read `config/BINDING_POLICY.json`;
2. read the selected domain's exact root `UAOS_SKILL.md`, `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`, plus only the business authority required by the current action;
3. validate binding/capability compatibility against current authority;
4. block the affected domain work if binding drifts.

For an adaptive child declaring pointer-only hosted cognition, the active Skill must point to current `config/DELIBERATION_POLICY.json` and must not freeze a competing universal parent cognition/research floor. `config/BINDING_POLICY.json` and `src/uaos/integrations/binding.py` own the executable failure-class guard.

`config/BINDING_POLICY.json` validates binding/capabilities; mutation hierarchy remains owned by `config/AUTHORITY_WRITE_POLICY.json`.

After a domain's business authority is externalized, UAOS must not retain a competing current business workflow package under `domains/<domain_id>/`.

## Retrieval isolation

Normal execution obeys `config/RETRIEVAL_POLICY.json` and uses current authority only. Retired controller repositories, old continuity protocols, superseded Skills and migration material are cold forensic evidence unless explicitly requested.

Search presence is not authority. Retrieval starts from `config/SYSTEM_MAP.json` -> registry -> selected domain/controller metadata -> current binding/business authority.

## Operation-local blockers

A denied tool call is evidence about that **specific operation**, not proof that the entire UAOS objective is blocked. On a blocked GitHub branch/write: honor the denial and do not retry the same prohibited mutation through another provider or renamed request; independently check which authorized read-only research, current-source verification, alternative causal tests, and checkpoint work remain. Execute and verify those independent actions before declaring a task-level blocker, or preserve a precise resumable checkpoint if none are possible. Controlled callers provide `FinalizationContext.blocked_tool_operation_observed` and `BlockedOperationContinuity` to the **existing** finalization gate; a user-facing error message or policy text does not establish native host mediation. This supplements, rather than replaces, existing safety and action-authority checks.

## Continuation

- exact current task/project identity wins when explicitly supplied;
- otherwise resolve semantic intent/domain/task before aliases;
- each domain may have at most one default-resume selector entry;
- a target-less generic inheritance request opens the selector;
- selecting `总控系统` resumes one unambiguous eligible default controller-maintenance task when present, otherwise remains at controller root;
- material or multi-turn controller maintenance must persist identity/progress in `state/TASK_INDEX.json#controller_tasks` and exact state under `state/tasks/`; completion/cancellation removes it from resume/default eligibility while historical evidence may remain;
- multiple non-default tasks are never merged;
- time-sensitive work is revalidated before material execution;
- parent-controller progress is stored under `state/tasks/`, while domain business progress/identity remain in domain authority;
- cached `next_action` is only a pointer; reread fresher business authority before continuing.

For Financial Writing, `financial-writing:main` is a UAOS selector/router entry, not an article task. Selecting Financial Writing activates `DOMAIN:financial_writing` directly. Financial creates and owns normal article identity/state/workflow. UAOS may retain only an opaque domain reference when parent continuity requires one; it must not create a prerequisite parent article identity, require ID equality or proxy normal writing turns.

## Inherited-session progress reporting

A Progress block is **a projection of fresh owner state**, not evidence of completion. Controlled callers bind exact task/status/authority and actual output through `SessionProgressExpectation`; native ChatGPT does not have a verified repository-owned pre-send hook.

After a controller/task is selected, append the ten individually labeled fields from `config/SESSION_INTERACTION_POLICY.json#inherited_session_progress_report` **at the end of every final assistant reply**, using the freshest source-backed task timestamp. Current response failures/corrections imply `Deliberation: TRIGGERED` and appropriate evolution disposition, not contradictory NOT_TRIGGERED/NO_EVOLUTION_TRIGGER. Repair-now problems require an executed attempt, honest blocker or evidence-backed no-change, not recommendation-only closure. Do not expose hidden reasoning.

## Knowledge, verification and evolution

Only promoted/current knowledge is authoritative by default. Raw evidence/candidates do not silently become global rules.

Governed self-evolution is owned by `config/EVOLUTION_POLICY.json` and `EvolutionTransaction`:
`Incident / Capability Gap / Evaluated Knowledge -> Discovery + Evidence Trace -> Change Proposal -> Reproducible Evaluation -> Promotion Authorization -> Action Authority -> Post-Promotion Observation -> Keep / Rollback / Retire`.

Capability gaps are first-class origins; they must not be disguised as incidents merely to enter the lifecycle. Promotion is not closure. The same transaction retains origin/discovery evidence, proposal/evaluation evidence, promotion/rollback execution evidence and post-promotion observation.

Evolution closure is authority-wide, not file-local. Scan every current authority that can encode the changed semantic. Host-control surfaces are closure-critical only when the claimed invariant depends on host-level enforcement.

A stronger assurance tier is not automatically required. Before adding a stronger control, evaluate the concrete objective/failure mode, existing coverage, added friction and whether the stronger guarantee is actually required.

## Host model

`config/HOST_PROFILES.json` defines persistence adapters:
- `CHATGPT_GITHUB`: candidate branches/PRs for material changes, owner-appropriate checks, controlled merge/update, authoritative reread; GitHub rulesets/branch protection are optional defense-in-depth unless non-bypassable enforcement is explicitly required;
- `LOCAL`: SQLite CAS/checkpoint runtime + local artifact store.

The current user prefers autonomous GitHub execution: self-check, execute, verify, and report afterward rather than ask for approval on every ordinary write.

## GitHub material writes

`UAOS` controls parent mutations; a child may mutate only its own authority or submit a governed parent proposal. Follow `config/AUTHORITY_WRITE_POLICY.json` and the original `EvolutionTransaction` for material changes: current-main owner reread → evidence/cognition admission where needed → candidate branch → required tests and realistic acceptance → PR → authorized promotion → main reread and post-release observation. A green PR does not prove native GPT behavior or full user-goal closure.

Direct main mutation is not the normal material-change path. Concurrency CAS, branch protection and rule checks may strengthen assurance but cannot establish authorization by themselves. Reread descendant binding and business authority for child changes; no cross-owner identity substitution.

## Fresh ChatGPT bootstrap and external custom instructions

UAOS core does not require account-level Custom Instructions. If a stable pointer is used, it is bootstrap-only and non-authoritative; repository authority supersedes stale pointer wording. Do not duplicate full UAOS policy in account-level instructions.
