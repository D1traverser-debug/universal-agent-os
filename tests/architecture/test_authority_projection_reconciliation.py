import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_current_system_is_declared_derived_projection_not_policy_owner():
    current = _json("CURRENT_SYSTEM.json")
    projection = _json("config/AUTHORITY_PROJECTION_POLICY.json")
    assert current["projection_role"] == "DERIVED_OPERATIONAL_PROJECTION__NOT_POLICY_OWNER"
    assert current["authority_projection_policy"] == "config/AUTHORITY_PROJECTION_POLICY.json"
    assert projection["derived_projections"]["CURRENT_SYSTEM.json"]["role"] == current["projection_role"]


def test_current_system_projection_is_not_older_than_semantic_owners():
    current = _json("CURRENT_SYSTEM.json")
    projection = _json("config/AUTHORITY_PROJECTION_POLICY.json")
    current_updated = _instant(current["updated_at"])
    owner_updates = []
    for path in projection["semantic_owners"].values():
        owner = _json(path)
        if "updated_at" in owner:
            owner_updates.append((path, _instant(owner["updated_at"])))
    stale = [(path, timestamp.isoformat()) for path, timestamp in owner_updates if timestamp > current_updated]
    assert not stale, f"CURRENT_SYSTEM projection is stale relative to semantic owners: {stale}"


def test_system_map_points_to_current_semantic_and_runtime_owners():
    system_map = _json("config/SYSTEM_MAP.json")
    controller = system_map["controller"]
    projection = _json("config/AUTHORITY_PROJECTION_POLICY.json")
    assert controller["authority_projection_policy"] == "config/AUTHORITY_PROJECTION_POLICY.json"
    assert controller["system_state_role"] == "DERIVED_OPERATIONAL_PROJECTION__NOT_POLICY_OWNER"
    assert controller["deliberation_policy"] == projection["semantic_owners"]["cognition"]
    assert controller["architecture_experience_policy"] == projection["semantic_owners"]["architecture_experience"]
    assert controller["host_profiles"] == projection["semantic_owners"]["host_enforcement"]
    assert controller["session_interaction_policy"] == projection["semantic_owners"]["session_interaction"]
    assert controller["runtime_finalization_gate"] == "src/uaos/runtime/finalization.py"
    assert controller["openai_agents_output_guardrail"] == "src/uaos/execution/openai_agents.py#build_uaos_output_guardrail"


def test_bootstrap_projection_exposes_finalization_boundary_without_claiming_native_chatgpt_hook():
    current = _json("CURRENT_SYSTEM.json")
    bootstrap = current["fresh_chat_bootstrap"]
    assert "UAOS_CONTROLLED_RUNTIME_FAIL_CLOSED" in bootstrap["finalization_gate"]
    assert "NATIVE_CHATGPT_PRE_SEND_HOOK_UNVERIFIED" in bootstrap["finalization_gate"]
    assert "NATIVE_CHATGPT_COMPLETE_MEDIATION_NOT_CLAIMED" in current["physical_complete_mediation_assurance"]
