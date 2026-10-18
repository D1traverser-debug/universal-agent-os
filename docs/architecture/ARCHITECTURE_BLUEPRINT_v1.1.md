# Clean-Slate v4 Architecture Blueprint v1.1 — Local-First Default

> **Historical local-first architecture delta (v1.1), not a competing current execution policy.** This document extends the historical v1.0 design; use `CURRENT_SYSTEM.json`, `config/SYSTEM_MAP.json`, `config/AUTHORITY_WRITE_POLICY.json` and current owner contracts for present-day effects and writes. Frozen Requirements v1.0/v1.1 retain their independent requirement provenance.

Requirements authority: Frozen Requirements v1.0 + v1.1 Z01–Z05.

This document changes deployment defaults only. The control-kernel, Action, WorkUnit, knowledge, assurance and evolution semantics of Architecture Blueprint v1.0 remain in force.

## Default zero-cost stack

- State authority: SQLite with WAL, transactions, optimistic CAS and append-only ledger.
- Durable continuity: SQLite checkpoint runtime at WorkUnit/checkpoint boundaries.
- Artifacts: local content-addressed filesystem store.
- AI/Agent execution: whatever executor is already available in the host environment through UAOS execution ports; no commercial API is mandatory.
- Verification: local pytest plus explicit runtime evidence.
- Background maintenance: opportunistic on invocation by default; truly always-on scheduling is optional.

## Optional enhancement adapters

- PostgreSQL: higher concurrency, richer operational tooling, multi-process/multi-node deployment.
- DBOS: transparent durable workflow replay, durable schedules/queues and stronger crash recovery semantics.
- S3-compatible remote storage: remote sharing/high availability of large artifacts.
- OpenAI Agents SDK/API: one optional AI executor provider.
- GitHub Actions: hosted CI convenience.

No optional adapter may become a hidden dependency of the core controller.

## Guarantee matrix

Without PostgreSQL: single-machine SQLite remains authoritative; high concurrent writer throughput and multi-node HA are reduced.

Without DBOS: UAOS resumes from durable WorkUnit/checkpoint state instead of replaying arbitrary Python execution frames.

Without remote S3: artifacts remain correct and content-addressed but are local to the machine/workspace.

Without a commercial model API: deterministic controller functions still work; reasoning/generation requires a currently available host/Agent/model executor.

Without a background runner: normal user-triggered work and resume work; between-session autonomous maintenance is unavailable and becomes opportunistic maintenance on the next invocation.
