# ADR-015 — Durable Runtime Boundary and DBOS Adapter

Status: ACCEPTED
Date: 2026-10-14

## Decision

Universal Agent OS owns a framework-independent `DurableRuntime` contract. DBOS is the baseline adapter, not the task-state authority and not a type that may leak through kernel/domain APIs.

## Verified DBOS capabilities used by the adapter

The current DBOS Python public API provides:
- durable `start_workflow` handles;
- globally unique workflow IDs via `SetWorkflowID`, with return-existing behavior by default;
- `retrieve_workflow`;
- `cancel_workflow` and `resume_workflow` from the last completed step;
- persisted workflow messages with optional topic and idempotency key;
- workflow events retrievable by workflow ID.

The adapter uses only this public surface. Workflow status values are mapped conservatively: unknown/new provider statuses become UAOS `UNKNOWN` instead of being guessed.

## UAOS-specific semantics

- UAOS task identity remains separate from runtime workflow identity, although normally bound one-to-one for a task execution generation.
- Requirement updates, pause/cancel requests and approvals are typed control messages.
- Messages sent from non-workflow callers require idempotency keys for important commands.
- DBOS events are observation/coordination data; authoritative task state remains in the UAOS state plane.
- Runtime/version migration cannot silently reinterpret old task/checkpoint semantics.

## Why not expose DBOS directly

Frozen requirements F08, D12 and X07 require compatibility and migration to remain explicit. Keeping DBOS behind a port preserves the ability to replace or migrate the durable engine without changing Task/Action/Artifact identities.

## Deferred

Queue registration, scheduling, application-version attributes and a live Postgres/DBOS integration test land after the core state and execution adapters are wired together. The current in-memory runtime is only a reference semantics implementation and must never be described as crash durable.
