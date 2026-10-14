# Universal Agent OS

Universal Agent OS is a clean-slate, requirement-driven control plane for durable multi-agent work.

> Agents may reason, research, propose, generate and execute through controlled interfaces; the control kernel decides what becomes authoritative system state.

## Current stage

**The zero-cost usable baseline is complete. Paid/cloud infrastructure is optional.**

The default core uses Python + SQLite + local content-addressed files + capabilities already available in the active host/session. Built-in tools, connected plugins, browser/search tools, local scripts and free/public APIs can be registered as session or local capabilities. Paid and unknown-cost capabilities are not auto-selected.

The same control loop now executes representative financial-writing, novel, video and A-share workflows. Legacy continuity state is selectively migrated rather than copied wholesale, and the self-change lifecycle has a real local promotion/rollback drill.

## Authority

- Requirements v1.0: `docs/requirements/FROZEN_REQUIREMENTS_v1.0.md`
- Zero-cost requirement delta v1.1: `docs/requirements/FROZEN_REQUIREMENTS_v1.1.md`
- Local-first architecture: `docs/architecture/ARCHITECTURE_BLUEPRINT_v1.1.md`
- Usable baseline definition: `docs/assurance/USABLE_BASELINE.md`
- Current readiness: `docs/assurance/PRODUCTION_READINESS.json`

## Default local stack

- `SQLiteVersionedRepository` + `SQLiteAppendOnlyLedger` for durable authority and CAS;
- `SQLiteCheckpointRuntime` for cross-process workflow identity/checkpoints/control messages;
- `LocalContentAddressedStore` for artifacts;
- zero-cost-first host capability routing for current Agent/model/tool/plugin capabilities;
- `LocalWorkflowRunner` for checkpoint-bound domain execution;
- opportunistic maintenance when no always-on scheduler exists.

PostgreSQL, DBOS, remote S3, OpenAI Agents SDK/API and hosted CI remain optional enhancement adapters.

## Local commands

```bash
python -m pip install -e '.[dev]'
pytest
python scripts/uaos_status.py
python scripts/migrate_legacy_cutover.py --db .uaos/uaos.db
python scripts/self_change_drill.py
```
