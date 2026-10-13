# Clean-Slate v4 Implementation Plan

Status: ACTIVE. The new repository exists and Phase 0 is in progress.

## Phase 0 — New repository and contracts
- initialize Python project and CI;
- copy frozen requirements v1.0 as immutable design input;
- add architecture docs/ADRs;
- define typed contracts for Task, Requirement, WorkUnit, Action, Artifact, KnowledgeItem, Capability, Subsystem, Approval, Evaluation;
- add contract tests before implementations.

Exit: schemas stable enough to build runtime; no domain business code yet.

## Phase 1 — State authority
- PostgreSQL migrations;
- repositories for tasks/requirements/plans/work units/actions/artifacts/knowledge/topology;
- append-only event/action ledger;
- optimistic version/CAS on authoritative mutable rows;
- artifact store interface + local dev adapter;
- production/candidate lane constraints.

Exit: X04/X09/X11/X13 mechanically represented.

## Phase 2 — Durable task runtime
- DurableRuntime interface;
- DBOS adapter;
- TaskWorkflow lifecycle;
- queues/priorities/schedules/messages;
- pause/cancel/requirement-update handling;
- version compatibility and recovery;
- inheritance/resume API.

Exit: generic long task survives process/chat restart and resumes without repeating confirmed work.

## Phase 3 — Execution fabric
- Capability Registry;
- generic executor protocol;
- OpenAI Agents SDK executor;
- MCP/function/HTTP/script adapters;
- sandbox workspace adapter;
- exact Action contract;
- idempotency/UNKNOWN reconciliation;
- approval binding and permission gate;
- cost/usage accounting.

Exit: tool/Agent execution cannot mutate authority outside controlled paths.

## Phase 4 — Planning and orchestration
- planner proposal schema;
- DAG validator;
- producer->artifact->consumer reachability checks;
- dependency-aware execution;
- impacted-subgraph replanning;
- multi-agent fan-out/fan-in/merge policies;
- capability routing.

Exit: complex multi-Agent workflow can execute with real artifact dependencies and no static dead links.

## Phase 5 — Knowledge and evidence
- source snapshot ingestion;
- provenance;
- parsing/chunking;
- candidate knowledge;
- optional pgvector embeddings;
- reconciliation and promotion lifecycle;
- scoped context builder;
- versioned compaction artifacts.

Exit: large-text distillation is resumable, source-bound and usable in subsequent work.

## Phase 6 — Assurance and delivery
- requirement-result trace;
- deterministic validators;
- semantic evaluator interface;
- independent-review policy;
- current artifact visibility/hash validation;
- completion gate and delivery receipt;
- capability/failure-class coverage reporting.

Exit: “done” requires evidence, not role claims.

## Phase 7 — Domain SDK + first pilot
Pilot: Financial Writing.
Why first: rich research/quality/delivery flow but fewer real-world destructive side effects than market execution or automated video production.

- domain manifest API;
- workflow template API;
- scoped requirement integration;
- knowledge namespace/eval suite hooks;
- migrate one real workflow end-to-end.

Exit: frozen scenario S2/S3/S8/S15 pass on the new system.

## Phase 8 — Novel and Video domains
Novel validates long-text coverage/compaction/knowledge transfer.
Video validates multi-Agent coordination, asset identity, provider/model routing, cost budgets and artifact lineage.

Exit: S6/S7/S17 pass.

## Phase 9 — A-share domain
Add time-sensitive data snapshots, source reconciliation, prerequisite completeness gates, trading-day semantics and post-hoc learning promotion.

Exit: S4/S5 pass without stale/partial data masquerading as complete evidence.

## Phase 10 — Evolution & maintenance
Only after core authority/assurance is proven:
- Incident and FailureClass pipelines;
- ChangeProposal lifecycle;
- scheduled health review;
- low-risk auto-maintenance policy;
- candidate sandbox/evals;
- promotion/rollback/retirement;
- complexity/toil metrics.

Exit: S11/S13/S16 pass; maintenance cannot bypass production gates.

## Phase 11 — Hardening
- selected multi-fault tests;
- restart/crash/fault injection;
- provider outage/replay tests;
- permission denial tests;
- migration/version skew tests;
- concurrency/race tests;
- storage corruption/visibility tests;
- cost and context budgets.

## Explicit non-goals before Phase 11
- Kubernetes;
- microservices;
- multiple orchestration frameworks;
- separate vector database;
- autonomous production code edits;
- migrating every legacy file/test.
