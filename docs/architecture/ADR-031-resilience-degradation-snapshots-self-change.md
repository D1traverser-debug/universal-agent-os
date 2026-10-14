# ADR-031 — Graceful Degradation, Portable Authority and Risk-Tier Self-Change

Status: ACCEPTED
Date: 2026-10-14

## Decision

UAOS keeps the zero-cost local-first baseline and hardens it instead of introducing mandatory cloud infrastructure.

1. Missing semantic/tool capability is not automatically a permanent task failure. Required work enters `WAITING_CAPABILITY`; background-only work without a host enters `PAUSED_NO_HOST`; exact approval gates enter `WAITING_APPROVAL`; unknown side effects enter recovery. `BLOCKED` is reserved for non-recoverable contract/invariant failures.
2. Side-effect-free work may fail over across currently eligible INCLUDED/FREE capabilities. Repeated provider/plugin failures are circuit-broken so UAOS does not hammer a dependency that is already failing. UNKNOWN never triggers blind failover.
3. WorkUnits may declare REQUIRED, PREFERRED or OPTIONAL capability dependence. PREFERRED may use an explicit verified fallback; OPTIONAL may be skipped only when it produces no downstream-required output.
4. SQLite remains the single-machine authority. Portability is provided with SQLite's backup API plus a content-hashed artifact snapshot, not by synchronizing a live WAL database through a network/sync folder.
5. When no always-on host exists, maintenance is opportunistic: recovery and due maintenance are evaluated on invocation, but foreground user work is not preempted unless recovery safety requires it.
6. Self-change is risk-tiered. Low-risk reversible changes can auto-apply after evaluation. Medium-risk changes stay in candidate/sandbox until evaluation, canary and rollback evidence pass. High-risk changes require explicit approval. A system change that attempts to widen the system's own authority is denied rather than self-approved.

## Comparison

Rejected alternatives:
- "No capability => whole task BLOCKED": loses valid completed work and makes transient plugin outages look permanent.
- Unlimited retry: amplifies outages and may duplicate effects.
- Live SQLite sync across machines: conflicts with WAL/single-writer characteristics and risks corruption/split authority.
- "Every self-change needs user approval": safe but defeats low-risk autonomous maintenance.
- "Self-change can approve its own permission expansion": circular authority escalation.

Optional PostgreSQL/DBOS/S3/hosted CI adapters remain available for scale or stronger guarantees, but are not required for normal use.
