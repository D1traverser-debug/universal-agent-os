# ADR-019 — Requirement-Driven Completion and Delivery Proof

Status: ACCEPTED
Date: 2026-10-14

## Decision

UAOS has a completion gate independent from Agent self-reporting. Every required user requirement must have a PASS check with concrete evidence at or above the task's minimum assurance level.

Evidence levels are ordered:
1. declaration;
2. structural;
3. deterministic execution;
4. semantic evaluation;
5. independent/heterogeneous confirmation;
6. observed live outcome.

A claim cannot exceed the evidence that actually exists.

Actual deliverables are part of assurance. Artifact ID, version, hash and accessibility must match the expected delivery. A historical path/hash or a task record saying “file exists” is insufficient.

Unresolved UNKNOWN side effects block completion.

When independent review is required, independence must be demonstrated by an actual separation axis and a distinct reviewer identity; reviewer count or labels do not prove independence.

Coverage is reported by capability, failure class and invariant rather than by raw test count.

## Requirements

Implements J01–J09, G08, H04/H09 and X09/X10/X15.
