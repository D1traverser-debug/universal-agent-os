# Clean-Slate v4 — 冻结需求规格 v1.4

Status: `FROZEN_BASELINE_V1_4 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-14
Updated-at: 2026-10-14T09:43:41Z

v1.4 incorporates v1.0 + v1.1 + v1.2 + v1.3 except where this delta explicitly supersedes a narrower clause. It adds hierarchical parent governance, in-place child-to-parent guidance calls, prevention-first strategic alignment and adaptive deliberation/evidence escalation.

## V14-01 — Authority is hierarchical, not peer-isolated
UAOS is the parent governance authority for registered domain Agents. A domain remains the business-method/state owner for normal execution, but the parent may govern and authoritatively modify a registered descendant when the mutation has explicit governance lineage, current domain binding/authority has been read, impact is understood, and normal action/approval/CAS/verification rules are satisfied.

- `UAOS -> UAOS`: allowed under normal controls.
- `DOMAIN:X -> DOMAIN:X`: allowed under normal domain-owner controls.
- `UAOS -> registered DOMAIN:X`: allowed for explicit parent-governed change with a recorded governance basis and domain-aware impact/verification.
- `DOMAIN:X -> UAOS`: direct authoritative mutation remains prohibited.
- `DOMAIN:X -> DOMAIN:Y`: direct authoritative mutation remains prohibited.

This supersedes only the v1.3 statement that all `UAOS -> DOMAIN:X` direct mutations are prohibited. It does not permit blind parent writes or removal of domain-specific validation.

## V14-02 — Child Agents may call the parent without surrendering task ownership
A selected child/domain Agent may issue a parent upcall at any time when it needs system-level diagnosis, goal clarification, scope arbitration, replanning, external architecture/method research, cross-domain impact analysis, assurance escalation or evolution guidance.

The upcall:
- does not by itself change the child task's selected authority context;
- carries the current problem, evidence, hypothesis/unknowns and requested outcome;
- returns parent guidance, constraints, plan changes and required evidence;
- allows the child to resume its task unless the parent deliberately changes lifecycle/plan authority.

A parent upcall is not permission for the child to mutate parent authority.

## V14-03 — Prevention-first strategic alignment precedes patch accumulation
Before a material repair, architecture change, repeated retry or scope expansion, UAOS must determine whether the observed symptom is a local execution defect, a repeated failure class, a goal-alignment problem, a control/interaction problem, an assumption/model problem, a knowledge/method gap or a verification gap.

For delegated work, the parent must make available enough typed governance context to preserve the main track: parent/system goal, local-goal linkage, non-goals, invariants, autonomy bounds, escalation conditions, stop conditions and verification expectations. These are control dimensions, not a fixed questionnaire.

## V14-04 — Deliberation is event/risk-triggered and dynamically framed
UAOS must not rely on a fixed list of self-questions as the complete entrance to reasoning. Trigger conditions determine when deeper deliberation is required; the actual questions, hypotheses, methods and evidence requests are generated from current state, symptoms, topology, requirements and unknowns.

Representative triggers include user correction, repeated failure, uncertain progress toward done-condition, scope expansion, cross-subsystem impact, complexity growth, conflicting evidence, an unknown failure class, a knowledge/method gap, architecture gap or high-risk change. The trigger set is extensible and is not an exhaustive ontology of possible problems.

## V14-05 — External method/architecture research is an escalation path, not a default ritual
When UAOS cannot adequately frame or solve a problem from current evidence/methods, or detects an architecture/method knowledge gap, it must actively search appropriate external evidence rather than remaining limited to its first internally generated framing.

External patterns are treated as candidates. UAOS must extract the property/mechanism relevant to the current problem, compare fit, costs and failure modes, and borrow the minimum useful mechanism. Architecture names or popularity never become authority by themselves.

## V14-06 — Self-dialogue is candidate generation, not independent proof
Same-model self-critique, self-refinement or multi-instance debate may be used adaptively when useful, but they are not automatically independent verification. Evidence strength must be escalated according to uncertainty/risk:
- deterministic or external feedback where available;
- counterexample search for material proposals;
- independent review/provider/tool evidence for high-risk or disputed claims when genuinely available;
- explicit assurance ceilings when independence is unavailable.

Do not run debate/reflection loops merely to create the appearance of rigor.

## V14-07 — Micro and macro reasoning form a closed loop
UAOS must be able to move from micro evidence to macro structure and back:
`observe concrete symptom -> diagnose local mechanism -> test whether governing goal/assumption/topology is wrong -> select the smallest correct abstraction to change -> verify concrete behavior and strategic alignment`.

Repeated local repairs without examining governing assumptions are not acceptable closure. Conversely, abstract architecture research without reproducing the concrete failure is not acceptable diagnosis.

## V14-08 — Architecture fitness and anti-bloat are continuous properties
Important architecture characteristics must be expressible as checkable fitness properties where practical, including single-controller authority, hierarchy direction, goal linkage, no duplicate control planes, candidate/production separation, complexity budgets, evidence/verification requirements and retirement of superseded mechanisms.

A new mechanism must identify the existing owner/overlap and what it replaces, retires or why no existing mechanism can be extended. Adding rules, reviewers, fallbacks or guarantee text without this analysis is not a valid repair strategy.

## V14-09 — Assurance authority must track current requirements
Production/readiness and validation snapshots must state the full current effective requirements authority. A snapshot that predates v1.2/v1.3/v1.4 cannot be presented as certification of those later requirements; targeted evidence may be recorded separately with its assurance ceiling.

## Authority composition
Current requirements authority = `FROZEN_REQUIREMENTS_v1.0.md` + `FROZEN_REQUIREMENTS_v1.1.md` + `FROZEN_REQUIREMENTS_v1.2.md` + `FROZEN_REQUIREMENTS_v1.3.md` + this v1.4 delta, with V14-01 superseding only the narrower parent-to-child prohibition described above.
