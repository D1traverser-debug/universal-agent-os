from pathlib import Path

import pytest

from uaos.integrations import AgentLinkRegistry, MigrationDisposition

ROOT = Path(__file__).resolve().parents[2]


def registry() -> AgentLinkRegistry:
    return AgentLinkRegistry.from_paths(ROOT / "config" / "AGENT_REGISTRY.json", ROOT / "state" / "TASK_INDEX.json")


def test_all_four_business_agents_are_registered_to_uaos():
    r = registry()
    assert {a.agent_id for a in r.agents} == {"financial_writing", "ashare", "novel", "video"}
    assert all(a.new_task_mode == "UAOS_NATIVE" for a in r.agents)
    assert all(a.legacy_resume_mode == "LAZY_IMPORT_THEN_UAOS_WRITE_ONLY" for a in r.agents)


def test_old_controller_is_not_an_agent_authority():
    r = registry()
    assert all(a.repository != "D1traverser-debug/universal-continuity-agent" for a in r.agents)


def test_aliases_resolve_business_agents_and_tasks():
    r = registry()
    assert r.resolve_agent("NOVEL_OS").agent_id == "novel"
    assert r.resolve_agent("A_SHARE_MARKET_AGENT").agent_id == "ashare"
    assert r.resolve_task("小说系统").task_id == "FQ001_MINGRI_ORDER"
    assert r.resolve_task("视频系统").task_id == "video-growth:main"


def test_past_ashare_premarket_task_cannot_auto_resume():
    r = registry()
    task = r.resolve_task("ashare:2026-10-12")
    assert task.migration_disposition is MigrationDisposition.HISTORICAL_STALE_REQUIRES_RECONCILIATION
    assert r.migration_action(task.task_id, already_imported=False) == "RECONCILE_BEFORE_IMPORT"


def test_novel_and_video_use_lazy_one_way_import():
    r = registry()
    for task_id in ("FQ001_MINGRI_ORDER", "video-growth:main"):
        assert r.migration_action(task_id, already_imported=False) == "READ_LEGACY_SOURCE_ONCE__IMPORT__THEN_UAOS_WRITE_ONLY"
        assert r.migration_action(task_id, already_imported=True) == "RESUME_UAOS"


def test_unknown_agent_and_task_fail_closed():
    r = registry()
    with pytest.raises(LookupError):
        r.resolve_agent("unknown")
    with pytest.raises(LookupError):
        r.resolve_task("unknown")
