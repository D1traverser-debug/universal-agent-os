# Architecture Decision Records — Initial Set

## ADR-001 Modular monolith first
Decision: one repository, one logical application, multiple worker processes if needed.
Reason: maximizes atomic refactoring and shared invariants while minimizing distributed failure modes. Split services only when independent deployment, security or scale is measured.

## ADR-002 PostgreSQL is the authoritative runtime state store
Decision: typed relational state plus append-only execution/action ledger.
Reason: transactions, constraints, versioning and queries fit task/requirements/lineage needs. Avoid a new database per concern.

## ADR-003 DBOS is the baseline durable runtime
Decision: use DBOS behind an internal DurableRuntime port.
Reason: durable resume, steps, queues/concurrency, schedules, workflow communication and versioning are available with Postgres and no mandatory separate orchestration server.
Constraint: DBOS Conductor is not required in baseline. HA/operability needs may later trigger a Temporal comparison/migration.

## ADR-004 OpenAI Agents SDK is an executor, not the control plane
Decision: use OpenAI Agents SDK for Agent loops, tools, guardrails, HITL and sandboxed workspaces via an adapter.
Reason: strong Agent execution features without surrendering durable task truth to a model/session.

## ADR-005 No LangGraph in the baseline
Decision: do not add LangGraph to core.
Reason: its checkpoint/store/graph responsibilities would overlap the chosen durable runtime and authoritative state plane. A domain may adopt it behind an executor adapter only if a concrete scenario justifies it.

## ADR-006 Git is source/config authority, not live task state
Decision: no task progress, writer lease, or current artifact truth depends on Git commits.
Reason: removes chat/Git mutation coupling and makes runtime recovery transactional.

## ADR-007 Event-sourcing-lite, not full event sourcing
Decision: keep normalized current state plus immutable execution/action/evidence events.
Reason: preserves auditability without requiring every current view to be rebuilt from events.

## ADR-008 Single object store interface for large artifacts
Decision: filesystem in development; S3-compatible in production.
Reason: stable artifact IDs/hashes stay independent of storage provider.

## ADR-009 pgvector only inside PostgreSQL and only when justified
Decision: no separate vector DB at baseline.
Reason: reduce infrastructure and keep metadata/provenance near retrieval. Vector similarity is retrieval assistance, not authority.

## ADR-010 Deterministic orchestration owns global task responsibility
Decision: specialists are bounded executors/tools by default. Free handoff is exceptional.
Reason: prevents loss of task ownership, context explosion and “agents chatting without completing”.

## ADR-011 Every side effect uses an Action contract
Decision: PREPARED/SENT/CONFIRMED/UNKNOWN/COMPENSATED state machine, request hash and idempotency/reconciliation policy.
Reason: solves retries and ambiguous external outcomes uniformly.

## ADR-012 User requirements are typed state, not prompt appendices
Decision: requirement lifecycle/scope/precedence stored in authority and compiled into scoped context.
Reason: new/old requirements can supersede cleanly without endless prompt growth.

## ADR-013 Candidate learning is isolated from production knowledge
Decision: promotion requires evidence/eval and an atomic alias/state transition.
Reason: prevents one failure, one book or one market day from mutating global methodology.

## ADR-014 High-impact self-evolution requires a change lifecycle
Decision: no direct “maintenance agent edits production” path.
Reason: autonomous maintenance remains useful but bounded, testable and reversible.
