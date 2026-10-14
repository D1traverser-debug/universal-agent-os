# Universal Agent OS

Universal Agent OS is a clean-slate, requirement-driven control plane for durable multi-agent work.

> Agents may reason, research, propose, generate and execute through controlled interfaces; the control kernel decides what becomes authoritative system state.

## Current stage

**Zero-cost local-first baseline is now the default. Domain cutover/E2E is still open.**

The core does not require PostgreSQL, DBOS, S3, OpenAI API or GitHub Actions. The default usable stack is Python + SQLite + local content-addressed files + whichever Agent/model/tool executor is already available in the host environment.

Optional adapters may improve scale or guarantees, but they are not prerequisites for the controller to function.

## Authority

- Requirements v1.0: `docs/requirements/FROZEN_REQUIREMENTS_v1.0.md`
- Zero-cost requirement delta v1.1: `docs/requirements/FROZEN_REQUIREMENTS_v1.1.md`
- Local-first architecture: `docs/architecture/ARCHITECTURE_BLUEPRINT_v1.1.md`
- Production/readiness boundary: `docs/assurance/PRODUCTION_READINESS.json`

## Default local stack

- `SQLiteVersionedRepository` + `SQLiteAppendOnlyLedger` for durable authority and CAS;
- `SQLiteCheckpointRuntime` for cross-process workflow identity/checkpoints/control messages;
- `LocalContentAddressedStore` for artifacts;
- UAOS executor ports for current host/Agent/model/tool capabilities;
- opportunistic maintenance when no always-on scheduler exists.

PostgreSQL, DBOS, remote S3, OpenAI Agents SDK/API and hosted CI remain optional enhancement adapters.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
```
