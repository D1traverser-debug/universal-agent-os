# Universal Agent OS — ChatGPT Entry Point

Status: ACTIVE_PRIMARY_CONTROLLER
Successor of: `D1traverser-debug/universal-continuity-agent`

## Minimal bootstrap

When UAOS is used from ChatGPT, load only:
1. `ENTRYPOINT.md`
2. `CURRENT_SYSTEM.json`

Then load `config/AGENT_REGISTRY.json` and `state/TASK_INDEX.json` only when routing or continuation is required. Do not preload every domain repository.

## Intent first

Classify the user request before touching durable task state:
- NEW_TASK: create a new UAOS task. Never inherit an old business stage merely because the domain matches.
- CONTINUE: resolve an exact UAOS task or a legacy task seed. If a legacy task has not yet been imported, read its declared source checkpoint once, translate it through the UAOS adapter, then write only UAOS continuity state afterwards.
- REQUIREMENT_CHANGE: update requirement authority and invalidate only affected downstream work.
- QUERY: read only what is needed.
- SYSTEM_MAINTENANCE: operate on UAOS itself. Never resume an ordinary business task by accident.
- PAUSE/CANCEL: checkpoint first when possible, then change lifecycle state.

## Host model

UAOS has one control model with two persistence adapters:
- CHATGPT_GITHUB: free ChatGPT/GitHub host. Durable controller state is JSON under `state/`; material writes use current-main observed-head CAS and authoritative reread. Current search/connectors/plugins/tools are session capabilities, not permanent background capabilities.
- LOCAL: SQLite authority/checkpoint runtime and local content-addressed artifacts.

Both hosts use the same Task, Requirement, WorkUnit, Action, Artifact, Knowledge and Assurance semantics. They are not separate business workflows.

## Agent/domain routing

`config/AGENT_REGISTRY.json` is the sole active registry for the four migrated business Agents:
- financial-writing-agent -> `financial_writing`
- a-share-event-driven-agent -> `ashare`
- novel-writing-agent -> `novel`
- video-growth-agent -> `video`

The business repositories remain domain code/rule/artifact providers. They are no longer independent cross-chat controllers. Their old v3.7 continuity/lease/resume_epoch files are compatibility evidence only.

New tasks use UAOS-native domain workflows. Existing unfinished tasks use `state/TASK_INDEX.json` migration dispositions. After a legacy task is imported, never dual-write its old continuity state.

## Continuation rules

- Exact task id or alias wins.
- Domain-scoped CONTINUE may use that domain's single default entry.
- Bare CONTINUE across multiple eligible domains must not guess. Use current conversational task identity if durably bound; otherwise present the small set of candidates.
- Stale time-sensitive tasks are reconciled before resume. In particular, a past A-share premarket task must not execute as if it were still premarket.
- Source checkpoints/artifacts remain readable for provenance after migration, but UAOS is the continuity authority after import.

## Capability rules

Discover capabilities from the active host at execution time. Prefer INCLUDED/FREE capabilities that meet permission and quality floors. PAID and UNKNOWN-cost capabilities are disabled unless explicitly authorized. Session-only tools may not be represented as background workers.

Missing capability handling is WorkUnit-scoped: safe fallback -> degraded execution; otherwise WAITING_CAPABILITY. Side-effecting actions never fail over blindly across providers; UNKNOWN outcomes are reconciled first.

## Material state writes in ChatGPT/GitHub host

For controller state under this repository:
1. reread current `main` HEAD;
2. build one coherent Git tree/commit on that HEAD;
3. update `main` with `expected_sha=<observed HEAD>`;
4. reread the written authority.

Do not use the retired universal-continuity lease/resume_epoch protocol. CAS protects against stale concurrent writers; task identity and action idempotency protect business semantics.

## Old controller

`D1traverser-debug/universal-continuity-agent` is RETIRED_READ_ONLY. It may be read for historical evidence only. Never create new tasks, leases, maintenance runs or controller state there.
