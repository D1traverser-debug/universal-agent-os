# ADR-019 — ChatGPT Host, Agent Anti-Corruption Layer and Legacy Controller Cutover

Status: ACCEPTED
Date: 2026-10-14

## Decision

UAOS becomes the sole cross-domain control-plane authority. The previous `universal-continuity-agent` is retired read-only. Financial Writing, A-share, Novel and Video repositories remain domain providers rather than being deleted or copied wholesale.

Migration follows Strangler Fig semantics: new tasks route directly to UAOS; unfinished legacy tasks coexist only long enough to be imported; after import, continuity writes go to UAOS only. A small anti-corruption adapter translates old v3.7 task indexes/checkpoints into UAOS task semantics and deliberately drops old controller-only concepts such as universal leases, resume_epoch ownership, progress receipts and maintenance-controller state.

## Host adapters

The user primarily operates from ChatGPT, so local SQLite cannot be the only practical persistence surface.

`CHATGPT_GITHUB` uses repository JSON under `state/` as durable controller state. Material state changes use observed-main HEAD -> one tree/commit -> `expected_sha` ref update -> authoritative reread. The GitHub connector is a host adapter, not a second business workflow.

`LOCAL` uses SQLite and local artifacts. Both profiles implement the same UAOS contracts.

## Domain repositories

The four legacy Agent repositories retain domain code, rules, references, data contracts, historical evidence and domain artifacts. Their old Universal Continuity adapter files remain readable as migration evidence but are no longer controller authority.

Each repository exposes `continuity/UAOS_ADAPTER.json` and points its Agent manifest at UAOS. New business tasks are UAOS-native. Existing resumable tasks are imported one way on first continuation.

## Time-sensitive migration

Task migration is semantic, not byte-for-byte replay. A historical A-share premarket task is not allowed to resume later as if its time window still existed. It must be reconciled as historical/post-close evidence before any remaining work is imported.

## Retirement policy

The old universal controller repository is not deleted during cutover because it contains audit/provenance evidence and is still referenced by historical commits. Its active entrypoint is replaced by a retirement redirect, and its protocol status becomes `RETIRED_READ_ONLY`. Deletion or GitHub archival is unnecessary for correctness and can be done later as repository hygiene.
