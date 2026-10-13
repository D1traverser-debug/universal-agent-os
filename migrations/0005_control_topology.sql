-- Control selection and subsystem topology authority.
ALTER TABLE uaos_task
    ADD COLUMN IF NOT EXISTS task_type TEXT,
    ADD COLUMN IF NOT EXISTS resume_eligible BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS default_resume BOOLEAN NOT NULL DEFAULT FALSE;

CREATE UNIQUE INDEX IF NOT EXISTS uaos_task_single_active_default_resume
ON uaos_task(default_resume)
WHERE default_resume = TRUE AND status NOT IN ('COMPLETE','CANCELLED');

CREATE TABLE IF NOT EXISTS uaos_subsystem (
    subsystem_id TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    root_path TEXT NOT NULL,
    parent_id TEXT REFERENCES uaos_subsystem(subsystem_id),
    lifecycle TEXT NOT NULL CHECK (lifecycle IN ('ACTIVE','DEPRECATED','RETIRED')),
    rule_refs TEXT[] NOT NULL DEFAULT '{}',
    state_refs TEXT[] NOT NULL DEFAULT '{}',
    knowledge_refs TEXT[] NOT NULL DEFAULT '{}',
    workflow_refs TEXT[] NOT NULL DEFAULT '{}',
    validation_refs TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (parent_id IS NULL OR parent_id <> subsystem_id)
);

CREATE TABLE IF NOT EXISTS uaos_subsystem_dependency (
    subsystem_id TEXT NOT NULL REFERENCES uaos_subsystem(subsystem_id),
    dependency_id TEXT NOT NULL REFERENCES uaos_subsystem(subsystem_id),
    PRIMARY KEY (subsystem_id, dependency_id),
    CHECK (subsystem_id <> dependency_id)
);

CREATE TABLE IF NOT EXISTS uaos_authority_binding (
    authority_key TEXT PRIMARY KEY,
    subsystem_id TEXT NOT NULL REFERENCES uaos_subsystem(subsystem_id),
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version >= 1),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
