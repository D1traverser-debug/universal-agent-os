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

## Deliberation

Apply `config/DELIBERATION_POLICY.json` when trigger signals indicate cognitive/system risk. Do not promote the first plausible framing merely because it sounds coherent.

- Start from concrete evidence; move to macro goal/assumption/topology when warranted; return to the smallest correct concrete change.
- Trigger conditions select depth, not a finite question list. Generate questions/methods from current evidence and unknowns.
- If the current method/architecture knowledge is insufficient, search external evidence; do not remain confined to internally generated options.
- Same-model critique/refinement/debate may generate candidates but is not independent verification.
- Material proposals seek counterexamples. High-risk/disputed claims require real independent evidence when available or an explicit assurance ceiling.
- Do not run extra Agents, debates or architecture searches as ritual.
- For material architecture/governance changes and any material change after a trigger signal, call the executable deliberation admission (`require_deliberation_admission`) or its host-equivalent before mutation/promotion. If any required dimension lacks evidence, fail closed.
- Before declaring an evolution incident resolved, scan every current authority and host control surface that can encode or bypass the changed semantic; local edited-file success is not enough.

## Mutation and complete mediation

Before every external or durable mutation, apply the always-on mutation sentinel from `config/AUTHORITY_WRITE_POLICY.json` and `config/SESSION_INTERACTION_POLICY.json`. The sentinel is lightweight: resolve selected authority, target authority/resource, read-vs-write, required host enforcement point, and deliberation triggers. It does not force heavy meta-reasoning for ordinary low-risk work.

For material UAOS production changes on `CHATGPT_GITHUB`, the normal promotion topology is:

`candidate branch -> pull request -> required promotion-gate -> GitHub protected main -> merge/promotion -> authoritative reread`

Direct mutation of `main` through raw connector writes is not a normal production promotion path. The previous observed-HEAD CAS direct-main procedure is retired as a production security/admission mechanism. CAS remains a concurrency-integrity tool for candidate refs or other contexts where direct mutation is valid; CAS does not establish authority and does not replace complete mediation.

If the required GitHub ruleset/branch protection is absent or cannot be verified, do not claim physical enforcement or technical resolution of a mutation-control incident. A known bypass keeps the incident in an explicit non-resolved state.

For parent-governed descendant writes, reread that descendant's current binding/business authority and satisfy its validation/impact requirements before mutation.

## Evolution and anti-bloat

Repair the unique owning abstraction. Prefer extending/replacing/removing superseded mechanisms over layering parallel ones. A repeated failure requires failure-class/root-cause treatment and regression evidence before closure.

A proposed new mechanism must state existing overlap, why extension is insufficient, what it replaces/retires (or why nothing can be retired), new failure modes, rollback and complexity delta. Do not convert every incident into another guarantee sentence when a contract, state machine, fitness check or deletion is the correct fix.

An incident affecting authority or mutation safety cannot be `RESOLVED` while a known active path can bypass the claimed invariant. Logical mitigation and physical enforcement are reported separately.

## Custom instructions

External account Custom Instructions are never policy authority. If present, they should contain only the compact bootstrap + mutation-sentinel pointer in `docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md`. They may keep bootstrap behavior active across chats, but they are not physical enforcement.
