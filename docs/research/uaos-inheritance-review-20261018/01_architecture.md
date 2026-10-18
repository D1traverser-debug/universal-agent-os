# A1 — Architecture governance study (independent lens)
Status: EVIDENCE_ONLY; not an architecture policy owner.

## Primary evidence
- CMU SEI ATAM: https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/ . Its nine-stage evaluation grounds business drivers, architectural approaches, utility tree, quality scenarios, sensitivity/tradeoff/risk points, expanded stakeholder scenarios and results.
- Continuous fitness functions: https://martinfowler.com/articles/fitness-functions-data-products.html . Automated tests of architectural qualities help detect drift continuously rather than only by inspection.

## Independently extracted methods
A. Scenario-first architecture challenge: goals -> quality attributes (correctness, independent evidence, recoverability, completeness, operability, change cost) -> observable stimulus/response scenarios -> competing architecture patterns -> tradeoff and risk themes.
B. Architecture fitness tests: static dependency/authority invariants + runtime scenario checks at actual critical paths. Both necessary; neither is a substitute for the other.
C. Incremental review may cover evolving high-risk seams continually, yet an explicit full-scope inventory is still needed to prevent silent blind spots.

## Challenge against current UAOS
Current UAOS has ArchitectureExperienceCase for *material proposed changes* and a five-stage cognition kernel for *detected problems*. Neither necessarily fires a periodic review on selecting the parent controller with no active problem. Prior inherited selector mostly resolves tasks.
Competing designs: (1) require full source files every time (large, untestable completion and many duplicate reads); (2) only on detected incident (misses latent failures); (3) mandatory five-repo coverage ledger with scenario-based depth per control dimension and risk-triggered expansion. Select 3 for a falsifiable, repeatable baseline, retain one full audit request as a forcing signal.
Counterexample: a green architecture static test while native tool call bypasses finalization; a successful child CI while business adapter is disabled.
Adoption: existing SESSION_INTERACTION_POLICY entry and existing architecture experience / cognition and evolution owners; no new planning authority.
Boundaries: ATAM typically uses stakeholders and trained evaluators; this solo Agent review is an ATAM-inspired quality-scenario application, not certified ATAM or independent stakeholder validation.
