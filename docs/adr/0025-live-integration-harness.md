# ADR-025 — Live Integration and Crash-Recovery Harness

Status: ACCEPTED
Date: 2026-10-14

## Decision

After Phase 11, local/reference tests remain necessary but cannot close production-readiness blockers that depend on actual infrastructure. UAOS therefore has a separate live verification layer with fail-closed semantics.

PostgreSQL verification must apply the real migration set and demonstrate authoritative row-version CAS plus ledger persistence. DBOS verification must demonstrate workflow identity/idempotency against PostgreSQL and a separate crash drill must kill the first process after durable workflow creation, then recover that workflow from a fresh process using the same application version.

The OpenAI Agents SDK verification uses the existing bounded reasoning/generation executor and receives no authoritative side-effect tools. It requires an explicit API model id; the harness never guesses a model. Provider checks are manual/credentialed because they can incur external cost.

Missing infrastructure or credentials are `BLOCKED`, not PASS. A configured dependency that violates the invariant is `FAIL`. Mocked results cannot promote R2/R3/R4 to complete.

Dependencies are isolated in the `live` optional extra. The core package stays framework-light and does not make DBOS, Psycopg or OpenAI Agents mandatory for every installation.
