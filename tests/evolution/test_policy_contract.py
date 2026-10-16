import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_all_parent_authorities_point_to_one_evolution_transaction():
    policy = load("config/EVOLUTION_POLICY.json")
    system_map = load("config/SYSTEM_MAP.json")
    current = load("CURRENT_SYSTEM.json")
    common = load("config/COMMON_CAPABILITIES.json")

    canonical = "src/uaos/evolution/transaction.py#EvolutionTransaction"
    assert policy["canonical_executable"] == "src/uaos/evolution/transaction.py"
    assert policy["canonical_transaction"] == "EvolutionTransaction"
    assert system_map["controller"]["evolution_policy"] == "config/EVOLUTION_POLICY.json"
    assert system_map["controller"]["canonical_evolution_transaction"] == canonical
    assert current["owners"]["evolution_policy"] == "config/EVOLUTION_POLICY.json"
    assert current["runtime"]["evolution_transaction"] == canonical

    capabilities = {item["capability_id"]: item for item in common["capabilities"]}
    evolution = capabilities["governed_self_evolution"]
    assert evolution["policy_ref"] == "config/EVOLUTION_POLICY.json"
    assert evolution["canonical_executable_ref"] == canonical


def test_capability_gap_is_first_class_and_not_incident_disguise():
    policy = load("config/EVOLUTION_POLICY.json")
    origins = policy["origin_kinds"]
    assert {"INCIDENT", "CAPABILITY_GAP", "EVALUATED_KNOWLEDGE"} <= set(origins)
    invariants = " ".join(policy["transaction_invariants"])
    assert "capability_gap_ids" in invariants
    assert "first-class" in origins["CAPABILITY_GAP"].lower() or "without fabricating an incident" in origins["CAPABILITY_GAP"].lower()


def test_proactive_depth_contract_requires_real_evidence_and_judge():
    policy = load("config/EVOLUTION_POLICY.json")
    depth = " ".join(policy["height_breadth_depth_admission"]["depth"]).lower()
    assert "raw evidence" in depth
    assert "professional methods/tools" in depth
    assert "novelty/unknown-signal" in depth
    assert "external or independent judge" in depth
    assert "feasibility evidence" in depth


def test_chatgpt_host_does_not_fake_background_execution():
    hosts = load("config/HOST_PROFILES.json")
    chatgpt = hosts["profiles"]["CHATGPT_GITHUB"]
    assert "WHEN_CONFIGURED" in chatgpt["proactive_evolution_trigger"]
    assert "ONLY_WHEN" in chatgpt["background_execution"]
    assert "NO_VERIFIED_CHATGPT_PRE_SEND_HOOK" in chatgpt["final_response_enforcement"]
