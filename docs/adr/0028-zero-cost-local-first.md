# ADR-028 — Zero-Cost Local-First Baseline

Status: ACCEPTED
Date: 2026-10-14

## Decision

UAOS changes its default deployment baseline from PostgreSQL + DBOS + remote object storage + provider API assumptions to a zero-cost local-first stack:

- SQLite (Python stdlib) for authoritative versioned state, CAS and append-only ledger;
- SQLite checkpoint runtime for workflow identity, lifecycle, messages and events across process restarts;
- local content-addressed filesystem store for artifacts;
- host-provided/currently available Agent/model/tool executors through the existing execution interfaces;
- local pytest/manual verification as the minimum test path.

PostgreSQL, DBOS, S3-compatible remote storage, OpenAI Agents SDK/API and hosted GitHub Actions remain optional adapters and scaling/guarantee upgrades. They are not prerequisites for a usable system.

## Consequences

The zero-cost baseline preserves the main user-facing requirements: task authority, requirement lifecycle, cross-chat checkpoint/resume, work-unit planning, Agent/tool routing, idempotent control messages, artifact identity, knowledge governance, verification and delivery.

It intentionally provides weaker guarantees in several areas: no transparent Python call-stack replay, no multi-node HA, lower write concurrency, local-only artifact availability, and no autonomous between-session background work unless a free/available scheduler exists.

Those are guarantee-level reductions, not core-function failures. Always-on background maintenance degrades to opportunistic maintenance when the system is next invoked.
