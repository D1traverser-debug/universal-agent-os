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


def test_active_registry_has_no_legacy_protocol_or_task_index_refs():
    r = registry()
    assert all(a.legacy_protocol_ref is None for a in r.agents)
    assert all(a.task_index_ref is None for a in r.agents)


def test_active_tasks_are_uaos_native_and_have_state_refs():
    r = registry()
    assert r.tasks
    assert all(t.migration_disposition is MigrationDisposition.UAOS_NATIVE for t in r.tasks)
    assert all(t.state_ref for t in r.tasks)
    assert all(not t.legacy_source_refs for t in r.tasks)


def test_old_ashare_market_day_is_not_active_candidate():
    r = registry()
    with pytest.raises(LookupError):
        r.resolve_task("ashare:2026-10-12")


def test_video_current_project_is_default_and_old_program_is_explicit_only():
    r = registry()
    candidates = {t.task_id: t for t in r.tasks if t.domain_id == "video"}
    assert candidates["video:ai-self-media-commercialization"].default_resume_within_domain is True
    assert candidates["video-growth:main"].default_resume_within_domain is False


def test_unknown_agent_and_task_fail_closed():
    r = registry()
    with pytest.raises(LookupError):
        r.resolve_agent("unknown")
    with pytest.raises(LookupError):
        r.resolve_task("unknown")
