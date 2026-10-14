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


def test_retired_domain_control_paths_are_blocked():
    assert not POLICY.is_allowed("D1traverser-debug/video-growth-agent", "continuity/tasks/video-growth-main/TASK_MANIFEST.json")
    assert not POLICY.is_allowed("D1traverser-debug/financial-writing-agent", "continuity/UNIVERSAL_PROTOCOL_ADAPTER.json")
    assert not POLICY.is_allowed("D1traverser-debug/novel-writing-agent", "continuity/TASK_INDEX.json")
    assert not POLICY.is_allowed("D1traverser-debug/a-share-event-driven-agent", "config/cutover_status.json")


def test_current_binding_surfaces_are_allowed():
    for repo in (
        "D1traverser-debug/video-growth-agent",
        "D1traverser-debug/financial-writing-agent",
        "D1traverser-debug/a-share-event-driven-agent",
        "D1traverser-debug/novel-writing-agent",
    ):
        assert POLICY.is_allowed(repo, "UAOS_SKILL.md")
        assert POLICY.is_allowed(repo, ".uaos/MANIFEST.json")
        assert POLICY.is_allowed(repo, ".uaos/ADAPTER.json")
        assert POLICY.is_allowed(repo, ".uaos/CAPABILITIES.json")


def test_normal_business_evidence_remains_retrievable():
    assert POLICY.is_allowed("D1traverser-debug/video-growth-agent", "projects/ai-self-media-commercialization/PROJECT_MANIFEST.json")
    assert POLICY.is_allowed("D1traverser-debug/novel-writing-agent", "projects/FQ001_MINGRI_ORDER/checkpoints/CURRENT_CHECKPOINT.json")
    assert POLICY.is_allowed("D1traverser-debug/financial-writing-agent", "workspaces/articles/example/STATE.json")
