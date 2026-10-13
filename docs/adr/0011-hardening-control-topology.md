# ADR-024 — Phase 11 Control Hardening and Readiness Boundary

Status: ACCEPTED
Date: 2026-10-14

## Decision

Phase 11 closes remaining deterministic control-plane gaps before live integration. Bare `CONTINUE` resolves only to an explicitly unique resumable task and fails closed on ambiguity; new-task and system-maintenance intents never silently inherit business state. Effective requirements are derived from explicit scope and supersession rather than prompt order.

Subsystem topology is first-class authority: owner, root location, parent/dependencies, rule/state/knowledge/workflow/validation references, authority bindings and retirement constraints are inspectable. A subsystem cannot be retired while active dependents or authority bindings remain.

Runtime version skew is classified `DIRECT`, `MIGRATE` or `BLOCK`; unknown state versions are never silently reinterpreted. Retry policy treats `UNKNOWN` external effects as reconciliation work, caps retries, and requires idempotency/deduplication evidence for side effects.

Scheduling is priority-aware and resource-conflict-aware. Context packets are budgeted so specialists receive minimum-sufficient state instead of global history. A selected multi-fault test combines primary-provider outage with ambiguous fallback outcome and must stop at reconciliation.

The 20 frozen acceptance scenarios now have a machine-readable local coverage ledger. This is not production certification. Production readiness remains blocked until hosted CI, live PostgreSQL/DBOS, real executor/provider/action flows, artifact delivery, four domain E2Es, background maintenance and controlled promotion/rollback drills have live evidence.
