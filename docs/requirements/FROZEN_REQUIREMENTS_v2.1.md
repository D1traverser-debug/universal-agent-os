# Clean-Slate v10 — Frozen Requirements Delta v2.1

Status: `FROZEN_BASELINE_V2_1 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-15

v2.1 extends v1.0-v2.0 with explicit operational inheritance assurance, proactive domain-health discovery and bulkheaded parent-guidance escalation.

## V21-01 — Inheritance is operational, not declarative
A registered domain may claim an inherited UAOS capability as operational only when current owner-appropriate execution evidence exists for the behavior being claimed. A pointer, manifest declaration or copied policy text is insufficient by itself.

When evidence is absent, stale or contradictory, the affected inherited behavior is `DECLARED_ONLY` or `UNVERIFIED`; only the affected hard prerequisite is blocked.

## V21-02 — Parent observations are caches, never child authority
Any UAOS record of a child version, profile, commit, release or health state is an observation/cache. Current child authority is resolved from the registered child repository and current binding/business authority.

A parent observation that differs from current child authority is a health finding, not proof that the child regressed. Regression tests must not freeze an old child release and label that historical snapshot as current.

## V21-03 — Proactive health discovery is required
UAOS must be able to detect relevant control-plane/domain-health problems without waiting for user correction or a child upcall. Proactive discovery must cover, when applicable:
- child-authority freshness and parent-observation drift;
- inherited-behavior evidence gaps;
- binding/authority contradictions;
- unresolved material child evolution or parent-guidance items;
- scenario, recovery and failure-injection probes for material control-plane changes;
- repeat or cross-domain failure-class clustering.

Proactive discovery supplements live observation; it does not imply that all future failures are statically knowable.

## V21-04 — Child problem upcalls are structured and diagnosable
A material child upcall to UAOS must identify enough evidence for the parent to determine what failed and where. The logical envelope includes:
- child/domain identity and current revision;
- problem/evolution reference;
- severity and user/business impact;
- blast radius / blocking scope;
- suspected layer (`DOMAIN_BUSINESS`, `DOMAIN_ARCHITECTURE`, `COMMON_CAPABILITY`, `HOST`, or `UNKNOWN`);
- evidence references and local recovery attempts;
- requested parent help;
- whether unaffected child work may continue.

The child keeps its business identity/state while requesting parent guidance.

## V21-05 — Parent guidance is bulkheaded, not one global blocking queue
Multiple child upcalls may coexist. UAOS must prioritize by impact, blast radius, urgency and cross-domain commonality, while allowing non-conflicting diagnosis/repair work to proceed concurrently.

One blocked child issue must not block unrelated domains or unaffected child work. Work serializes only when a real shared resource, shared authority, common invariant or causal dependency requires it.

## V21-06 — Cross-domain repetition promotes diagnosis scope, not automatic global failure
When multiple domains exhibit the same credible failure class or common-capability symptom, UAOS should cluster the evidence and evaluate the common abstraction. A suspected common cause does not globally block all domains until evidence establishes a hard shared dependency or unsafe common invariant.

## V21-07 — “Done” claims expose assurance boundaries
A system/subsystem repair or architecture-management claim must distinguish:
- what was structurally verified;
- what was behaviorally/replay/scenario verified;
- what was observed in current production/live use;
- what remains unverified, under observation or dependent on future live evidence.

Green CI or document completeness alone must not be reported as proof that every operational behavior is solved.

## V21-08 — External Skills are candidate methods, not authority
External Skill catalogs such as SkillsMP may be used as discovery sources for reusable workflows and architecture patterns. Before adoption:
1. inspect source/provenance and companion files;
2. map the Skill to a concrete observed need/failure class;
3. identify authority/security/tool implications;
4. evaluate it in a bounded sandbox, scenario, replay or regression appropriate to the claim;
5. promote only the minimum useful mechanism at the correct owner scope.

Catalog popularity, stars, indexing or publication do not constitute quality/safety certification or authority.

## Authority composition
Current requirements authority = v1.0 + v1.1 + v1.2 + v1.3 + v1.4 + v1.5 + v1.6 + v1.7 + v1.8 + v1.9 + v2.0 + this v2.1 delta.
