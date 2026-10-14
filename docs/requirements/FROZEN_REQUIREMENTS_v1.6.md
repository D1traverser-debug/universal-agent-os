# Clean-Slate v6 — 冻结需求规格 v1.6

Status: `FROZEN_BASELINE_V1_6 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-14
Updated-at: 2026-10-14T15:20:00Z

v1.6 incorporates v1.0 + v1.1 + v1.2 + v1.3 + v1.4 + v1.5. It closes the gap between cognitive/policy admission and physical mutation enforcement. The governing principle is complete mediation: a production mutation invariant is not fully enforced while any known write path can bypass the enforcing control point.

## V16-01 — Production mutation requires complete mediation
Every write path capable of changing current/production authority must satisfy one of two conditions:
- it traverses a policy enforcement point that mechanically applies the current mutation/admission decision; or
- it is physically incapable of writing that production target.

A policy, prompt, Custom Instruction, self-review, Python guard or CI test does not by itself satisfy this requirement when a separate writer can still mutate production without passing that control.

## V16-02 — Separate policy decision from policy enforcement
UAOS may compute mutation/deliberation decisions in its control plane, but the host must provide an enforcement point that cannot be bypassed by the same writer identity.

For GitHub-hosted production authority:
- branch/repository rulesets are the production policy-enforcement boundary;
- direct writes to `main` are not an accepted production promotion path once ruleset enforcement is available;
- the normal production path is `candidate branch -> pull request -> required promotion gate -> protected merge`;
- no ChatGPT/GitHub App bypass entry is granted for the production ruleset;
- force-push and deletion of the protected production branch are prohibited.

Observed-HEAD CAS remains useful for concurrency correctness on mutable refs where it is allowed, but CAS is not a security/admission boundary and must not be presented as a substitute for protected promotion.

## V16-03 — Always-on sentinel, adaptive-depth cognition
The always-on part of cognition is a lightweight event/mutation sentinel, not a permanent heavy debate loop.

For every turn capable of changing external or durable state, the host/session must identify:
- selected authority context;
- target resource/authority;
- whether the action is mutating;
- whether the mutation path is mediated by the required enforcement point;
- whether current trigger signals require deeper deliberation/evolution.

If no material trigger exists, normal work continues without ritualized debate. If a trigger exists, `DELIBERATION_POLICY` selects the required depth and evidence.

## V16-04 — Custom Instructions are bootstrap, not enforcement
Account-level ChatGPT Custom Instructions may remain enabled as an always-applied bootstrap signal so fresh chats load current UAOS authority and activate the lightweight sentinel before persistent-Agent mutations.

They are not policy authority and do not count as physical enforcement. The authoritative policy remains in the repository, and mutation safety must survive omission, drift or model noncompliance at the prompt layer.

## V16-05 — Known bypass blocks `RESOLVED`
An evolution incident whose target invariant can still be violated by a known unmediated production write path must not be reported `RESOLVED`.

Permitted intermediate states include `REOPENED`, `LOGICALLY_MITIGATED__PHYSICAL_ENFORCEMENT_PENDING`, or `BLOCKED_HOST_ENFORCEMENT` as appropriate. A user may explicitly accept residual host risk, but risk acceptance is not equivalent to technical resolution and must be recorded separately.

## V16-06 — GitHub promotion gate is a stable required check
GitHub protection should require one stable `promotion-gate` status rather than a changing set of low-level jobs. The workflow may conditionally run expensive live verification according to changed-path/risk classification, but `promotion-gate` must fail unless every verification required for that change has succeeded.

The required gate itself must always produce a terminal status on pull requests targeting `main`.

## V16-07 — Host enforcement is assurance evidence
Production readiness must separately report:
- logical/cognitive admission status;
- repository/host enforcement status;
- actual remote protection evidence (for example active GitHub ruleset identity and required gate);
- any remaining bypass identity or path.

A local configuration declaring intended protection is not evidence that GitHub or another host actually enforces it.

## Authority composition
Current requirements authority = `FROZEN_REQUIREMENTS_v1.0.md` + `FROZEN_REQUIREMENTS_v1.1.md` + `FROZEN_REQUIREMENTS_v1.2.md` + `FROZEN_REQUIREMENTS_v1.3.md` + `FROZEN_REQUIREMENTS_v1.4.md` + `FROZEN_REQUIREMENTS_v1.5.md` + this v1.6 delta.
