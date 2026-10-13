-- Point-in-time and completeness evidence for source snapshots.
CREATE TABLE IF NOT EXISTS uaos_source_snapshot (
    snapshot_id TEXT PRIMARY KEY,
    source_uri TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    content_max_available_at TIMESTAMPTZ,
    storage_uri TEXT NOT NULL,
    media_type TEXT NOT NULL DEFAULT 'application/octet-stream',
    completeness TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK (completeness IN ('FULL','PARTIAL','UNKNOWN')),
    gaps TEXT[] NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (content_max_available_at IS NULL OR content_max_available_at <= observed_at),
    CHECK (completeness <> 'FULL' OR cardinality(gaps) = 0)
);

CREATE INDEX IF NOT EXISTS uaos_source_snapshot_hash_idx
ON uaos_source_snapshot(content_hash);

CREATE INDEX IF NOT EXISTS uaos_source_snapshot_availability_idx
ON uaos_source_snapshot(content_max_available_at);
