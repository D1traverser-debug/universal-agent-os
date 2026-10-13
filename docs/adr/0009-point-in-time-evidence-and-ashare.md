# ADR-022 — Point-in-Time Evidence and A-Share Pilot

Status: ACCEPTED
Date: 2026-10-14

## Decision

`SourceSnapshot` is strengthened as the shared point-in-time evidence contract rather than creating an A-share-only frozen-data type. In addition to source identity, content hash and observation time, a snapshot can record the latest knowledge-availability time admitted from the source, an explicit completeness class, gaps and source metadata.

A snapshot used for a frozen decision must prove that its admitted content was knowable no later than the freeze boundary. Retrieval may happen later; later retrieval never authorizes later information. `FULL` is explicit and cannot coexist with declared gaps.

The PostgreSQL authority persists these fields in `uaos_source_snapshot`, making point-in-time evidence reconstructable without chat or Git.

The A-share pilot uses two separate workflows. Premarket freezes evidence, checks completeness, builds recall before ranking, expands candidate tickers into first-class work units and produces an immutable frozen decision (or a valid NO_TRADE). Post-close review is a separate task bound to that frozen decision; later outcomes cannot rewrite premarket evidence. A single day can only produce a learning candidate, never canonical strategy knowledge.

This design implements the same generic evidence semantics needed by financial research, backtests, experiments, compliance reviews and any task where late-arriving information could contaminate a frozen decision.
