# ADR-030 — Selective Legacy Cutover and Governed Local Self-Change

Status: ACCEPTED
Date: 2026-10-14

## Legacy cutover

The old continuity repository is not migrated as a runtime. UAOS imports only explicitly selected semantic records: durable requirements, task disposition/meaning, knowledge and evidence. Each imported record retains its source reference and is written to the zero-cost SQLite authority with an append-only migration event.

Writer leases, resume epochs, maintenance-controller state, monitor state, owner guards, cache/mirror state, exact-text test coupling, stale branch state and duplicated prompt/policy machinery are not migratable record types. The importer fails closed on any unrecognized control type. Replaying the same migration bundle is idempotent; conflicting content under an existing record ID is rejected.

## Self-change drill

A self-evolving system must prove rollback with a real mutation, not only a state transition. The zero-cost drill therefore creates an isolated local workspace, evaluates a candidate, requires exact-action approval, atomically changes a real file under hash-CAS, marks the proposal PROMOTED, injects a regression observation, requires ROLLBACK, restores the exact baseline hash, and retires the proposal. Every lifecycle step is written to the local SQLite ledger.

The drill does not grant global mutation authority. Normal production changes remain subject to scope, risk, approvals and Action Authority. High-impact external changes are never enabled merely because the drill passes.
