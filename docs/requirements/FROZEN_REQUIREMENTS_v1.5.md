# Clean-Slate v5 — 冻结需求规格 v1.5

Status: `FROZEN_BASELINE_V1_5 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-14
Updated-at: 2026-10-14T13:48:00Z

v1.5 incorporates v1.0 + v1.1 + v1.2 + v1.3 + v1.4 except where this delta explicitly sharpens runtime/session topology or deliberation admission. It does not replace domain business authority; it clarifies how registered child Agents are activated and how triggered cognition/evolution becomes enforceable before material change.

## V15-01 — Registered child Agents are directly activatable work planes
A registered domain Agent must be usable from a fresh chat without requiring the user to first enter, remain in, or proxy normal business turns through a UAOS controller conversation.

The bootstrap/selector may read UAOS control-plane authority to identify the selected controller or domain. Once a domain is selected:
- the selected domain becomes the current Agent for normal business execution;
- authority context is `DOMAIN:<domain_id>`;
- the domain executes against its own current business authority, workflow, state and artifacts;
- UAOS remains available as parent control/governance capability but is not a mandatory per-turn business gateway.

Parent authority therefore does not imply parent ownership of child business identity, state or workflow.

## V15-02 — Parent and child business identities are distinct unless the child explicitly contracts otherwise
UAOS controller/router/task identity and a registered domain's business identity are distinct namespaces by default.

Correlation may use a domain-declared opaque reference when parent continuity actually needs one. UAOS must not create a prerequisite parent business identity, require parent/child identifier equality, rename a child identity or duplicate the child's per-business-task registry unless the current domain authority explicitly defines that contract.

For Financial Writing specifically, article identity/state/workflow remain Financial-owned; `financial-writing:main` is selector/router metadata, not an article workspace.

## V15-03 — Common capability inheritance is not runtime proxying
A child inheriting UAOS common capabilities means reuse of parent governance/control capabilities, not execution through a live parent business proxy.

A child may consume common requirements, assurance, deliberation, evolution, continuity and parent-guidance contracts while retaining direct business execution. Parent upcall remains an escalation path, not a prerequisite for ordinary child work.

## V15-04 — Triggered deliberation is fail-closed admission for material change
When `config/DELIBERATION_POLICY.json` determines that deliberation is required for a material architecture/governance change, or for a material change after a trigger such as user correction, repeated failure, architecture gap, conflicting evidence or high risk, the required deliberation dimensions are admission requirements rather than optional advice.

Before mutation/promotion:
- construct the current signals from observed evidence rather than from the preferred solution;
- run the current deliberation selector;
- satisfy every required escalation dimension with evidence;
- perform external method/architecture research when required;
- perform counterexample search when required;
- do not label same-model reflection as independent verification.

If required evidence is missing, material mutation/promotion must fail closed.

## V15-05 — Evolution closure is authority-wide, not file-local
A change triggered by governed evolution may not be reported `RESOLVED` merely because the edited files or targeted tests pass.

Before closure, scan all current authoritative surfaces capable of encoding the changed semantic, including as applicable:
- `ENTRYPOINT.md`;
- `CURRENT_SYSTEM.json`;
- repository instructions;
- session/binding/authority/deliberation/common-capability policies;
- task/router state and task index;
- bootstrap pointers;
- affected domain Skill/manifest/adapter/capability/business authority;
- readiness/assurance snapshots.

Any contradiction must be resolved or explicitly bounded before closure. Final candidate-tree evaluation and post-promotion production observation remain required at the assurance level appropriate to the change.

## V15-06 — Control-plane topology is a checkable fitness property
Where practical, CI/architecture fitness checks must reject reintroduction of:
- mandatory UAOS-controller-chat entry before using a registered child;
- per-turn proxying of normal child business execution through UAOS;
- parent-created business identity as a prerequisite for ordinary child work;
- parent/child business identifier equality imposed without an explicit child contract;
- material triggered promotion that bypasses required deliberation evidence;
- evolution closure while current authority surfaces still contradict the promoted semantic.

## Authority composition
Current requirements authority = `FROZEN_REQUIREMENTS_v1.0.md` + `FROZEN_REQUIREMENTS_v1.1.md` + `FROZEN_REQUIREMENTS_v1.2.md` + `FROZEN_REQUIREMENTS_v1.3.md` + `FROZEN_REQUIREMENTS_v1.4.md` + this v1.5 delta.
