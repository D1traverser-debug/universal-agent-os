# Universal Agent OS — Entry Point

Status: `ACTIVE_PRIMARY_CONTROLLER`
System release: `2.4.1`
Authority updated at: `2026-10-14T10:42:00Z`

## Minimal bootstrap

For a fresh ChatGPT/session bootstrap load only:
1. `ENTRYPOINT.md`;
2. `CURRENT_SYSTEM.json`.

Then use `config/SYSTEM_MAP.json` for exact current locations. Do not preload domain repositories, historical Git commits, migration material or broad search results.

## Intent before state

Classify the request semantically first:
- `NEW_TASK`: create a new UAOS task; never inherit unfinished state merely because the domain matches.
- `CONTINUE`: resolve an exact current UAOS task from `state/TASK_INDEX.json`; do not reconstruct task identity from search results or chat memory.
- `REQUIREMENT_CHANGE`: update requirement authority at the narrowest valid scope and invalidate only affected downstream work.
- `QUERY`: read only what the question requires.
- `SYSTEM_MAINTENANCE`: operate on UAOS/system authority, not an ordinary business task.
- `PAUSE/CANCEL`: persist a safe checkpoint when possible, then change lifecycle state.

Natural-language resolution obeys `config/INTENT_RESOLUTION_POLICY.json`:
- user wording is semantic input, not a command grammar;
- task aliases are convenience metadata, not required phrases;
- never add or mutate aliases merely because the user used one colloquial description;
- after semantic intent/domain resolution, use exact/default-resume mechanical rules;
- if a continued request resolves to one domain and that domain has exactly one default-resume task, that task is selected even when the wording matches no stored alias;
- a bare generic “继承/继续/恢复” that resolves to no domain or exact task opens the current inheritance selector instead of silently choosing a task;
- ambiguity still fails closed rather than guessing across multiple current tasks.

## Bare inheritance selector

`config/SESSION_INTERACTION_POLICY.json` defines the selector.

For a generic inheritance request with no resolved target, present:
1. `总控系统` as the controller/system-maintenance option;
2. every current `resume_eligible` task/project from `state/TASK_INDEX.json`.

Show enough current metadata to distinguish running/default, hold, and explicit-only projects. The menu is generated from current authority every time and never mutates aliases.

Selecting `总控系统` establishes controller maintenance/query context and authority context `UAOS`; it does not create a fake business task. Selecting a domain task establishes `DOMAIN:<domain_id>`.

## Current routing

When routing or continuing, load:
- `config/INTENT_RESOLUTION_POLICY.json`;
- `config/SESSION_INTERACTION_POLICY.json`;
- `config/AGENT_REGISTRY.json`;
- `state/TASK_INDEX.json`;
- the selected `state/tasks/<task>.json`.

There is one cross-domain parent controller: UAOS. Business repositories own domain methods, fine-grained business state, Canon/media/data and artifacts for normal execution. They do not own cross-chat controller state or parent governance policy.

## Hierarchical authority and mutation admission

`config/AUTHORITY_WRITE_POLICY.json` is mandatory for authoritative mutation.

The selected controller/domain is a real authority context:
- controller: `UAOS`;
- domain: `DOMAIN:<domain_id>`.

The relationship is hierarchical, not symmetric peer isolation:
- `UAOS -> UAOS`: allowed subject to normal action/approval/CAS rules;
- `DOMAIN:X -> DOMAIN:X`: allowed subject to domain-owner rules;
- `UAOS -> registered DOMAIN:X`: allowed only as an explicit parent-governed change with known ancestry, non-empty `governance_basis`, fresh domain binding/business authority, impact analysis and domain-aware verification;
- `DOMAIN:X -> UAOS`: direct authoritative mutation blocked;
- `DOMAIN:X -> DOMAIN:Y`: direct authoritative mutation blocked.

Parent governance is not permission to write a child blindly. UAOS must read the current child authority and preserve business-specific validation. A child can request parent guidance at any time without receiving parent write authority.

`src/uaos/execution/authority.py` mechanically enforces same-owner and registered ancestor-to-descendant admission when the hierarchy map is bound. `config/AGENT_REGISTRY.json` exposes each domain's `parent_authority`; `AgentLinkRegistry.authority_parent_map()` supplies the mapping. Approval never overrides hierarchy.

Git branch/ruleset protection is defense-in-depth, not the parent/child authority model. On `CHATGPT_GITHUB`, a raw native connector call is outside Python `ActionCoordinator`; UAOS policy still forbids out-of-policy bypass, while full physical enforcement additionally requires repository-scoped credentials/tool mediation and/or GitHub rulesets.

## Common capability inheritance

All registered domains inherit `config/COMMON_CAPABILITIES.json`, including:
- intent/requirement governance;
- cross-chat continuity and recovery;
- capability handshake and graceful degradation;
- assurance/evidence/completion governance;
- hierarchical authority governance;
- adaptive deliberation and parent guidance;
- governed self-evolution;
- inherited-session progress reporting;
- version/timestamp provenance.

This is reuse, not duplication. Domain repositories keep business methods/state/learning/artifacts. They must not create a second controller, task index, continuation plane, requirement registry, evolution catalog, architecture-advisor plane or parent-guidance controller.

## Adaptive deliberation and parent guidance

`config/DELIBERATION_POLICY.json` defines epistemic escalation. It is not a fixed self-question checklist.

Trigger signals decide when deeper deliberation is required; current evidence generates the actual questions, hypotheses, methods and search terms. The control path can escalate across:
- concrete/micro diagnosis;
- macro goal/topology alignment;
- governing-assumption challenge (double-loop style);
- external method/architecture research when current framing is insufficient;
- counterexample search for material proposals;
- genuinely independent verification for high-risk or disputed outcomes when available.

Use a micro -> macro -> micro loop: reproduce the concrete symptom, ask whether the governing goal/assumption/control structure is wrong when evidence warrants it, then return to the smallest correct change and verify concrete behavior plus strategic alignment.

Same-model self-critique/refinement/debate may generate candidates but is not automatically independent evidence. Do not run debate, architecture search or extra Agents as ritual. External patterns are candidate mechanisms: extract the relevant property, fit/misfit, costs/failure modes and minimum useful borrowing; popularity or names never become authority.

Delegated work may carry a bounded `GovernanceFrame` inside the existing `ContextPacket`: parent goal, local-goal linkage, non-goals, invariants, autonomy bounds, escalation conditions, stop conditions and verification expectations.

A selected child may issue `ParentUpcall` with problem/evidence/unknowns/requested outcome. UAOS returns `ParentGuidance` without automatically replacing the selected child task authority. Parent guidance may diagnose, replan, request external research/verification or decide that a parent-governed descendant change is required.

## Domain execution admission

Before material domain work:
1. read `config/BINDING_POLICY.json`;
2. from the selected registry entry read its exact root `UAOS_SKILL.md`, `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`, plus only the business authority required by the current action;
3. validate the binding against current repository state;
4. if controller/Skill/manifest/adapter/capability binding drifts, block the affected domain execution until reconciled.

A repository declaration is a capability ceiling, not proof that the active session can execute it.

## Retrieval isolation

All controller/domain repository retrieval obeys `config/RETRIEVAL_POLICY.json`.

Normal execution must not use retired controller repositories, old continuity protocols/task indexes/leases/resume metadata, superseded Skill/controller surfaces, or historical migration mechanisms.

Historical evidence is a cold forensic path through Git history. It may be accessed only for an explicit historical/forensic question and never overrides current authority.

Search presence is not authority. Retrieval starts from `config/SYSTEM_MAP.json` -> registry -> task -> current Skill/manifest/adapter chain.

## Continuation

- exact current task id/project identity wins when the user clearly provides one;
- otherwise resolve intent/domain/task semantics before consulting aliases;
- each domain may have at most one default-resume task;
- a domain-level continuation selects that one default task without requiring a literal alias match;
- a target-less generic inheritance request opens the selector;
- multiple non-default tasks are never merged;
- time-sensitive work is revalidated against current time/business semantics before material execution;
- current controller progress is stored under `state/tasks/`, while domain business progress remains in its declared domain authority;
- before executing a continued domain task, reread the domain business authority named by the current task state; cached `next_action` is a pointer, not permission to ignore fresher business state.

For the video domain, the current default project is the active original-digital-IP incubation task; the older video-growth program is explicit-only.

## Inherited-session progress reporting

After a controller or task/project has been selected, every final assistant response ends with the compact progress block defined by `config/SESSION_INTERACTION_POLICY.json`.

Report:
- current Agent/controller;
- current task/project or maintenance scope;
- selected authority context;
- lifecycle status and current stage;
- next action or blocker;
- actual governed-evolution state when triggered, otherwise `NO_EVOLUTION_TRIGGER`;
- material adaptive-deliberation escalation when triggered, otherwise `NOT_TRIGGERED`;
- governing version identity;
- freshest authoritative progress/update timestamp.

Do not expose private chain-of-thought. Deliberation reporting describes the control/evidence escalation used, not hidden reasoning text. Do not use response time as an authority timestamp or a schema number as a release number.

## Version and timestamp semantics

`CURRENT_SYSTEM.json` exposes the current `system_release_version` and `updated_at`.

Material continuation/reporting should prefer:
1. explicit authority/business `updated_at` or equivalent progress timestamp;
2. exact authoritative Git commit timestamp when the authority file has no own timestamp;
3. `UNKNOWN` if neither can be verified.

Version identity may include system release, domain runtime/profile/manifest version, task schema/version, artifact version/hash, or exact commit identity as appropriate.

## Knowledge, verification and evolution

Only promoted/current knowledge is used by default. Raw evidence/candidates remain non-authoritative until evaluation/promotion. One project/day/book/result may create a candidate; it does not silently become a global rule.

The Assurance layer already distinguishes declaration/structural/deterministic/semantic/independent/live-outcome evidence. Role-play or self-review must not be promoted to `INDEPENDENT` without real independence evidence.

Governed self-evolution follows:
`Incident -> Failure Class -> Change Proposal -> Reproducible Evaluation -> Promotion Authorization -> Action Authority -> Post-Promotion Observation -> Keep / Rollback / Retire`.

Before a material system proposal is promoted, apply adaptive deliberation when trigger signals exist. Repeated failure must challenge the governing abstraction instead of adding another local guarantee. A new mechanism states overlap, replacement/retirement, new failure modes, rollback and complexity delta.

For `CHATGPT_GITHUB` maintenance, durable evolution records live under `state/evolution/`. Surface real lifecycle state; do not claim evolution merely because an edit resembles it.

## Host model

`config/HOST_PROFILES.json` defines persistence adapters:
- `CHATGPT_GITHUB`: controller JSON under `state/`; observed-HEAD CAS + authoritative reread; current tools/connectors are session capabilities.
- `LOCAL`: SQLite CAS/checkpoint runtime + local artifact store.

Both hosts share controller semantics. They are persistence adapters, not separate business workflows.

## Fresh ChatGPT bootstrap

UAOS core does not require account-level Custom Instructions. A completely fresh ordinary ChatGPT conversation still needs the host to inject the bootstrap or one stable account pointer to this repository.

For deterministic fresh-chat use, use only the pointer at `docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md`; it is bootstrap-only and non-authoritative.

## GitHub material writes

A mutation of UAOS parent authority requires selected authority context `UAOS`. A child context may not directly write parent UAOS authority; it uses a parent upcall/proposal.

For a UAOS controller state mutation:
1. reread current `main` HEAD;
2. build one coherent tree/commit on that HEAD;
3. update `main` with `expected_sha=<observed HEAD>` and no force;
4. reread the exact written authority.

For a parent-governed descendant mutation, additionally read the descendant's current binding/business authority and preserve its validation/impact requirements before writing its repository. A stale writer must re-read and rebase; never overwrite concurrent work.

## External custom instructions

Account-level ChatGPT Custom Instructions must never contain a duplicate copy of UAOS policy. If used, keep only the stable bootstrap pointer stored at `docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md`.

A stale pointer to the retired controller is fail-safe because that repository's default branch is a tombstone redirect, but it should be replaced with the current pointer before relying on deterministic fresh-chat bootstrap.
