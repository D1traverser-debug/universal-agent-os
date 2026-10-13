# Universal Agent OS

Universal Agent OS is a clean-slate, requirement-driven control plane for durable multi-agent work.

> Agents may reason, research, propose, generate and execute through controlled interfaces; the control kernel decides what becomes authoritative system state.

## Current stage

**Phase 11 implementation baseline complete; production readiness is still OPEN.**

The repository now contains deterministic contracts and reference implementations for task/requirement authority, durable runtime adapters, execution/capability routing, approvals and ambiguous side effects, DAG orchestration and dynamic fan-out, source/knowledge governance, evidence-based completion, domain SDKs (financial writing, novel, video, A-share), governed self-evolution, control-target resolution, topology authority, compatibility and retry policy.

Local cumulative integration currently passes the recorded Phase 0–11 suite. This is not a production certification. See `docs/assurance/PRODUCTION_READINESS.json` for live blockers and `docs/assurance/FROZEN_SCENARIO_COVERAGE.json` for the 20 frozen acceptance scenarios.

## Authority

- Frozen requirements: `docs/requirements/FROZEN_REQUIREMENTS_v1.0.md`
- Requirement lock: `docs/requirements/FROZEN_REQUIREMENTS_v1.0.gitblob`
- Architecture blueprint: `docs/architecture/ARCHITECTURE_BLUEPRINT_v1.md`
- Requirement mapping: `docs/architecture/REQUIREMENT_MAPPING.md`
- Production readiness: `docs/assurance/PRODUCTION_READINESS.json`

Frozen Requirements v1.0 is not edited in place. Requirement changes create a new version with explicit user/evidence-driven justification.

## Architecture stance

The implementation remains a modular monolith. PostgreSQL is the intended authority, DBOS is behind a `DurableRuntime` boundary, OpenAI Agents SDK is an execution adapter rather than the control plane, and domain packages cannot redefine shared continuity/action/knowledge/assurance authorities.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
```
