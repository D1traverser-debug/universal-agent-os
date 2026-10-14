# Clean-Slate v6 — 冻结需求规格 v1.6

Status: `FROZEN_BASELINE_V1_6 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-14
Updated-at: 2026-10-14T15:28:00Z

v1.6 incorporates v1.0 + v1.1 + v1.2 + v1.3 + v1.4 + v1.5. It closes the gap between cognitive/policy admission and physical mutation enforcement. The governing principle is complete mediation: a production mutation invariant is not fully enforced while any known write path can bypass the enforcing control point.

## V16-01 — Production mutation requires complete mediation
Every write path capable of changing current/production authority must satisfy one of two conditions:
- it traverses a policy enforcement point that mechanically applies the current mutation/admission decision; or
- it is physically incapable of writing that production target.

A policy, prompt, Custom Instruction, self-review, Python guard or CI test does not by itself satisfy this requirement when a separate writer can still mutate production without passing that control.

## V16-02 — Separate policy decision from policy enforcement
UAOS may compute mutation/deliberation decisions in its control plane, but the host must provide an enforcement point that cannot be bypassed by the same ordinary writer path.

For GitHub-hosted production authority:
- branch/repository rulesets are the production policy-enforcement boundary;
- direct writes to `main` are not an accepted normal production promotion path once ruleset enforcement is active;
- the normal production path is `candidate branch -> pull request -> required promotion check(s) -> protected merge`;
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

## V16-06 — Stable promotion check
GitHub protection must require at least one stable promotion status check for `main`. For UAOS the stable check context is `promotion-gate`; it runs the repository contract/architecture suite on the candidate PR commit.

Additional expensive live verification is selected by the assurance/risk policy and may remain separate, but a change that requires such live evidence must not be semantically reported as ready merely because `promotion-gate` passed. The ruleset is the physical production write barrier; assurance still determines which evidence is sufficient for promotion.

## V16-07 — Host enforcement is assurance evidence
Production readiness must separately report:
- logical/cognitive admission status;
- repository/host enforcement status;
- actual remote protection evidence (for example active GitHub ruleset identity and required promotion check);
- any remaining bypass identity or path.

A local configuration declaring intended protection is not evidence that GitHub or another host actually enforces it.

## V16-08 — Reference-monitor fitness
The production mutation boundary should satisfy the reference-monitor properties relevant to this system:
- complete mediation: every protected production mutation is checked;
- tamper resistance: the governed writer cannot silently disable or bypass the enforcement point as part of the same ordinary write path;
- verifiability: the enforcement mechanism and its tests/rules are small and inspectable enough to audit.

This borrows the security property, not an operating-system implementation.

## V16-09 — Host permission is part of the control surface
ChatGPT connector permissions and GitHub repository rules are part of the actual execution control surface and must be inspected when diagnosing write-governance failures.

A connector permission such as unrestricted write access may be operationally convenient but cannot be ignored when evaluating whether mutation admission is physically enforceable.

## Authority composition
Current requirements authority = `FROZEN_REQUIREMENTS_v1.0.md` + `FROZEN_REQUIREMENTS_v1.1.md` + `FROZEN_REQUIREMENTS_v1.2.md` + `FROZEN_REQUIREMENTS_v1.3.md` + `FROZEN_REQUIREMENTS_v1.4.md` + `FROZEN_REQUIREMENTS_v1.5.md` + this v1.6 delta.
