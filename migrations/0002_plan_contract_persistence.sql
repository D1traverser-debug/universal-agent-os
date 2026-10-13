-- Persist the complete plan/work-unit contract required for authoritative recovery.
ALTER TABLE uaos_plan
    ADD COLUMN IF NOT EXISTS external_inputs TEXT[] NOT NULL DEFAULT '{}';

ALTER TABLE uaos_work_unit
    ADD COLUMN IF NOT EXISTS dependencies TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS required_inputs TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS expected_outputs TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS executor_constraints TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS bindings JSONB NOT NULL DEFAULT '{}'::jsonb;
