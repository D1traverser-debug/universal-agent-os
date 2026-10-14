# UAOS Repository Instructions

This repository is the sole cross-domain controller authority.

## Authority order

1. current user instruction within its valid scope;
2. `CURRENT_SYSTEM.json` + current UAOS task/requirement/action state;
3. current registered domain `UAOS_SKILL` + `UAOS_MANIFEST` + `UAOS_ADAPTER` + exact domain business authority;
4. promoted current knowledge/evidence;
5. external references;
6. migration/history only when explicitly requested.

## Hard rules

- Do not create a second control plane, owner registry, task index, lease system, resume epoch or progress-receipt protocol.
- Do not infer current authority from search ranking, file age, chat memory, historical branches or migration files.
- Do not load `docs/migration/**` during normal execution.
- Apply `config/RETRIEVAL_POLICY.json` before controller/domain repository retrieval.
- Apply `config/BINDING_POLICY.json` before material domain execution.
- Missing hard capability blocks only the affected work unit; never fabricate execution or silently weaken the user's objective.
- Candidate/exploration state may not overwrite production/current authority before promotion.
- Time-sensitive tasks must be revalidated before resume.

## Mutation

Material UAOS GitHub writes use observed-HEAD CAS: reread HEAD -> build commit on that tree -> update with expected SHA -> reread authority. Never force through a stale concurrent writer.

## Evolution

Repair the unique owning abstraction. Prefer replacing/removing superseded mechanisms to layering new parallel ones. A repeated failure requires failure-class/root-cause treatment and regression evidence before closure.

## Custom instructions

External account Custom Instructions are never policy authority. If present, they should only point to `D1traverser-debug/universal-agent-os@main:ENTRYPOINT.md`.
