# ADR-016 — Execution Fabric Boundaries

Status: ACCEPTED
Date: 2026-10-14

## Decision

Execution capability is represented by current observations, not by Agent names or prompt declarations. A request is routed only to an eligible capability whose action set, permissions, freshness, quality floor and cost ceiling satisfy the request.

The OpenAI Agents SDK baseline adapter is reasoning/generation-only. It receives no authoritative side-effecting tools. Side effects are separate executors governed by the UAOS Action/approval/reconciliation contracts.

## Why

This mechanically separates:
- “the model can reason about an operation” from “the environment can perform it”;
- an Agent role declaration from a current capability handshake;
- low-risk autonomous work from operations requiring exact user approval;
- provider timeout from known success/failure.

## Current OpenAI SDK fit

The current Agents SDK offers Agent/Runner execution, tools, MCP integration, HITL, tracing, sessions and sandbox workspaces. UAOS uses those features behind adapters, while keeping task truth, durable state, artifact identity and completion outside the SDK session.

## Approval semantics

Approval is not automatically required for every write; policy/risk determines `approval_required`. When required, the grant is bound to exact `action_id`, target, parameter hash/version and expiry. This preserves autonomy for already-authorized low-risk operations without turning broad approval into an unlimited capability.

## Ambiguous outcomes

Executors may return `UNKNOWN`. The coordinator preserves it. A reconciler may probe the external system and resolve it to CONFIRMED or FAILED. If no reliable reconciliation exists, UNKNOWN remains unresolved rather than being silently retried or guessed.
