# Live Integration Verification

Status: `HARNESS_READY / LIVE_EVIDENCE_PENDING`

This layer exists specifically to prevent unit tests, mocks, role labels or architecture prose from closing production blockers.

## Local PostgreSQL/DBOS

With Docker/Compose available:

```bash
docker compose up -d postgres
python -m pip install -e '.[dev,live]'
export UAOS_DATABASE_URL='postgresql://uaos:uaos-local-only@localhost:5432/uaos'
export DBOS_SYSTEM_DATABASE_URL="$UAOS_DATABASE_URL"
python scripts/live_verify.py postgres
python scripts/live_verify.py dbos
```

For an actual process-crash recovery drill:

```bash
python scripts/dbos_crash_probe.py start   # intentionally exits 91
python scripts/dbos_crash_probe.py recover # a new process must recover the same durable workflow
```

The PostgreSQL probe applies every repository migration, verifies row-version CAS rejects a stale writer, and verifies the append-only ledger can round-trip a live event. The DBOS probe verifies durable workflow identity/idempotency. The crash probe verifies recovery in a fresh process.

## S3-compatible object store

```bash
docker compose up -d minio
export AWS_ACCESS_KEY_ID='uaos-minio'
export AWS_SECRET_ACCESS_KEY='uaos-minio-secret'
export UAOS_OBJECT_STORE_URL='http://localhost:9000'
export UAOS_OBJECT_STORE_BUCKET='uaos-live'
python scripts/live_verify.py object-store
```

The probe uses the production-shaped `S3ContentAddressedStore`, performs a real network put/get/hash/delete roundtrip and fails on corrupted content. MinIO proves protocol/adapter behavior only; the eventual production bucket must still be verified separately.

## OpenAI Agents executor

Provider verification is intentionally opt-in because it uses a real API credential and may incur a small API charge. No model is guessed.

```bash
export OPENAI_API_KEY='...'
export UAOS_OPENAI_PROBE_MODEL='<explicit API model id>'
python scripts/live_verify.py openai
```

The probe goes through `OpenAIAgentsExecutor`; it does not give the Agent side-effecting tools or authority-state access.

## Exit semantics

- `PASS`: the real configured dependency executed the requested probe successfully.
- `BLOCKED` (exit 2): required environment/credential/model was not configured; this is not a failure and not a pass.
- `FAIL` (exit 1): the real dependency was configured and the live invariant failed.

GitHub workflow `.github/workflows/live-integration.yml` runs PostgreSQL/DBOS, an explicit DBOS crash/recovery drill, and S3-compatible artifact integration when a hosted runner is available. OpenAI provider verification runs only on manual workflow dispatch and requires repository secret/variable configuration.

Passing these harnesses does not close all production readiness blockers. The final production object store, four domain live E2Es, background maintenance and controlled self-change still need their own evidence.
