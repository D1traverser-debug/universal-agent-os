import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = "D1traverser-debug/universal-continuity-agent"


def test_hot_bootstrap_has_no_old_controller_literal():
    for rel in ("ENTRYPOINT.md", "README.md", "AGENTS.md", "CURRENT_SYSTEM.json", "config/AGENT_REGISTRY.json", "state/TASK_INDEX.json"):
        assert OLD not in (ROOT / rel).read_text(encoding="utf-8"), rel


def test_registry_and_task_index_have_no_legacy_refs():
    registry = json.loads((ROOT / "config/AGENT_REGISTRY.json").read_text(encoding="utf-8"))
    tasks = json.loads((ROOT / "state/TASK_INDEX.json").read_text(encoding="utf-8"))
    for agent in registry["agents"]:
        assert "legacy_protocol_ref" not in agent
        assert "task_index_ref" not in agent
        assert agent["agent_manifest_ref"] == "continuity/UAOS_MANIFEST.json"
    for task in tasks["tasks"]:
        assert "legacy_source_refs" not in task
        assert task["state_model"] == "UAOS_NATIVE"


def test_cutover_evidence_is_not_active_state():
    assert not (ROOT / "state" / "CUTOVER_STATUS.json").exists()
    assert (ROOT / "docs" / "migration" / "CUTOVER_EVIDENCE_2026-10-14.json").exists()


def test_custom_instruction_doc_is_pointer_only():
    text = (ROOT / "docs" / "integration" / "CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")
    assert "universal-agent-os@main:ENTRYPOINT.md" in text
    assert "does not depend" in text
