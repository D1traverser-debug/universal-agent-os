# Clean-Slate v10 — Frozen Requirements Delta v2.2

Status: `FROZEN_BASELINE_V2_2 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-16

v2.2 extends v1.0-v2.1 with an evidence-gated problem cognition -> evolution -> action transaction. It is motivated by repeated UAOS failures where a user correction or newly discovered local defect was accepted as the active problem frame and moved directly toward repair before the system had proved the correct problem layer.

## V22-01 — A repairable symptom is not an admitted root cause
A detected problem must not enter repair/no-change merely because an edit is available, authorized, familiar, suggested by the user, or supported by an external method. The current problem layer/root hypothesis must first be evidence-tested and admitted.

## V22-02 — User and external authority are evidence, not automatic root-cause authority
A user correction, user theory, external Skill, SRE/debugging method, architecture pattern, popular repository or prior UAOS mechanism may seed hypotheses and evaluation criteria. None may be promoted directly to the selected root cause without current evidence/falsification appropriate to the claim.

## V22-03 — Systemic signals force cross-layer hypothesis comparison
When a problem is repeated, cross-subsystem, architecture-gap, complexity-growth or scope-expansion shaped, root-scope admission requires:
- at least two credible hypotheses;
- hypotheses spanning at least two problem layers;
- at least one architecture/upstream hypothesis (`DOMAIN_ARCHITECTURE`, `COMMON_CAPABILITY`, `CONTROL_PLANE`, `HOST`, or `REQUIREMENT_OR_GOAL`);
- evidence rejecting at least one alternative;
- explicit architecture/upstream reassessment evidence even if the selected root cause is ultimately local.

This requirement prevents both architecture blindness and architecture overreaction.

## V22-04 — Root-scope admission precedes evolution and action
The common transaction is:

`Detect -> Record when material/evolution-relevant -> Deliberation -> Competing hypotheses/falsification -> Root-scope admission -> Evolution disposition -> Repair/Redesign/No-change -> Verification -> Observation`

The transaction may be compact for small local defects, but its ordering may not be reversed. A successful repair attempted before root-scope admission is process-failure evidence; success does not retroactively prove the original diagnosis was justified.

## V22-05 — Every admitted problem receives a learning/evolution disposition
Before repair/no-change, determine whether the problem is:
- a small one-off with `NO_DURABLE_EVOLUTION`;
- evidence attached to an existing failure class;
- a new durable incident/failure-class candidate;
- a material architecture/governance evolution candidate.

Material or evolution-relevant problems require durable causal evidence. The system must not silently drop the problem because a repair was found.

## V22-06 — Problem recording preserves root-scope evidence
For material/evolution-relevant problems, durable evidence must preserve enough information to reconstruct why the selected problem layer was chosen: symptom, competing hypotheses, falsification/rejection evidence, selected root scope, material failed/rejected paths, selected action, verification and remaining unknowns/observation conditions.

UAOS standardizes these semantics, not one universal child journal format.

## V22-07 — Architecture redesign is evidence-triggered, not reflexive
Neither repeated local patching nor a user request to “怀疑架构” automatically proves a whole-system redesign is warranted. Architecture redesign is selected when root-scope evidence shows the existing abstraction/topology repeatedly causes or cannot contain the failure class, or when quality attributes/scenario evaluation fail at that layer. Otherwise repair the narrowest justified owner abstraction.

## V22-08 — External method discovery is comparative
External Skill catalogs such as SkillsMP are method candidate pools. For material governance/architecture adoption, compare multiple relevant method families and extract the smallest useful mechanisms. Do not treat popularity, reputation, a single search result, or one external framework as sufficient architecture selection evidence.

## Authority composition
Current requirements authority = v1.0 + v1.1 + v1.2 + v1.3 + v1.4 + v1.5 + v1.6 + v1.7 + v1.8 + v1.9 + v2.0 + v2.1 + this v2.2 delta.
