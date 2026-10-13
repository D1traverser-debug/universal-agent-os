-- Universal Agent OS core authority schema (PostgreSQL)
-- Runtime truth belongs here; Git/chat/telemetry are not authority.

CREATE TABLE IF NOT EXISTS uaos_task (
    task_id TEXT PRIMARY KEY,
    intent TEXT NOT NULL,
    owner_domain TEXT NOT NULL,
    goal TEXT NOT NULL,
    done_condition TEXT NOT NULL,
    status TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    current_stage TEXT NOT NULL,
    next_action TEXT,
    workflow_id TEXT,
    plan_version INTEGER NOT NULL DEFAULT 1 CHECK (plan_version >= 1),
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version >= 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS uaos_requirement (
    requirement_id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    scope_type TEXT NOT NULL,
    scope_id TEXT,
    priority INTEGER NOT NULL DEFAULT 100,
    lifecycle_state TEXT NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL,
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version >= 1),
    CHECK ((scope_type = 'GLOBAL' AND scope_id IS NULL) OR (scope_type <> 'GLOBAL' AND scope_id IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS uaos_requirement_supersedes (
    requirement_id TEXT NOT NULL REFERENCES uaos_requirement(requirement_id),
    superseded_requirement_id TEXT NOT NULL REFERENCES uaos_requirement(requirement_id),
    PRIMARY KEY (requirement_id, superseded_requirement_id),
    CHECK (requirement_id <> superseded_requirement_id)
);

CREATE TABLE IF NOT EXISTS uaos_task_requirement (
    task_id TEXT NOT NULL REFERENCES uaos_task(task_id),
    requirement_id TEXT NOT NULL REFERENCES uaos_requirement(requirement_id),
    PRIMARY KEY (task_id, requirement_id)
);

CREATE TABLE IF NOT EXISTS uaos_plan (
    plan_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES uaos_task(task_id),
    version INTEGER NOT NULL CHECK (version >= 1),
    lane TEXT NOT NULL CHECK (lane IN ('PRODUCTION','CANDIDATE','EXPLORATION')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (task_id, version, lane)
);

CREATE TABLE IF NOT EXISTS uaos_work_unit (
    work_unit_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL REFERENCES uaos_plan(plan_id),
    task_id TEXT NOT NULL REFERENCES uaos_task(task_id),
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    risk TEXT NOT NULL,
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version >= 1)
);

CREATE TABLE IF NOT EXISTS uaos_action (
    action_id TEXT PRIMARY KEY,
    work_unit_id TEXT NOT NULL REFERENCES uaos_work_unit(work_unit_id),
    capability_id TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    target TEXT NOT NULL,
    side_effect_class TEXT NOT NULL,
    status TEXT NOT NULL,
    idempotency_key TEXT,
    approval_id TEXT,
    attempt INTEGER NOT NULL DEFAULT 1 CHECK (attempt >= 1),
    provider_ref TEXT,
    outcome TEXT,
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version >= 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uaos_action_idempotency_unique
ON uaos_action(capability_id, idempotency_key)
WHERE idempotency_key IS NOT NULL;

CREATE TABLE IF NOT EXISTS uaos_artifact (
    artifact_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 1),
    kind TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    storage_uri TEXT NOT NULL,
    producer_action TEXT REFERENCES uaos_action(action_id),
    state TEXT NOT NULL,
    visibility_state TEXT NOT NULL,
    lane TEXT NOT NULL CHECK (lane IN ('PRODUCTION','CANDIDATE','EXPLORATION')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (artifact_id, version)
);

CREATE TABLE IF NOT EXISTS uaos_knowledge (
    knowledge_id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    applicable_scope TEXT NOT NULL,
    state TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    lane TEXT NOT NULL CHECK (lane IN ('PRODUCTION','CANDIDATE','EXPLORATION')),
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version >= 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS uaos_ledger_event (
    sequence BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS uaos_ledger_aggregate_idx
ON uaos_ledger_event(aggregate_type, aggregate_id, sequence);

CREATE TABLE IF NOT EXISTS uaos_production_alias (
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    object_version INTEGER NOT NULL,
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version >= 1),
    PRIMARY KEY (object_type, object_id)
);
