# Clean-Slate v7 — 冻结需求规格 v1.7

Status: `FROZEN_BASELINE_V1_7 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-14
Updated-at: 2026-10-14T16:05:00Z

v1.7 incorporates v1.0 through v1.6 and tightens problem-response cognition. The user requirement is explicit: once a problem is detected, external research and reflective challenge are mandatory, not optional escalations reserved for unfamiliar cases.

## V17-01 — Every detected problem requires research and reflection
A detected problem includes a defect, failed or degraded outcome, user correction, repeated failure, contradiction, uncertain goal progress, increasing repair complexity, conflicting evidence, unknown failure class, knowledge gap, architecture/control-plane gap, or other evidence that current behavior is not reliably satisfying the governing objective.

For every detected problem, before choosing or promoting a repair, UAOS must perform and retain evidence for:
- concrete/micro diagnosis;
- macro goal/topology/architecture alignment;
- governing-assumption challenge;
- external research against relevant authoritative or technically credible sources.

Familiarity with the problem is not a waiver. A small problem may use a lightweight research/reflection pass; a material problem requires deeper evidence. The distinction is depth, not whether research/reflection happens at all.

## V17-02 — Risk adds depth; it does not decide whether research starts
Counterexample search, independent verification, broader architecture comparison, live evidence, or additional assurance remain risk-sensitive escalations.

The base problem-response floor is always research + reflection. Risk signals only add further depth above that floor.

## V17-03 — Research must inform the repair
Research is not ceremonial browsing. The record must identify the relevant fact, method, architecture property, known failure mode, standard, implementation behavior, or counterexample that affected the diagnosis or repair decision. Irrelevant search results do not satisfy admission.

## V17-04 — Reflection is not self-congratulation
Reflection must challenge at least one current assumption, boundary, abstraction, topology, or causal explanation. Repeating the preferred fix in different words does not satisfy the governing-assumption challenge.

## V17-05 — Problem-free work remains lightweight
Normal work with no detected problem does not require ritual external research or architecture reflection. The always-on sentinel still checks for mutation/authority/trigger conditions, but the mandatory problem-response floor activates only when a problem is detected.

## Authority composition
Current requirements authority = `FROZEN_REQUIREMENTS_v1.0.md` + `FROZEN_REQUIREMENTS_v1.1.md` + `FROZEN_REQUIREMENTS_v1.2.md` + `FROZEN_REQUIREMENTS_v1.3.md` + `FROZEN_REQUIREMENTS_v1.4.md` + `FROZEN_REQUIREMENTS_v1.5.md` + `FROZEN_REQUIREMENTS_v1.6.md` + this v1.7 delta.
