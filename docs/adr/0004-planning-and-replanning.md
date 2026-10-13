# ADR-017 — DAG Reachability and Impact-Scoped Replanning

Status: ACCEPTED
Date: 2026-10-14

## Decision

A valid plan must prove more than the existence of a producer. If a WorkUnit consumes an artifact produced inside the plan, that producer must be a transitive upstream dependency of the consumer. External inputs and internally produced outputs may not share the same name because their authority would be ambiguous.

The kernel exposes deterministic topological order and execution layers. WorkUnits in the same layer are candidates for parallel execution subject to resource/concurrency policy.

When a requirement, artifact contract or user goal changes, replanning invalidates the identified roots and their transitive downstream dependents. Successful upstream WorkUnits whose contracts are unchanged remain reusable.

## Why

This directly enforces frozen D02/D07/D09 and scenario S19:
- no static producer→artifact→consumer dead links;
- safe parallelism is visible rather than improvised by Agents;
- a mid-task user change does not force a full restart;
- stale downstream results cannot silently survive a changed upstream contract.

## Boundaries

Determining which root WorkUnits are affected by a semantic requirement change is a separate impact-analysis responsibility. Once roots are identified, downstream invalidation is deterministic and mechanical.
