# ADR-029 — Host Capabilities and Zero-Cost-First Routing

Status: ACCEPTED
Date: 2026-10-14

## Decision

UAOS treats capabilities already available in the current host/session as first-class executors. A host capability may be a ChatGPT built-in tool, connected plugin, browser/search tool, local script, free/public API, or another executor supplied by the embedding environment.

Capabilities declare both a cost class (`INCLUDED`, `FREE`, `PAID`, `UNKNOWN`) and availability (`SESSION`, `LOCAL`, `BACKGROUND`). Normal UAOS execution does not auto-route to `PAID` or `UNKNOWN` cost capabilities. Paid use requires an explicit request that opts in; an unknown-price capability requires a separate explicit opt-in. Even when paid use is allowed, zero-cost candidates remain preferred when they satisfy the mandatory quality and permission floor.

A `SESSION` plugin can execute while the user/host session is active. It must not be treated as a background worker. A background-required WorkUnit can route only to a capability explicitly observed as `BACKGROUND`.

## Why

The user's actual environment often already exposes useful tools without requiring a separate API account or always-on server. Requiring a hosted orchestration or commercial API for every task would add cost and fragility without improving the core control semantics.

The host bridge is deliberately callback-based and provider-neutral. UAOS owns action identity, permission/approval, output contracts, UNKNOWN handling and task state; the host owns how the callback reaches a particular plugin/tool.

## Failure semantics

If no current capability satisfies action, permission, quality, cost and availability constraints, the WorkUnit becomes BLOCKED. UAOS must report which capability class is missing. It must not silently buy capacity, lower a mandatory quality floor, or pretend a session-only tool is available in the background.
