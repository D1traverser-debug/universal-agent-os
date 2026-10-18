# Clean-Slate v4 Architecture Blueprint v1.0

> **Historical design baseline (v1.0), not the current UAOS 2.8 runtime authority.** Consult `CURRENT_SYSTEM.json`, `config/SYSTEM_MAP.json` and the current canonical owner policies before making execution, write or resume decisions. This note does **not** retire the separate Frozen Requirements v1.0 baseline.

Status: BASELINE ACCEPTED / PHASE 0 BOOTSTRAP
Requirements authority: Frozen Requirements v1.0 (A–J, X01–X15)

## 1. Architectural thesis

The system is a deterministic control plane around probabilistic executors.

The user states goals. The control plane owns intent, requirements, task identity, task state, plans, permissions, side effects, lineage, recovery, verification and delivery. LLM agents may plan, research, synthesize, critique, generate and propose changes, but they do not directly become the authority for system state.

Core rule:

> Agents propose and execute through controlled interfaces; the kernel decides what becomes authoritative.

This avoids the current failure mode where prompts, role claims, chat summaries or agent output are mistaken for durable truth.

## 2. Top-level architecture

The system has six primary layers and one cross-cutting plane.

### 2.1 Control Kernel
Owns:
- intent and scope classification;
- requirement lifecycle and precedence;
- task creation and task identity;
- completion criteria;
- plan proposal validation and replanning;
- topology/owner registry;
- policy/risk decisions;
- user override impact analysis.

It is deterministic wherever possible. LLMs can advise, but state transitions are typed and validated.

### 2.2 Durable Runtime
Owns:
- durable task workflows;
- checkpoints and resume;
- dependency graph execution;
- queues, priorities and concurrency;
- schedules/background maintenance;
- workflow messaging (requirement change, pause, cancel, approval);
- workflow/application version compatibility;
- recovery after process/session failure.

Baseline engine: DBOS Python, hidden behind an internal DurableRuntime interface.

### 2.3 Execution Fabric
Owns:
- capability registry;
- executor selection;
- Agent / model / provider / tool / MCP / script / sandbox adapters;
- capability handshakes;
- cost/quality/latency/resource routing;
- permissions and exact-action approval;
- side-effect action journal;
- idempotency and ambiguous-outcome reconciliation.

Default AI executor adapter: OpenAI Agents SDK. It is not the task state store and not the system authority.

### 2.4 State, Artifact & Knowledge Plane
Owns authoritative persistent objects:
- task records;
- scoped requirements;
- plan/work-unit state;
- execution/action ledger;
- subsystem manifests;
- capability metadata;
- artifacts/assets;
- evidence and source snapshots;
- knowledge candidates/canonical knowledge;
- approvals;
- evaluations/incidents/change proposals.

Storage baseline:
- PostgreSQL: authoritative metadata/state and execution ledger;
- pgvector: optional semantic retrieval inside PostgreSQL, enabled only when needed;
- S3-compatible object storage: large artifacts, source snapshots, video/image/document assets;
- Git: code/config/versioned schemas only, never the live runtime state authority.

### 2.5 Assurance & Recovery
Owns:
- requirement-to-result trace;
- structural validators;
- semantic reviewers;
- independence policy;
- artifact/delivery verification;
- fault classification;
- retry/reconcile/compensation decisions;
- capability/failure-class coverage reporting;
- final completion gate.

### 2.6 Evolution & Maintenance
Owns:
- incident clustering and failure classes;
- research of alternatives;
- change proposals;
- candidate isolation;
- reproducible evaluation;
- promotion/rollback/retirement;
- complexity budgets;
- scheduled health reviews;
- subsystem drift checks.

It cannot silently promote high-impact changes. Low-risk self-maintenance is allowed only within explicit policy.

### 2.7 Observability Plane (cross-cutting)
Uses OpenTelemetry-compatible traces/metrics/logs.

Observability is evidence and diagnosis, not authoritative state. Task/work-unit/action/artifact IDs correlate telemetry back to the state plane.

## 3. Core object model

### Task
Stable task identity independent of chat/session.
Fields include: task_id, intent, scope, owner_domain, goal, done_condition, requirement_snapshot, workflow_id, plan_version, status, priority, current_stage, next_action.

### Requirement
Typed user/system requirement.
Fields include: requirement_id, scope_type, scope_id, priority, lifecycle_state, supersedes, effective_from, content/schema payload.

### Plan / WorkUnit
A plan is versioned. WorkUnits form a DAG.
Each WorkUnit has dependencies, inputs, expected outputs, executor constraints, risk, completion criteria and current status.

### Action
Every external or authoritative side effect is an Action.
State machine:
PREPARED -> SENT -> CONFIRMED
              -> UNKNOWN -> RECONCILED -> CONFIRMED / FAILED / COMPENSATED

Key fields: action_id, work_unit_id, capability_id, request_hash, target, side_effect_class, idempotency_key, approval_id, attempt, provider_ref, outcome.

### Artifact
Stable artifact identity with immutable versions.
Fields: artifact_id, kind, version, content_hash, storage_uri, producer_action, lineage, approval_state, visibility_state.

### KnowledgeItem
Lifecycle:
RAW_EVIDENCE -> CANDIDATE -> EVALUATED -> CANONICAL -> RETIRED

Fields include source provenance, applicable scope, confidence, evidence set, supersedes, embedding reference and usage links.

### Subsystem
Manifest-driven domain package.
Fields: subsystem_id, version, owner, capabilities, workflows, dependencies, knowledge namespaces, required tools, eval suites, risk profile, lifecycle.

### Approval
Approval is bound to an exact action, target, parameter hash/version, approver and expiry. Generic “you may edit GitHub” approvals are not reused for materially different actions.

### Evaluation / Incident / ChangeProposal
These form the assurance and evolution lifecycle and preserve why a mechanism was changed, what evidence justified it, and what old mechanism was retired.

## 4. Authoritative state rules

1. Runtime truth lives in PostgreSQL, not chat summaries or Git files.
2. Large files live in object storage; DB stores stable identity, hash, provenance and current approved version.
3. Git stores source code, schemas, migrations, domain manifests and versioned policy definitions.
4. Telemetry is observational and cannot directly mutate authority.
5. Agent/session memory is working context, not authoritative durable state.
6. Every authoritative mutation passes through typed kernel/state APIs.
7. Direct agent writes to authoritative tables/object aliases are prohibited.
8. Candidate/exploration state uses a separate lane and cannot overwrite production aliases before promotion.

## 5. Task lifecycle

1. INGEST
- classify intent/scope;
- resolve active requirements;
- create or select task identity.

2. DEFINE
- establish goal, done-condition, risk and permissions;
- identify unknowns and mandatory evidence.

3. PLAN
- planner agent/code may propose DAG;
- kernel validates dependency reachability, capabilities, resources, permissions and output producers;
- commit plan version.

4. EXECUTE
- durable runtime dispatches WorkUnits;
- each WorkUnit binds an executor and immutable input snapshot;
- side effects go through Action contract.

5. SUPERVISE
- monitor errors, unknown outcomes, requirement changes, user overrides, resource limits;
- replan impacted subgraph only; reuse valid unaffected outputs.

6. VERIFY
- build requirement->result map;
- run deterministic checks first;
- use semantic/independent reviewer only where needed;
- verify actual deliverable version and accessibility.

7. DELIVER
- present result first;
- publish delivery receipt and remaining risks;
- persist final checkpoint.

8. COMPLETE / PAUSE / BLOCK
- state is explicit; no ambiguous “probably done”.

## 6. Resume / inheritance

“继承” never depends on chat transcript continuity.

Flow:
1. query resumable tasks in user scope;
2. if one unambiguous target exists, select it automatically;
3. if genuinely ambiguous, present minimal selection;
4. load task record, active requirements, latest plan, valid WorkUnits, unresolved Actions, required artifacts/knowledge refs;
5. validate workflow/app compatibility;
6. resume from durable runtime checkpoint;
7. revalidate time-sensitive external facts before using them.

Context for the LLM is rebuilt from authority. It is not “restore the whole previous chat”.

## 7. Context construction and compaction

Each Agent call receives only:
- current task goal/done-condition;
- scoped effective requirements;
- current WorkUnit contract;
- relevant upstream artifacts;
- scoped canonical knowledge/evidence;
- allowed tools and risk limits.

Compaction is treated as a versioned transformation artifact. It must preserve unresolved obligations, approvals, tool/result pairing, provenance, important decisions and next actions.

## 8. Multi-agent coordination

Default pattern: orchestrator retains global task ownership; specialists are invoked as bounded executors/tools.

Use free handoff only when ownership transfer is semantically correct (primarily interactive conversational tasks).

Rules:
- no shared mutable scratchpad as authority;
- each specialist gets an immutable input contract;
- outputs become versioned artifacts/evidence;
- fan-out work can run concurrently;
- fan-in passes through merge/arbitration;
- reviewers cannot approve work they did not actually inspect;
- same-model reviewer is allowed for low-risk semantics but does not count as independent assurance;
- higher-risk work can route review to a different prompt, model, provider, deterministic validator or external data source.

## 9. Side effects and ambiguous outcomes

Every side-effecting operation is wrapped as Action.

Before execution:
- verify capability;
- verify permission/approval;
- assign idempotency key where supported;
- record PREPARED request hash.

After request is sent:
- record provider reference if available;
- only mark CONFIRMED with positive evidence.

On timeout/lost acknowledgement:
- set UNKNOWN;
- probe external system first;
- retry only if replay safety is known or duplication is acceptable and explicitly authorized;
- otherwise HOLD / compensate / ask for approval.

This logic is shared by email, file writes, Git operations, API mutations, publishing, payments-like effects, etc.

## 10. Capability registry and routing

Capability records describe what is actually executable now, not just what a prompt says an Agent can do.

Each capability records:
- capability_id;
- executor adapter;
- provider/model/tool version;
- health and last handshake;
- permissions;
- supported input/output schemas;
- side-effect class;
- latency/cost/quality profile;
- rate/usage limits;
- compatibility constraints.

Routing priority:
1. mandatory correctness/quality constraints;
2. permissions and safety;
3. capability availability;
4. task fit;
5. cost/latency/usage budget.

Fallback never silently lowers a mandatory requirement.

## 11. Knowledge system

No single undifferentiated “memory”.

Namespaces:
- user/global requirements;
- system operational knowledge;
- domain canonical knowledge;
- task-local evidence;
- candidate learning;
- source snapshots.

Ingestion pipeline:
SOURCE -> SNAPSHOT -> PARSE/CHUNK -> EXTRACT -> RECONCILE -> CANDIDATE -> EVAL -> PROMOTE

Retrieval is hybrid metadata + lexical + optional vector similarity. Semantic retrieval is a search aid, never proof of truth.

Every promoted method must retain provenance and scope. A single novel, trading day or incident cannot directly become a universal rule.

## 12. Subsystem model

A subsystem is a package that plugs into the shared kernel, not a separate mini-platform by default.

A DomainManifest declares:
- identity/version/owner;
- domain capabilities;
- agent specs;
- workflow templates;
- artifact schemas;
- knowledge namespaces;
- tools/providers;
- evaluation suites;
- dependencies;
- risk/approval rules.

Examples:
- financial_writing;
- a_share;
- video;
- novel.

All inherit the shared runtime, action journal, state, knowledge, assurance and evolution APIs. Domain logic remains inside its domain package.

## 13. Evolution and anti-bloat lifecycle

Failure/user correction -> Incident -> FailureClass -> ChangeProposal -> Research -> Candidate -> Eval -> Approval (if required) -> Promotion -> Observe -> Retire/Rollback.

Every non-trivial ChangeProposal must state:
- capability added;
- why existing mechanism cannot satisfy it;
- mechanism replaced;
- code/rules/files removed;
- new state introduced;
- new failure modes;
- runtime/context/tool/maintenance cost;
- rollback plan;
- evaluation evidence.

A proposal that only adds another rule/Agent/file without explaining replacement and benefit is blocked from promotion.

## 14. Idle maintenance

Implemented as real durable schedules, not a promise in a prompt.

HealthReviewWorkflow runs at low priority and can inspect:
- repeated failure classes;
- stale dependencies/providers;
- unresolved UNKNOWN actions;
- long-running blocked tasks;
- unused/duplicated capabilities;
- stale knowledge;
- orphan artifacts;
- complexity/toil metrics;
- domain drift.

Low-risk reversible maintenance may auto-apply within policy. High-impact code/architecture/data changes create ChangeProposals and wait for required approval.

## 15. Assurance model

Assurance is requirement-driven.

For each task, generate an AssurancePlan from:
- active requirements;
- risk class;
- artifact types;
- side effects;
- domain eval suite.

Evidence levels:
1. declaration only;
2. structural/schema check;
3. deterministic execution evidence;
4. semantic evaluation;
5. independent/heterogeneous confirmation;
6. observed live outcome.

Claims are capped by the strongest actual evidence. Test count is not a quality metric by itself.

## 16. Technology baseline

- Language: Python for kernel/runtime/domain SDK.
- Durable execution: DBOS behind internal interface.
- Database: PostgreSQL.
- Semantic search: pgvector only if/when useful.
- Artifact store: S3-compatible interface; local filesystem adapter for development.
- AI executor: OpenAI Agents SDK adapter by default.
- External tools: MCP + typed function/HTTP adapters.
- Sandboxed file/code work: sandbox executor / Docker-backed workspace where appropriate.
- Schemas: Pydantic + SQL migrations.
- Observability: OpenTelemetry-compatible tracing/metrics/logging.
- API/UI: thin FastAPI/admin UI later; not part of kernel semantics.

## 17. Deliberately excluded from baseline

- microservice decomposition;
- Kafka;
- Redis as a required coordinator;
- separate vector database;
- LangGraph as a second durability/orchestration authority;
- a global shared chat transcript as memory;
- autonomous code mutation without promotion gates;
- one Agent per imagined role;
- blockchain/consensus/distributed consensus for current single-system scope;
- Kubernetes as a development requirement.

These can only be introduced after measured evidence shows the baseline cannot satisfy a frozen requirement.

## 18. Scale/HA escape hatch

DBOS is selected for the initial architecture because it keeps durable execution close to Python/Postgres and avoids a separate orchestration cluster.

The DurableRuntime interface prevents lock-in. Re-evaluate Temporal (or another engine) only when measured requirements demand capabilities the baseline cannot reasonably deliver, such as substantially stronger independent orchestration operations, cross-region/high-availability requirements, or workload scale/operational constraints that make the Postgres-backed baseline unsuitable.

A runtime migration is a versioned subsystem change and must preserve Task/Action/Artifact identities and migration evidence.

## 19. Security model

- least-privilege capability tokens;
- secrets from secret manager/environment injection only;
- secrets never stored as ordinary knowledge;
- exact-action approval binding;
- sandbox untrusted file/code execution;
- state mutations through typed APIs;
- domain ownership boundaries;
- audit trail for high-impact actions;
- no tool capability assumed from model instructions.

## 20. Definition of architecture-ready

Architecture is ready for repository implementation when:
- every frozen A–J capability maps to at least one owning component;
- every X constraint maps to a mechanical or explicitly bounded control;
- no second authority exists for task state, requirements, artifacts or knowledge promotion;
- runtime and Agent frameworks are replaceable behind internal contracts;
- migration path from legacy state is defined;
- initial repo layout and implementation sequence are defined;
- scenario tests can be derived without inventing new requirements.

This blueprint satisfies those design conditions. The new repository has been created and Phase 0 materialization is underway.
