# UAOS Zero-Cost Usable Baseline

Status: COMPLETE
Date: 2026-10-14

The core system is considered usable without paid infrastructure when all of the following are true:

- frozen requirements v1.0 + zero-cost delta v1.1 are authoritative;
- SQLite provides durable state, CAS and append-only evidence;
- SQLiteCheckpointRuntime provides cross-process checkpoint/resume semantics;
- local content-addressed storage provides artifact identity;
- session/local host capabilities can be registered dynamically, with paid and unknown-cost capabilities blocked by default;
- representative financial-writing, novel, video and A-share workflows execute through the same zero-cost control loop, including runtime fan-out/fan-in;
- the legacy system is selectively cut over without importing obsolete control machinery;
- self-change promotion and rollback are proven against a real isolated file mutation with exact approval and hash-CAS.

## Intentional guarantee reductions

A zero-cost baseline does not claim multi-node HA, arbitrary Python call-stack replay, remote object availability, or autonomous execution while no host/process exists. If no background capability is available, maintenance runs opportunistically when UAOS is next invoked. If a semantic executor (model/plugin/search source) is absent, the affected WorkUnit is BLOCKED rather than silently downgraded.

PostgreSQL, DBOS, remote S3, commercial model APIs and hosted CI remain optional enhancements, not completion blockers.
