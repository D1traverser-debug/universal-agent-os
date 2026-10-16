import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def test_common_contract_declares_domain_internal_orchestration():
    common = load("config/COMMON_CAPABILITIES.json")
    assert _version_tuple(common["contract_version"]) >= (1, 7, 0)
    capabilities = {item["capability_id"]: item for item in common["capabilities"]}
    orchestration = capabilities["domain_internal_work_orchestration"]
    assert "DOMAIN_OWNER_FOR_INTERNAL_TASK_GRAPH_BUSINESS_STATE_AND_DECISIONS" in orchestration["owner"]
    assert {
        "SERIAL_DEPENDENCY",
        "INDEPENDENT_PARALLEL",
        "FAN_OUT_FAN_IN",
        "CONSULTATIVE_ADVICE",
        "COMPETITIVE_CANDIDATES",
        "STRUCTURED_CRITIQUE_AND_REVISION",
        "OWNER_ADJUDICATION",
        "QUORUM_OR_PANEL_REVIEW",
    } <= set(orchestration["patterns"])
    rules = " ".join(orchestration["rules"]).lower()
    assert "acyclic" in rules
    assert "unbounded peer chat" in rules
    assert "adjudicator" in rules
    assert "uaos" in rules and "must not mirror" in rules


def test_common_contract_routes_governed_evolution_through_one_transaction():
    common = load("config/COMMON_CAPABILITIES.json")
    capabilities = {item["capability_id"]: item for item in common["capabilities"]}
    evolution = capabilities["governed_self_evolution"]
    assert evolution["policy_ref"] == "config/EVOLUTION_POLICY.json"
    assert "EvolutionTransaction" in evolution["canonical_executable_ref"]
    lifecycle = evolution["lifecycle"]
    assert "CAPABILITY_GAP" in lifecycle
    rules = " ".join(evolution["rules"])
    assert "one canonical EvolutionTransaction" in rules
    assert "external/independent judge" in rules


def test_v2_requirements_are_current_and_preserve_child_business_identity():
    current = load("CURRENT_SYSTEM.json")
    assert _version_tuple(current["system_release_version"]) >= (2, 5, 0)
    assert "docs/requirements/FROZEN_REQUIREMENTS_v2.0.md" in current["requirements"]
    text = (ROOT / "docs/requirements/FROZEN_REQUIREMENTS_v2.0.md").read_text(encoding="utf-8")
    assert "Independent parallel work" in text or "independent parallel work" in text
    assert "structured, not unbounded peer chat" in text
    assert "parent router/task IDs and child project/program/workstream IDs" in text
    assert "must not mirror child project/program/workstream/subtask identities" in text


def test_parent_common_contract_forbids_child_work_graph_mirroring():
    common = load("config/COMMON_CAPABILITIES.json")
    anti = " ".join(common["anti_duplication"]).lower()
    assert "project/program/workstream/subtask identities" in anti
    assert "opaque child references" in anti
