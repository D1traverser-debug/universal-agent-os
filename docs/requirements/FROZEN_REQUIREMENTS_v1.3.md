# Clean-Slate v4 — 冻结需求规格 v1.3

Status: `FROZEN_BASELINE_V1_3 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-14
Updated-at: 2026-10-14T08:44:50Z

v1.3 incorporates v1.0 + v1.1 + v1.2 unchanged and adds explicit authority-isolation and evolution-observability requirements.

## V13-01 — Selected authority context is part of mutation admission
Once a controller or domain Agent/project has been selected for the current conversation, the selected authority context is a control-plane input, not display metadata.

Examples:
- controller context: `UAOS`;
- domain context: `DOMAIN:financial_writing`, `DOMAIN:video`, `DOMAIN:ashare`, `DOMAIN:novel`.

A mutating action must not be admitted without a verifiable selected authority context and target authority owner.

## V13-02 — Same-owner authoritative mutation rule
Authoritative mutation is fail-closed and same-owner by default.

- `UAOS -> UAOS` mutation: permitted subject to normal action/approval/CAS rules.
- `DOMAIN:X -> DOMAIN:X` mutation: permitted subject to that domain owner and normal action rules.
- `DOMAIN:X -> UAOS`: prohibited as a direct mutation.
- `DOMAIN:X -> DOMAIN:Y`: prohibited as a direct mutation.
- `UAOS -> DOMAIN:X` direct business mutation: prohibited; UAOS must dispatch/handoff to the domain owner or create an owner-scoped request/proposal instead of impersonating the domain owner.

Cross-scope reads remain governed by retrieval policy and are not automatically prohibited.

## V13-03 — Parent/common change requests from child context
When a child/domain context detects a parent/common mechanism defect, it may diagnose, research and produce a change proposal/evidence package, but it must not directly mutate parent UAOS authority.

The proposal is promoted only after execution is in the owning `UAOS` controller context. Switching owner/context is an explicit control-plane transition, not a hidden privilege escalation.

## V13-04 — Governed evolution must be observable during system maintenance
A user correction, repeated failure or maintenance finding that triggers governed self-evolution must expose its actual lifecycle state in durable maintenance evidence and in the inherited-session progress report.

At minimum report one of:
- `NO_EVOLUTION_TRIGGER`;
- `INCIDENT_RECORDED`;
- `FAILURE_CLASS_IDENTIFIED`;
- `PROPOSAL_DRAFT`;
- `EVALUATED`;
- `APPROVED`;
- `PROMOTED`;
- `OBSERVING`;
- `ROLLED_BACK`;
- `RETIRED`.

Do not claim that the evolution system was used merely because an edit resembles its intended behavior.

## V13-05 — Repository branch protection is defense-in-depth, not authority isolation
Git branch/ruleset protection and CAS protect repository write concurrency/integration policy. They do not encode the selected Agent owner and therefore cannot substitute for parent/child/domain authority isolation.

A repository may be unprotected at the GitHub branch layer while UAOS still enforces owner-scoped mutation admission. Conversely, a protected branch does not authorize a child Agent to mutate parent authority.

## V13-06 — Host-enforcement assurance must be explicit
When the active host exposes a raw connector that can write repositories outside the UAOS ActionCoordinator, UAOS must state that code-level authority gating cannot physically intercept an out-of-policy manual/direct connector call.

In that host, the system must:
1. enforce the authority rule in UAOS policy and execution APIs;
2. never intentionally perform such a bypass;
3. lower the mechanical-enforcement assurance for the raw connector surface; and
4. treat repository-scoped credentials/rulesets/tool mediation as the path to full host-level enforcement.

## Authority composition
Current requirements authority = `FROZEN_REQUIREMENTS_v1.0.md` + `FROZEN_REQUIREMENTS_v1.1.md` + `FROZEN_REQUIREMENTS_v1.2.md` + this v1.3 delta.
