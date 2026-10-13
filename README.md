# Universal Agent OS

Universal Agent OS is a clean-slate, requirement-driven control plane for durable multi-agent work.

The core design rule is simple:

> Agents may reason, propose, research, generate and execute through controlled interfaces; the control kernel decides what becomes authoritative system state.

## Current stage

Phase 0 — frozen requirements, architecture baseline and typed cross-layer contracts.

The repository intentionally starts as a modular monolith. It does **not** begin with microservices, Kubernetes, multiple orchestration frameworks or a separate vector database.

## Authority

- Frozen requirements: `docs/requirements/FROZEN_REQUIREMENTS_v1.0.md`
- Requirement lock: Git blob SHA recorded in `docs/requirements/FROZEN_REQUIREMENTS_v1.0.gitblob`
- Architecture blueprint: `docs/architecture/ARCHITECTURE_BLUEPRINT_v1.md`
- Requirement mapping: `docs/architecture/REQUIREMENT_MAPPING.md`
- Initial ADRs: `docs/adr/0001-initial-decisions.md`

The frozen requirements are not changed to make implementation easier. A change requires a new version with an explicit reason.

## Phase 0 contracts

The first executable code establishes invariants for:

- task identity and completion evidence;
- scoped requirement lifecycle;
- work-unit DAGs and producer→artifact→consumer reachability;
- exact-action approvals;
- side-effect action state transitions including ambiguous outcomes;
- artifact identity and knowledge promotion states.

These contracts are deliberately independent of any specific Agent framework or durable runtime.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
```
