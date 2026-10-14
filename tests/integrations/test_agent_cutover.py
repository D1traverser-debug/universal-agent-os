import json
from pathlib import Path

import pytest

from uaos.integrations import AgentLinkRegistry

ROOT = Path(__file__).resolve().parents[2]


def registry() -> AgentLinkRegistry:
    return AgentLinkRegistry.from_paths(ROOT / "config" / "AGENT_REGISTRY.json", ROOT / "state" / "TASK_INDEX.json")


def test_all_four_business_agents_use_current_uaos_binding_namespace():
    r = registry()
    assert {a.agent_id for a in r.agents} == {"financial_writing", "ashare", "novel", "video"}
    for agent in r.agents:
        assert agent.new_task_mode == "UAOS_NATIVE"
        assert agent.skill_ref == "UAOS_SKILL.md"
        assert agent.agent_manifest_ref == ".uaos/MANIFEST.json"
        assert agent.capability_ref == ".uaos/CAPABILITIES.json"
        assert agent.uaos_adapter_ref == ".uaos/ADAPTER.json"
        assert "continuity/" not in json.dumps(agent.__dict__ if hasattr(agent, "__dict__") else {
            "skill_ref": agent.skill_ref,
            "agent_manifest_ref": agent.agent_manifest_ref,
            "capability_ref": agent.capability_ref,
            "uaos_adapter_ref": agent.uaos_adapter_ref,
        })


def test_old_controller_is_not_an_agent_authority():
    assert all(a.repository != "D1traverser-debug/universal-continuity-agent" for a in registry().agents)


def test_aliases_resolve_current_agents_and_tasks():
    r = registry()
    assert r.resolve_agent("NOVEL_OS").agent_id == "novel"
    assert r.resolve_agent("A_SHARE_MARKET_AGENT").agent_id == "ashare"
    assert r.resolve_task("小说系统").task_id == "FQ001_MINGRI_ORDER"
    assert r.resolve_task("原创数字IP设计").task_id == "video:ai-self-media-commercialization"


def test_video_default_is_current_digital_ip_not_old_program():
    r = registry()
    defaults = [task for task in r.tasks if task.domain_id == "video" and task.default_resume_within_domain]
    assert [task.task_id for task in defaults] == ["video:ai-self-media-commercialization"]
    old = r.resolve_task("video-growth:main")
    assert old.default_resume_within_domain is False


def test_unknown_agent_and_task_fail_closed():
    r = registry()
    with pytest.raises(LookupError):
        r.resolve_agent("unknown")
    with pytest.raises(LookupError):
        r.resolve_task("unknown")
