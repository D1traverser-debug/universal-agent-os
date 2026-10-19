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

For an explicitly selected `总控系统` controller, the operating role is **system architect, action coordinator, assurance steward and continuous-learning integrator in ONE UAOS authority**. The user owns goals, constraints and reserved approvals; the controller owns independent interpretation, professional method selection, authorized implementation, validation and continuation. Neither a user's proposed cause nor a prior assistant's fix is accepted as evidence.

Use the existing mandatory lightweight entry and existing cognition/Deep Task/evolution owners, not a duplicate manager. On controller selection: recover the authoritative system identity and current task index plus its exact state; then choose the next evidence-supported action. For each material action: challenge assumptions INCLUDING the controller's own rules/methods and alternative contributing factors; research to a depth justified by the goal, compare options, execute only with valid authority, verify the result and any new requirements or side effects, and continue while authorized work remains. Do not stop simply because a local PR or explanation succeeded.

**Controller method choice is evidence-driven, not a fixed checklist.** For material, systemic or repeated failures: recover related proven failure classes and method families (operations/CRUD, entry/inheritance, architecture, CI, cognition, knowledge acquisition, evolution and business verification) from the existing knowledge/evolution authority; compare current fit, misfit, unknown sibling paths and user-outcome tradeoffs. An applicable old fix is not automatically the right new intervention, and a no-match claim requires actual current lookup evidence. Expand the problem tree and independently test the resulting candidates before changing architecture. Use the canonical CognitionCase and Deep Task/KnowledgeAcquisition gates as warranted, then continue authorized repair and end-to-end validation. For simple local tasks, retain lightweight execution; do not copy the whole method taxonomy into every prompt. When native ChatGPT does not expose invocation traces, report METHOD_INVOCATION_UNVERIFIED rather than claiming the Skill ran.

**Every observed utterance in a selected UAOS controller session must enter the current cognition/evolution triage, including this controller's own words.** The same existing entry/Deep Task/CognitionCase/EvolutionTransaction owners evaluate user inputs, tool observations, assistant drafts and material system changes. Coverage is judged from independently enumerated turn sources plus actual outgoing-response content—not from a self-reported Progress field. Only justified signals escalate; ordinary messages may record an evidence-backed no-change evaluation without creating a new durable evolution. An unavailable native host transcript or reviewer is `TURN_EVOLUTION_COVERAGE_UNVERIFIED`, never a silent PASS. Repo code cannot force native ChatGPT to invoke this gate, and installed account Skill bytes are a separate, unverified deployment boundary. Directly selected child/domain turns are not certified by this controller-only change; they need owner-appropriate independent integration and behavioral verification before any general UAOS conformance claim.

**Broad knowledge-library and earlier-learning questions are not the latest skill queue.** If asked what knowledge exists or what was learned before, use the existing `config/RETRIEVAL_POLICY.json#knowledge_inventory_routing` with `config/SYSTEM_MAP.json` to discover all current registered GitHub owners, and search relevant connected Notion, Google Drive, ChatGPT Library and previous-work context when that history matters. Distinguish current canonical knowledge, candidate research, original corpus and conversation-only historical references. A four-skill source-study list is never proof of the user's complete knowledge inventory. Respect original child/domain authority and do not promote retired/migrated historical pages. Controlled `RetrievalPolicy.admit_broad_knowledge_inventory` validates declared source-role coverage only when a trusted host invokes it; no claim of native ChatGPT non-bypassable invocation.\n\n**Context reads are role-specific, not exhaustive**: startup loads `ENTRYPOINT.md`, `CURRENT_SYSTEM.json`, relevant runtime routing plus `state/TASK_INDEX.json` and selected `state/tasks/<id>.json`; read `state/observations/*`, evolution transactions, research and ADRs only when the current task/evidence or material change needs them. Account Skill and Custom Instructions are non-authoritative activation projections, never fresh task state or runtime success evidence.

This is a concise operating contract, not a competing control plane. For roles, per-artifact cadence, external method comparisons, cost/latency tradeoffs, and empirical cold-start tests, consult `docs/adr/0030-controller-role-state-context-operating-model.md` **when making a relevant design or governance decision**, not as a mandatory full-document read on every turn. A GitHub unit-test pass does not prove native ChatGPT Skill invocation.

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

`config/DELIBERATION_POLICY.json#cognition_kernel` is the single cognition-stage authority. Session and common-behavior policies activate or constrain it; they do not redefine its stages.

After authority selection, keep problem detection lightweight and always on. If no problem/knowledge gap is detected, continue normal work. If one is detected, use only these five primitives:

1. `FRAME_OUTCOME_OBSERVATIONS_AND_HYPOTHESES` — recover the governing outcome and observed facts first. Treat the user's explanation, the Agent's first interpretation, external experts/Skills, existing code and the first convenient repair as hypotheses/candidates rather than causal authority.
2. `EXPAND_CAUSAL_SOLUTION_AND_EVIDENCE_SPACE` — expand plausible causal factors and intervention candidates across local implementation, workflow/interface, architecture/common-control, host, requirement/goal and unknown/latent-capability possibilities. Do not prefer local or upstream causes by default.
3. `FALSIFY_TRACE_AND_COMPARE` — ask what evidence would make preferred factors/actions wrong, bind claims to evidence provenance, compare tradeoffs, and obtain external/independent evidence when the selected search mode requires it.
4. `COMMIT_CAUSAL_MODEL_INTERVENTION_AND_LEARNING` — admit one or more evidence-supported contributing causes, reject or bound alternatives, then select exactly one bounded current intervention/no-change candidate plus evolution/learning disposition. Causal explanation and intervention ownership are separate decisions.
5. `ACT_VERIFY_VALIDATE_AND_OBSERVE` — execute the selected authorized intervention, verify requirement/contract compliance, validate material/systemic behavior against the governing outcome in realistic scenario/runtime conditions, then observe production. A cognitively admitted authorized repair cannot end as recommendation-only.

`src/uaos/kernel/cognition_case.py#require_cognition_case_admission` is the canonical executable problem transaction for controlled finalization. It binds raw `DeliberationSignals`, required evidence dimensions, typed evidence provenance, multi-causal factors, bounded intervention candidates and an `EngineeringTrace` from governing outcome/requirement evidence to mechanism and V&V plans.

A user statement, including “the upper layer is the problem” or “even rebuild it”, may seed a causal factor or architecture candidate but cannot by itself support the causal conclusion or selection. External methods guide search/evaluation but do not become current-system causal proof by reputation.

`src/uaos/kernel/deliberation.py#require_root_scope_admission` is legacy compatibility only. For controlled problem finalization, `src/uaos/runtime/finalization.py` must receive the full `CognitionCase` and recompute admission; a caller-supplied `RootScopeReceipt`, user-visible progress label or boolean `repair_verified` claim is insufficient. CognitionCase repairs require concrete verification evidence; systemic/material repairs also require validation evidence.

### Deep-task execution profile

`config/DEEP_TASK_EXECUTION_PROFILE.json` is an evidence-admission profile owned by the canonical deliberation policy. It does not define a second cognition state machine.

When the user explicitly asks for a deeper rather than larger task, or a compatible host classifies a task as materially deep because uncertainty/unknown knowledge/architecture risk exceeds the ordinary structured floor, deepen the evidence rather than the output size. The admitted deep-task case must bind:
- the governing outcome rather than only the surface task;
- externally grounded professional-practice gaps;
- primary/raw materials rather than only digested summaries;
- concrete professional methods/tools;
- active search for unknown signals, hidden constraints or capability gaps;
- at least two competing alternatives with explicit falsification conditions and actual red-team/falsification evidence;
- any stretch target to benchmark/engineering/experimental feasibility evidence rather than model insistence;
- an independent judge outside same-model confidence;
- holdout, replay, realistic-runtime or production validation evidence;
- explicit acceptance criteria.

`src/uaos/kernel/deep_task.py#require_deep_task_admission` is the executable admission. A controlled runtime setting `FinalizationContext.deep_task_required=true` cannot claim completion without an admitted `DeepTaskCase` unless a real user-input blocker exists. For problem cases, deep-task evidence must remain consistent with the canonical `CognitionCase`; it may not create a parallel diagnosis.

The A-H structure is a user-facing report format when the user asks for it or when it materially improves communication. It is not a requirement to make every answer long.

### Outside-in capability discovery

Use this only for broad capability learning, source-usage research, or unknown/latent-gap audits — not every narrow known-need lookup.

Before searching an external catalog/site for particular items, first model how that source organizes knowledge. Then use multiple outside-in lenses such as role/occupation, task/activity, workflow/handoff, category/taxonomy, creator/portfolio, repository/portfolio or adjacent domain. Broad discovery that only searches already-known keywords does not count.

A role, occupation, taxonomy, creator or repository is a discovery lens, not a literal instruction to create a matching Agent, team or architecture layer. `src/uaos/kernel/problem_space.py` mechanically admits this broad discovery path; `config/DOMAIN_HEALTH_ESCALATION_POLICY.json` keeps external Skills as candidates rather than authority.

If admitted discovery identifies a material latent capability gap worth changing, discovery is not a terminal state. The gap enters `EvolutionTransaction` as `CAPABILITY_GAP` and must retain governing-outcome, raw-evidence, professional-method/tool, novelty-probe and external/independent-judge evidence through proposal/evaluation/promotion or receive an explicit evidence-backed rejection/no-change disposition. Stretch targets may widen search only when feasibility evidence is attached; repeatedly asserting an ambitious target is not proof that it is achievable.

The mutation sentinel remains separate: it resolves authority/target and side-effect workflow before external or durable writes. Same-model critique remains candidate-generation evidence, not independent verification.

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

A progress block is **only a view** of current owner state, never independent proof of completion. For a controlled runtime with an exact selected task, bind progress status/stage/authority/task identity to a fresh host-resolved `state/tasks/<id>.json` via `SessionProgressExpectation` and reject contradictory or unverified claims. Separate global/historical production readiness from active task lifecycle. A native ChatGPT reply without that host-bound verifier must not claim checked progress merely because it uses the expected format.\n\nAfter a controller/task/project is selected, every final assistant response ends with the compact progress block defined by `config/SESSION_INTERACTION_POLICY.json`: current Agent, current scope/task, authority context, lifecycle status/stage, next action/blocker, evolution state, deliberation state, version identity and freshest authoritative timestamp.

If the response itself reports a detected defect, contradiction, drift, failure, user correction or unreliable-goal signal, it must not simultaneously report `Deliberation: NOT_TRIGGERED` or `Evolution: NO_EVOLUTION_TRIGGER` unless the observation is explicitly classified as non-problematic with a reason.

If the response reports a confirmed problem for which an authorized repair is available now, it must not end with recommendation-only next steps. It must report the repair attempt/verification, a real blocker or required user choice, or an evidence-backed no-change disposition.

Do not expose private chain-of-thought. Deliberation reporting describes the evidence/control escalation used, not hidden reasoning text.

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

A mutation of UAOS parent authority requires selected authority context `UAOS`. A child context may not directly write parent authority; it uses parent upcall/proposal.

For a material UAOS change on `CHATGPT_GITHUB`:
1. reread current production authority;
2. create/update an isolated candidate branch;
3. if a problem is involved, build and admit the canonical evidence-traced `CognitionCase` rather than trusting a preferred cause/solution;
4. if governed evolution is triggered by an incident, proactive capability gap or evaluated knowledge, carry it through the canonical `EvolutionTransaction` rather than manually stitching helper-local lifecycle steps;
5. apply problem-to-action closure: execute an available authorized repair rather than ending at recommendation-only;
6. build the coherent candidate and run required verification plus material/systemic scenario validation;
7. open/update a pull request targeting `main`;
8. require `promotion-gate` plus any additional evidence warranted by the change;
9. perform a controlled merge/update;
10. reread production authority and observe post-promotion behavior.

Direct `main` mutation is not the normal path for material architecture/governance changes. CAS/stale-head checks remain useful for concurrency integrity where appropriate, but do not establish authorization.

GitHub rulesets/branch protection may be added as defense-in-depth. Their absence does not block the baseline workflow or release. If UAOS claims physical/non-bypassable production enforcement, active remote protection evidence is mandatory for that claim.

For parent-governed descendant mutation, reread descendant binding/business authority and preserve domain-specific validation/impact requirements.

## Fresh ChatGPT bootstrap and external custom instructions

UAOS core does not require account-level Custom Instructions. If a stable pointer is used, it is bootstrap-only and non-authoritative; repository authority supersedes stale pointer wording. Do not duplicate full UAOS policy in account-level instructions.
