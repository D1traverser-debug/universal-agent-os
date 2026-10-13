-- Self-evolution and maintenance governance. Candidates are not production changes.
CREATE TABLE IF NOT EXISTS uaos_incident (
    incident_id TEXT PRIMARY KEY,
    task_id TEXT REFERENCES uaos_task(task_id),
    domain_id TEXT,
    summary TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    severity TEXT NOT NULL,
    evidence_refs TEXT[] NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (cardinality(evidence_refs) > 0)
);
CREATE INDEX IF NOT EXISTS uaos_incident_fingerprint_idx ON uaos_incident(fingerprint);

CREATE TABLE IF NOT EXISTS uaos_failure_class (
    failure_class_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    root_layer TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS uaos_failure_class_incident (
    failure_class_id TEXT NOT NULL REFERENCES uaos_failure_class(failure_class_id),
    incident_id TEXT NOT NULL REFERENCES uaos_incident(incident_id),
    PRIMARY KEY (failure_class_id, incident_id)
);

CREATE TABLE IF NOT EXISTS uaos_change_proposal (
    proposal_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    target_scope TEXT NOT NULL,
    added_mechanisms TEXT[] NOT NULL DEFAULT '{}',
    replaced_mechanisms TEXT[] NOT NULL DEFAULT '{}',
    retired_mechanisms TEXT[] NOT NULL DEFAULT '{}',
    why_not_reuse TEXT NOT NULL,
    retirement_rationale TEXT NOT NULL,
    rollback_plan TEXT NOT NULL,
    expected_benefit TEXT NOT NULL,
    new_failure_modes TEXT[] NOT NULL DEFAULT '{}',
    required_scenarios TEXT[] NOT NULL,
    complexity_delta JSONB NOT NULL,
    evidence_refs TEXT[] NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('DRAFT','EVALUATED','APPROVED','PROMOTED','REJECTED','ROLLED_BACK','RETIRED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (cardinality(required_scenarios) > 0),
    CHECK (cardinality(evidence_refs) > 0)
);

CREATE TABLE IF NOT EXISTS uaos_change_proposal_failure_class (
    proposal_id TEXT NOT NULL REFERENCES uaos_change_proposal(proposal_id),
    failure_class_id TEXT NOT NULL REFERENCES uaos_failure_class(failure_class_id),
    PRIMARY KEY (proposal_id, failure_class_id)
);

CREATE TABLE IF NOT EXISTS uaos_evaluation (
    evaluation_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL REFERENCES uaos_change_proposal(proposal_id),
    scenario_refs TEXT[] NOT NULL,
    metrics_before JSONB NOT NULL,
    metrics_after JSONB NOT NULL,
    acceptance_checks JSONB NOT NULL,
    regression_failures TEXT[] NOT NULL DEFAULT '{}',
    passed BOOLEAN NOT NULL,
    evidence_refs TEXT[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (cardinality(scenario_refs) > 0),
    CHECK (cardinality(evidence_refs) > 0)
);

CREATE TABLE IF NOT EXISTS uaos_post_promotion_observation (
    observation_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL REFERENCES uaos_change_proposal(proposal_id),
    healthy BOOLEAN NOT NULL,
    metrics JSONB NOT NULL,
    evidence_refs TEXT[] NOT NULL,
    regression_refs TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (cardinality(evidence_refs) > 0)
);

CREATE TABLE IF NOT EXISTS uaos_maintenance_run (
    maintenance_id TEXT PRIMARY KEY,
    scope TEXT NOT NULL,
    trigger TEXT NOT NULL,
    risk TEXT NOT NULL CHECK (risk IN ('LOW','MEDIUM','HIGH')),
    background_capability_available BOOLEAN NOT NULL,
    foreground_priority_active BOOLEAN NOT NULL,
    production_mutation_requested BOOLEAN NOT NULL,
    explicit_approval_id TEXT,
    allowed BOOLEAN NOT NULL,
    mode TEXT NOT NULL,
    reasons TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
