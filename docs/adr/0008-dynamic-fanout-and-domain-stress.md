# ADR-021 — Dynamic Fan-Out and Domain Stress

Status: ACCEPTED
Date: 2026-10-14

## Decision

UAOS adds one generic runtime fan-out primitive rather than domain-specific parallel engines. A discovered item set is expanded into first-class work units with exact item bindings, unique outputs and an explicit merge dependency. The merge work unit remains HOLD until expansion is complete.

This primitive is intended for video shots, stock/universe members, long-text partitions and similar runtime-discovered work. It is not a hidden sub-agent loop: every expanded child is visible to the control plane and subject to the same capability, approval, evidence and recovery rules.

Phase 8 also corrects the authoritative PostgreSQL schema so plan external inputs and the complete work-unit contract (dependencies, inputs, outputs, executor constraints and bindings) can be reconstructed from authority rather than chat/Git.

The novel pilot preserves whole-source coverage, scoped distillation, canon/plan separation, minimum-sufficient writer context, hash-bound review invalidation and release authorization. The video pilot preserves approved asset identity, pre-generation briefs, maker/reviewer separation, cost envelopes and reviewed shot generation.
