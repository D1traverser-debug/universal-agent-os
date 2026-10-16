# UAOS Repository Instructions

This repository is the sole cross-domain parent controller authority.

## Authority order

1. current user instruction within its valid scope;
2. `CURRENT_SYSTEM.json` + current UAOS controller/task/requirement/action state;
3. current registered domain `UAOS_SKILL` + `UAOS_MANIFEST` + `UAOS_ADAPTER` + exact domain business authority;
4. promoted current knowledge/evidence;
5. external references;
6. migration/history only when explicitly requested.

## Hard rules

- Do not create a second control plane, owner registry, task index, lease system, resume epoch or progress-receipt protocol.
- Do not infer current authority from search ranking, file age, chat memory, historical branches or migration files.
- Do not load `docs/migration/**` during normal execution.
- Apply `config/RETRIEVAL_POLICY.json` before controller/domain repository retrieval.
- Apply `config/BINDING_POLICY.json` before material domain execution or parent-governed descendant mutation.
- Missing hard capability blocks only the affected work unit; never fabricate execution or silently weaken the user's objective.
- Candidate/exploration state may not overwrite production/current authority before promotion.
- Time-sensitive tasks must be revalidated before resume.

## Hierarchical governance

UAOS is parent of registered domain Agents. A child may mutate its own authority but not UAOS or a sibling. UAOS may govern a registered descendant only with explicit hierarchy, `governance_basis`, fresh child authority/binding, impact analysis and domain-aware validation. Parent governance is not blind impersonation of domain expertise.

Parent authority is a control/supervision relationship, not a mandatory business gateway. A registered child can be selected directly in a fresh chat; after selection, normal business turns execute under `DOMAIN:<domain_id>` against the child's own business authority. The user does not need to first enter or remain in a UAOS controller conversation.

A child may issue a non-mutating parent upcall for diagnosis, goal clarification, replanning, architecture/method research, assurance or evolution support without surrendering its selected task authority, business identity, workflow or state.

## Canonical cognition kernel

`config/DELIBERATION_POLICY.json#cognition_kernel` is the only cognition-stage authority. Do not maintain a second ordered problem-solving state machine in repository instructions, session policy, common-behavior policy or a domain copy.

For a detected problem/knowledge gap use the five hot-path primitives:
1. `FRAME_AS_HYPOTHESIS` — user framing, Agent framing, external methods, existing code and first-fix ideas are candidates, not authority.
2. `EXPAND_PROBLEM_SPACE_WHEN_NEEDED` — test whether the case is local, workflow/interface, architecture/common-control, requirement/goal or an unknown/latent capability gap before narrowing.
3. `FALSIFY_COMPETING_FRAMES` — actively seek evidence that would make the preferred frame wrong; material/systemic work must preserve a rejected alternative and test upstream/architecture involvement.
4. `COMMIT_ROOT_SCOPE_AND_LEARNING_DISPOSITION` — only after evidence bounds/selects the layer may root scope, evolution disposition and durable-record need be committed.
5. `ACT_AND_VERIFY` — execute the smallest authorized repair/redesign/no-change/block and verify against the governing objective.

The detailed evidence floor and root-scope mechanics remain in `config/DELIBERATION_POLICY.json` and `src/uaos/kernel/deliberation.py`. `src/uaos/kernel/problem_closure.py` owns terminal action admission. Same-model critique may generate alternatives but is not independent verification.

For broad external capability learning, source-usage research or unknown-gap audits, apply the outside-in discovery admission in `src/uaos/kernel/problem_space.py`: model the source's own organization axes first, then use multiple lenses such as role/occupation, task/activity, workflow/handoff, category/taxonomy, creator/repository portfolio or adjacent domain. A known-keyword-only survey is not broad discovery. A role or taxonomy is a lens, not a literal new Agent/team/architecture requirement.

## Architecture experience evaluation

For material architecture work, also apply `config/ARCHITECTURE_EXPERIENCE_POLICY.json` and the executable admission in `src/uaos/kernel/architecture_experience.py`.

- Recover the governing user goal before interpreting proposed mechanisms. A user example, analogy, observation or hypothesis is evidence/candidate input, not a binding architecture requirement unless the user explicitly locks it.
- Do not evaluate architecture only as a spatial/static component map. Walk representative real tasks through the architecture, including success, failure/recovery, resume/interruption, correction/change and maintenance/evolution paths when applicable.
- For control-plane or Agent-experience changes, perform a CURRENT_AGENT dogfood walkthrough: act as the Agent that must understand and use the system, step by step, and record where the right authority/action/progress signal is or is not discoverable.
- Choose representations by concern. Ownership/dependency concerns normally need a structural view; ordering/lifecycle/recovery/handoff concerns need a temporal/behavioral view; actor-operability concerns need a cognitive/task walkthrough. Do not force one representation family onto every problem.
- Every walkthrough step must expose the intended action, observable progress evidence, plausible confusion/failure, and recovery/next-evidence path.
- Compare candidate architectures against governing goals and relevant tradeoffs. The fact that a mechanism was mentioned by the user, already exists in the repository, or is familiar is not sufficient selection evidence.
- Architecture promotion requires the scenario/walkthrough evidence to agree with the structural contracts; a clean static diagram or green unit test cannot by itself prove the architecture is usable in sequence.

## Autonomous mutation baseline

Before every external or durable mutation, apply the lightweight mutation sentinel from `config/AUTHORITY_WRITE_POLICY.json` and `config/SESSION_INTERACTION_POLICY.json`: resolve authority, target, read-vs-write, owner-appropriate workflow, and current problem/risk signals.

For material UAOS changes on `CHATGPT_GITHUB`, the normal workflow is:

`candidate branch -> pull request -> promotion-gate / owner-appropriate checks -> controlled merge/update -> authoritative reread`

This workflow provides isolation, auditability and reproducible evidence. Direct `main` mutation is not the normal path for material architecture/governance changes. CAS remains useful for stale-write/concurrency integrity where appropriate; it is not authorization.

GitHub rulesets, branch protection and mandatory reviews are optional defense-in-depth by default. Their absence does not block normal Agent operation or a verified release. They become required only when the user/risk model explicitly requires a non-bypassable physical-enforcement guarantee. Do not claim that guarantee without remote evidence.

The current user prefers autonomous GitHub execution: self-check, execute, verify and report afterward rather than request approval for every ordinary write.

For parent-governed descendant writes, reread that descendant's current binding/business authority and satisfy its validation/impact requirements before mutation.

## Evolution and anti-bloat

Repair the unique owning abstraction. Prefer extending/replacing/removing superseded mechanisms over layering parallel ones. A repeated failure requires failure-class/root-cause treatment and regression evidence before closure.

A proposed new mechanism must state existing overlap, why extension is insufficient, what it replaces/retires (or why nothing can be retired), new failure modes, rollback and complexity delta. Do not convert every incident into another guarantee sentence when a contract, state machine, fitness check or deletion is the correct fix.

Stronger assurance is not automatically required. Before adding a stronger control, ask which objective/failure mode requires it, what existing controls already cover, and whether the added operational complexity is justified.

## Custom instructions

External account Custom Instructions are never policy authority. If present, they should contain only a compact bootstrap pointer. Repository requirements and current authority override stale pointer wording. Custom Instructions may help bootstrap behavior across chats, but they are not physical enforcement.
