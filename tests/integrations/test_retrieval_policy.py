from pathlib import Path

import pytest

from uaos.integrations import RetrievalDenied, RetrievalPolicy, RetrievalPurpose

ROOT = Path(__file__).resolve().parents[2]
POLICY = RetrievalPolicy.from_path(ROOT / "config" / "RETRIEVAL_POLICY.json")


def test_retired_controller_blocked_in_active_execution():
    with pytest.raises(RetrievalDenied):
        POLICY.authorize("D1traverser-debug/universal-continuity-agent", "ENTRYPOINT.md")


def test_retired_controller_historical_access_requires_explicit_intent():
    with pytest.raises(RetrievalDenied):
        POLICY.authorize("D1traverser-debug/universal-continuity-agent", "README.md", purpose=RetrievalPurpose.HISTORICAL_QUERY)
    POLICY.authorize("D1traverser-debug/universal-continuity-agent", "README.md", purpose=RetrievalPurpose.HISTORICAL_QUERY, explicit_historical=True)


def test_old_domain_continuity_paths_are_blocked():
    assert not POLICY.is_allowed("D1traverser-debug/video-growth-agent", "continuity/tasks/video-growth-main/TASK_MANIFEST.json")
    assert not POLICY.is_allowed("D1traverser-debug/financial-writing-agent", "continuity/UNIVERSAL_PROTOCOL_ADAPTER.json")
    assert not POLICY.is_allowed("D1traverser-debug/novel-writing-agent", "SKILL.md")


def test_current_binding_surfaces_are_allowed():
    assert POLICY.is_allowed("D1traverser-debug/video-growth-agent", "continuity/UAOS_MANIFEST.json")
    assert POLICY.is_allowed("D1traverser-debug/financial-writing-agent", "UAOS_SKILL.md")
    assert POLICY.is_allowed("D1traverser-debug/a-share-event-driven-agent", "continuity/EXECUTION_CAPABILITIES.json")


def test_uaos_migration_docs_are_cold_path():
    assert not POLICY.is_allowed("D1traverser-debug/universal-agent-os", "docs/migration/CUTOVER_EVIDENCE_2026-10-14.json")
    assert POLICY.is_allowed("D1traverser-debug/universal-agent-os", "docs/migration/CUTOVER_EVIDENCE_2026-10-14.json", purpose=RetrievalPurpose.HISTORICAL_QUERY, explicit_historical=True)


def test_normal_business_evidence_remains_retrievable():
    assert POLICY.is_allowed("D1traverser-debug/video-growth-agent", "projects/ai-self-media-commercialization/PROJECT_MANIFEST.json")
    assert POLICY.is_allowed("D1traverser-debug/novel-writing-agent", "projects/FQ001_MINGRI_ORDER/checkpoints/CURRENT_CHECKPOINT.json")
