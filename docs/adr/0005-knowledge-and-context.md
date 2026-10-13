# ADR-018 — Source-Bound Knowledge, Progress Cursors and Context Compaction

Status: ACCEPTED
Date: 2026-10-14

## Decision

UAOS does not have one undifferentiated “memory”. Source snapshots, task evidence, candidate knowledge, canonical knowledge, progress cursors and compacted context are different object types with different lifecycles.

Canonical knowledge uses the existing shared knowledge state machine:
`RAW_EVIDENCE -> CANDIDATE -> EVALUATED -> CANONICAL -> RETIRED`.
A CANONICAL transition additionally requires a validated usage/evaluation link.

Long-document progress cursors bind to both source identity and content hash. A changed source cannot silently reuse the old cursor.

Compaction is a versioned artifact. It must retain all pending obligations, active approval IDs, material tool/result pairings and required provenance references before it can replace a larger context representation.

## Why

This enforces frozen C05–C09, F03/F10, G03/G04/G09 and scenarios S7/S17 without relying on prompt discipline.

A vector index, when later introduced, is only a retrieval mechanism. It does not change knowledge lifecycle state or proof level.
