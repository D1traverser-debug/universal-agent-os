# Clean-Slate v4 — 冻结需求规格 v1.1

Status: `FROZEN_BASELINE_V1_1 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-14

v1.1 does not rewrite v1.0. It incorporates every requirement in `FROZEN_REQUIREMENTS_v1.0.md` unchanged and adds the following explicit user requirement. Where deployment/cost assumptions conflict, this v1.1 delta takes precedence.

## Z01 — Zero-cost core baseline
The default usable system must not require any paid external service, paid cloud resource, paid API subscription, paid hosted database, paid object store or paid CI runner.

## Z02 — Local-first persistence and recovery
The default implementation must provide durable task/requirement/action/knowledge state, optimistic concurrency/CAS, append-only evidence, checkpoint/resume and artifact persistence using components that can run locally without paid infrastructure. SQLite and the local filesystem are acceptable baseline implementations.

## Z03 — External platforms are optional adapters
PostgreSQL, DBOS, S3-compatible remote storage, OpenAI API/Agents SDK, GitHub Actions and any other hosted/provider-specific integration may exist only as optional enhancement adapters. Their absence must not make the core controller unusable.

## Z04 — Explicit graceful degradation
If an optional external capability is absent, the system must state which guarantee is reduced instead of silently failing or pretending the capability exists. Examples: no always-on background worker means opportunistic maintenance on the next invocation; no remote object store means local-only artifacts; no commercial model API means use the current host/available executor or leave that provider-specific action unavailable.

## Z05 — No paid provisioning without explicit approval
The system must never create, enable or consume a paid external resource merely to satisfy an internal implementation choice unless the user explicitly authorizes that specific paid use.

## Authority composition
Current requirements authority = `FROZEN_REQUIREMENTS_v1.0.md` + Z01–Z05 in this file.
