# Universal Agent OS — Entry Point

Status: `ACTIVE_PRIMARY_CONTROLLER`

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
- ambiguity still fails closed rather than guessing across multiple current tasks.

## Current routing

When routing or continuing, load:
- `config/INTENT_RESOLUTION_POLICY.json`;
- `config/AGENT_REGISTRY.json`;
- `state/TASK_INDEX.json`;
- the selected `state/tasks/<task>.json`.

There is one cross-domain controller: UAOS. Business repositories own domain code, rules, fine-grained business state, Canon/media/data and artifacts. They do not own cross-chat controller state.

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
- multiple non-default tasks are never merged;
- time-sensitive work is revalidated against current time/business semantics before material execution;
- current controller progress is stored under `state/tasks/`, while domain business progress remains in its declared domain authority;
- before executing a continued domain task, reread the domain business authority named by the current task state; cached `next_action` is a pointer, not permission to ignore fresher business state.

For the video domain, the current default project is the active original-digital-IP incubation task; the older video-growth program is explicit-only.

## Knowledge and learning

Only promoted/current knowledge is used by default. Raw evidence and candidates remain scoped and non-authoritative until evaluation/promotion. One project/day/book/result may create a candidate; it does not silently become a global rule.

## Host model

`config/HOST_PROFILES.json` defines persistence adapters:
- `CHATGPT_GITHUB`: controller JSON under `state/`; observed-HEAD CAS + authoritative reread; current tools/connectors are session capabilities.
- `LOCAL`: SQLite CAS/checkpoint runtime + local artifact store.

Both hosts share the same controller semantics. They are persistence adapters, not separate business workflows.

## Fresh ChatGPT bootstrap

UAOS core does not require account-level Custom Instructions. However, a completely fresh ordinary ChatGPT conversation has no deterministic way to know which private repository is the controller unless the host injects the bootstrap or the account carries one stable pointer.

For deterministic fresh-chat use in ordinary ChatGPT, use the single pointer stored at `docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md`. That pointer is bootstrap-only and non-authoritative; all real policy remains in UAOS.

## GitHub material writes

For UAOS controller state:
1. reread current `main` HEAD;
2. build one coherent tree/commit on that HEAD;
3. update `main` with `expected_sha=<observed HEAD>` and no force;
4. reread the exact written authority.

A stale writer must re-read and rebase; never overwrite concurrent work.

## External custom instructions

Account-level ChatGPT Custom Instructions must never contain a duplicate copy of UAOS policy. If used, keep only the stable bootstrap pointer stored at `docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md`.

A stale pointer to the retired controller is fail-safe because that repository's default branch is a tombstone redirect, but it should be replaced with the current pointer before relying on deterministic fresh-chat bootstrap.
