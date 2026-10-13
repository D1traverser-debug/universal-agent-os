# Frozen Requirement -> Architecture Mapping

| Requirement group | Primary owner | Supporting components | Mechanical evidence |
|---|---|---|---|
| A Intent / requirements / scope | Control Kernel | State Plane, Durable Runtime | typed intent/scope; requirement lifecycle; task identity; update propagation |
| B Autonomous completion | Control Kernel + Durable Runtime | Assurance | done-condition; durable TaskWorkflow; completion gate |
| C Knowledge/evidence/decision | Control Kernel + State/Knowledge | Execution Fabric, Assurance | provenance; reconciliation; decision record; knowledge usage linkage |
| D Orchestration/resource coordination | Durable Runtime + Execution Fabric | Control Kernel | DAG validation; capability handshake; queues; executor binding; producer-artifact-consumer checks |
| E Topology/change governance | Control Kernel/Topology Registry | Evolution | manifests; owner binding; impact analysis; lifecycle states; topology change trigger |
| F Continuity | Durable Runtime + State Plane | Execution Fabric | durable workflow id; checkpoints; cursors; compatibility/version checks; reconstructed context |
| G Data/artifact/knowledge governance | State/Artifact/Knowledge Plane | Assurance | IDs/hashes/snapshots/lineage; approval aliases; current deliverable proof |
| H Fault diagnosis/recovery | Assurance & Recovery + Durable Runtime | Action Journal | fault class; hold/isolation; UNKNOWN reconciliation; bounded retries; recovery verification |
| I Evolution/maintenance/complexity | Evolution & Maintenance | Assurance, Topology | incident/change lifecycle; eval gate; rollback/retire; complexity budget; scheduled reviews |
| J Verification/delivery | Assurance | State/Artifact, Control Kernel | requirement-result trace; evaluator evidence; delivery identity; status semantics |

## Cross-cutting constraints

- X01: user-facing API hides internal orchestration.
- X02: complexity budget + default modular monolith + no duplicate orchestration layer.
- X03: mandatory impact analysis + regression suite before promotion.
- X04: typed object classes and separate authority/observation/candidate states.
- X05: exact-action approval contract and risk policy.
- X06: task/domain/lane IDs on every state object; queues and namespaces isolate failures.
- X07: explicit application/workflow/schema versions and migration states.
- X08: cost/latency/token/tool counters attached to work units and change proposals.
- X09: task/work-unit/action/artifact/evidence IDs form traceable lineage.
- X10: completion gate uses execution evidence, never role claims.
- X11: schemas, transactions, state machines, capability gates and permissions enforce high-impact invariants.
- X12: prerequisite validator blocks or explicitly downgrades when required evidence/capability is missing.
- X13: candidate/exploration lane cannot update production aliases without promotion transaction.
- X14: capability-scoped permissions and secret isolation.
- X15: observability emits signals; only validated control-plane actions mutate authority.
