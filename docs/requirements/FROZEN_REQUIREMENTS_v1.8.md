# Clean-Slate v8 — 冻结需求规格 v1.8

Status: `FROZEN_BASELINE_V1_8 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-14
Updated-at: 2026-10-14T16:30:00Z

v1.8 incorporates v1.0 through v1.7 and corrects an overconstraint introduced by v1.6. The user goal is autonomous maintenance: the Agent should diagnose, research, reflect, modify, verify, promote and report without requiring per-write user approval. Repository rulesets/branch protection remain valuable defense-in-depth, but they are not a universal prerequisite for normal Agent operation or release promotion unless a non-bypassable physical-enforcement guarantee is explicitly required.

## V18-01 — Autonomous maintenance baseline
For a material repository/system change, the normal baseline is:
1. detect/define the problem or requested change;
2. when a problem exists, satisfy the v1.7 research-and-reflection floor;
3. work on a candidate branch or equivalent isolated candidate state;
4. run owner-appropriate reproducible validation;
5. evaluate the candidate against current authority and known counterexamples/risk;
6. promote through a controlled repository update/merge path;
7. reread production authority and perform post-promotion observation;
8. report what changed, why, evidence, and remaining limitations to the user.

The user does not need to approve each ordinary GitHub write when the connected app permission allows autonomous action.

## V18-02 — Host hardening is defense-in-depth by default
GitHub rulesets, protected branches, mandatory reviews, and equivalent non-bypassable repository controls are optional defense-in-depth for the default UAOS operating objective.

Their absence does not by itself:
- make a registered Agent unusable;
- block an otherwise verified release;
- create parent-core open work;
- force per-write human confirmation;
- prevent an evolution incident from closing when the claimed invariant does not require physical non-bypassability.

The system may recommend or add these controls when risk, repository criticality, collaboration model, or an explicit user requirement justifies the extra complexity.

## V18-03 — Physical complete mediation is an assurance tier, not the baseline
If UAOS explicitly claims `PHYSICAL_COMPLETE_MEDIATION`, `NON_BYPASSABLE_PRODUCTION_ENFORCEMENT`, or an equivalent hard guarantee, then active remote enforcement evidence is mandatory and v1.6 complete-mediation requirements apply to that claim.

Without such a claim, UAOS must state the actual assurance ceiling accurately rather than treating the missing hard guarantee as a blocker.

## V18-04 — Candidate/PR discipline remains the normal material-change workflow
Material GitHub maintenance should normally use:
`candidate branch -> pull request -> owner-appropriate checks -> controlled merge/update -> production reread`.

This workflow provides isolation, auditability and reproducible evidence even when GitHub does not mechanically enforce it with a ruleset. Direct production writes are not the normal path for material architecture/governance changes, but this is a process invariant rather than a claim that the platform physically forbids such writes.

## V18-05 — CAS and host controls have distinct roles
CAS/stale-head checks protect concurrency integrity. Candidate isolation and CI protect change quality. Authority/deliberation policies protect semantic ownership and decision quality. Rulesets/protected branches optionally add host-level non-bypassability.

Do not conflate these layers, and do not require the strongest layer when the governing user objective is already satisfied by a simpler sufficient architecture.

## V18-06 — Anti-bloat / proportional assurance
Before adding a stronger control, ask:
- what user/system objective requires it;
- which concrete failure mode it mitigates;
- whether existing controls already reduce that risk sufficiently;
- what operational friction/complexity it adds;
- whether the stronger assurance is explicitly required or merely possible.

`Stronger` is not automatically `required`.

## V18-07 — GitHub permission preference
For the current user, the GitHub connector may remain in autonomous/full-access mode. The Agent is expected to self-check and report actions rather than request approval for each write. Account login, payment, identity verification, or other actions that inherently require the user remain user-mediated.

## Authority composition
Current requirements authority = v1.0 + v1.1 + v1.2 + v1.3 + v1.4 + v1.5 + v1.6 + v1.7 + this v1.8 delta. Where v1.6 made physical complete mediation a universal baseline blocker, v1.8 narrows that requirement to explicit hard-enforcement assurance claims.