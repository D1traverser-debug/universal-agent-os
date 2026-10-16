# Universal Agent OS — Entry Point

Status: `CANDIDATE_AUTONOMOUS_MAINTENANCE_BASELINE`
System release: `2.5.2`
Authority updated at: `2026-10-16T10:09:00+08:00`

## Minimal bootstrap

For a fresh ChatGPT/session bootstrap load only:
1. `ENTRYPOINT.md`;
2. `CURRENT_SYSTEM.json`.

Then use `config/SYSTEM_MAP.json` for exact current locations. Do not preload domain repositories, historical Git commits, migration material or broad search results.

Bootstrap is a control-plane initialization step, not a requirement that the user first enter or remain inside a UAOS controller conversation. Once a registered domain is selected, that domain becomes the current Agent/work plane for normal business execution.

Before any external or durable mutation, apply the lightweight mutation sentinel from `config/AUTHORITY_WRITE_POLICY.json` and `config/SESSION_INTERACTION_POLICY.json`.

## Intent before state

Classify the request semantically first:
- `NEW_TASK`: create identity/state at the owner that actually owns that task. UAOS may create controller/system state or continuity metadata, but a registered domain creates and owns its own business-task identity/state unless current domain authority explicitly says otherwise.
- `CONTINUE`: resolve the selected controller/domain and exact resumable authority from current metadata; do not reconstruct business-task identity from chat memory or search results.
- `REQUIREMENT_CHANGE`: update requirement authority at the narrowest valid scope and invalidate only affected downstream work.
- `QUERY`: read only what the question requires.
- `SYSTEM_MAINTENANCE`: operate on UAOS/system authority, not an ordinary business task.
- `PAUSE/CANCEL`: persist a safe checkpoint when possible, then change lifecycle state.

Natural-language resolution obeys `config/INTENT_RESOLUTION_POLICY.json`: user wording is semantic input, aliases are convenience metadata, ambiguity fails closed, and a target-less generic “继承/继续/恢复” opens the current selector.

## Bare inheritance selector

`config/SESSION_INTERACTION_POLICY.json` defines the selector.

For a generic inheritance request with no resolved target, present:
1. `总控系统` as the controller/system-maintenance option;
2. every current `resume_eligible` task/project from `state/TASK_INDEX.json`.

Selecting `总控系统` establishes `UAOS`. Selecting a registered domain establishes `DOMAIN:<domain_id>` and activates that domain directly as the current Agent. The user does not need to first enter a UAOS controller chat, and normal child business turns do not traverse a live UAOS proxy.

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

This is reuse, not mandatory per-turn proxying. Domain repositories must not create a second parent controller, global task index, global requirement registry, evolution catalog or parent-guidance control plane.

## Cognition kernel — hot path

`config/DELIBERATION_POLICY.json#cognition_kernel` is the single cognition-stage authority. Session and common-behavior policies activate or constrain it; they do not redefine its stages.

After authority selection, keep problem detection lightweight and always on. If no problem/knowledge gap is detected, continue normal work. If one is detected, use only these five primitives:

1. `FRAME_AS_HYPOTHESIS` — treat the user's explanation, the Agent's first interpretation, external experts/Skills, existing code and the first convenient repair as hypotheses rather than authority.
2. `EXPAND_PROBLEM_SPACE_WHEN_NEEDED` — before narrowing, test local implementation, workflow/interface, architecture/common-control, requirement/goal and unknown/latent-capability possibilities appropriate to the case.
3. `FALSIFY_COMPETING_FRAMES` — ask what evidence would make the preferred explanation wrong; material/systemic cases must preserve an evidence-rejected alternative and test upstream/architecture involvement.
4. `COMMIT_ROOT_SCOPE_AND_LEARNING_DISPOSITION` — only after evidence bounds/selects the layer may the Agent commit root scope, evolution disposition and durable-record need.
5. `ACT_AND_VERIFY` — execute the smallest authorized repair/redesign/no-change/block and verify it against the governing objective. A cognitively admitted authorized repair cannot end as recommendation-only.

The detailed evidence depth, root-scope gate and architecture-experience rules remain in `config/DELIBERATION_POLICY.json`, `src/uaos/kernel/deliberation.py`, `config/ARCHITECTURE_EXPERIENCE_POLICY.json` and `src/uaos/kernel/problem_closure.py`.

### Outside-in capability discovery

Use this only for broad capability learning, source-usage research, or unknown/latent-gap audits — not every narrow known-need lookup.

Before searching an external catalog/site for particular items, first model how that source organizes knowledge. Then use multiple outside-in lenses such as role/occupation, task/activity, workflow/handoff, category/taxonomy, creator/portfolio, repository/portfolio or adjacent domain. Broad discovery that only searches already-known keywords does not count.

A role, occupation, taxonomy, creator or repository is a discovery lens, not a literal instruction to create a matching Agent, team or architecture layer. `src/uaos/kernel/problem_space.py` mechanically admits this broad discovery path; `config/DOMAIN_HEALTH_ESCALATION_POLICY.json` keeps external Skills as candidates rather than authority.

The mutation sentinel remains separate: it resolves authority/target and side-effect workflow before external or durable writes. Same-model critique remains candidate-generation evidence, not independent verification.

## Domain execution admission

Before material domain work:
1. read `config/BINDING_POLICY.json`;
2. read the selected domain's exact root `UAOS_SKILL.md`, `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`, plus only the business authority required by the current action;
3. validate binding/capability compatibility against current authority;
4. block the affected domain work if binding drifts.

`config/BINDING_POLICY.json` validates binding/capabilities; mutation hierarchy remains owned by `config/AUTHORITY_WRITE_POLICY.json`.

After a domain's business authority is externalized, UAOS must not retain a competing current business workflow package under `domains/<domain_id>/`.

## Retrieval isolation

Normal execution obeys `config/RETRIEVAL_POLICY.json` and uses current authority only. Retired controller repositories, old continuity protocols, superseded Skills and migration material are cold forensic evidence unless explicitly requested.

Search presence is not authority. Retrieval starts from `config/SYSTEM_MAP.json` -> registry -> selected domain/controller metadata -> current binding/business authority.

## Continuation

- exact current task/project identity wins when explicitly supplied;
- otherwise resolve semantic intent/domain/task before aliases;
- each domain may have at most one default-resume selector entry;
- a target-less generic inheritance request opens the selector;
- multiple non-default tasks are never merged;
- time-sensitive work is revalidated before material execution;
- parent-controller progress is stored under `state/tasks/`, while domain business progress/identity remain in domain authority;
- cached `next_action` is only a pointer; reread fresher business authority before continuing.

For Financial Writing, `financial-writing:main` is a UAOS selector/router entry, not an article task. Selecting Financial Writing activates `DOMAIN:financial_writing` directly. Financial creates and owns normal article identity/state/workflow. UAOS may retain only an opaque domain reference when parent continuity requires one; it must not create a prerequisite parent article identity, require ID equality or proxy normal writing turns.

## Inherited-session progress reporting

After a controller/task/project is selected, every final assistant response ends with the compact progress block defined by `config/SESSION_INTERACTION_POLICY.json`: current Agent, current scope/task, authority context, lifecycle status/stage, next action/blocker, evolution state, deliberation state, version identity and freshest authoritative timestamp.

If the response itself reports a detected defect, contradiction, drift, failure, user correction or unreliable-goal signal, it must not simultaneously report `Deliberation: NOT_TRIGGERED` or `Evolution: NO_EVOLUTION_TRIGGER` unless the observation is explicitly classified as non-problematic with a reason.

If the response reports a confirmed problem for which an authorized repair is available now, it must not end with recommendation-only next steps. It must report the repair attempt/verification, a real blocker or required user choice, or an evidence-backed no-change disposition.

Do not expose private chain-of-thought. Deliberation reporting describes the evidence/control escalation used, not hidden reasoning text.

## Knowledge, verification and evolution

Only promoted/current knowledge is authoritative by default. Raw evidence/candidates do not silently become global rules.

Governed self-evolution follows:
`Incident -> Failure Class -> Change Proposal -> Reproducible Evaluation -> Promotion Authorization -> Action Authority -> Post-Promotion Observation -> Keep / Rollback / Retire`.

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
3. if a problem is involved, complete the canonical cognition kernel and required evidence depth;
4. apply problem-to-action closure: execute an available authorized repair rather than ending at recommendation-only;
5. build the coherent candidate and run required assurance;
6. open/update a pull request targeting `main`;
7. require `promotion-gate` plus any additional evidence warranted by the change;
8. perform a controlled merge/update;
9. reread production authority and observe post-promotion behavior.

Direct `main` mutation is not the normal path for material architecture/governance changes. CAS/stale-head checks remain useful for concurrency integrity where appropriate, but do not establish authorization.

GitHub rulesets/branch protection may be added as defense-in-depth. Their absence does not block the baseline workflow or release. If UAOS claims physical/non-bypassable production enforcement, active remote protection evidence is mandatory for that claim.

For parent-governed descendant mutation, reread descendant binding/business authority and preserve domain-specific validation/impact requirements.

## Fresh ChatGPT bootstrap and external custom instructions

UAOS core does not require account-level Custom Instructions. If a stable pointer is used, it is bootstrap-only and non-authoritative; repository authority supersedes stale pointer wording. Do not duplicate full UAOS policy in account-level instructions.
