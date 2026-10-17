import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_authority_write_policy_mechanically_routes_mutations_through_asset_gate():
    policy = load("config/AUTHORITY_WRITE_POLICY.json")
    assert policy["persistent_asset_policy"] == "config/PERSISTENT_ASSET_POLICY.json"
    assert policy["persistent_asset_executable"].endswith("#PersistentAssetGate")
    checks = set(policy["always_on_mutation_sentinel"]["checks"])
    assert {
        "TARGET_PERSISTENT_SURFACE",
        "TARGET_ASSET_ROLE",
        "TARGET_ASSET_LIFECYCLE",
        "ASSET_OWNER_AUTHORITY",
        "PERSISTENT_ASSET_OPERATION_ADMISSION",
    } <= checks


def test_existing_common_mutation_capability_inherits_asset_policy_transitively():
    common = load("config/COMMON_CAPABILITIES.json")
    mutation = next(
        item for item in common["capabilities"]
        if item["capability_id"] == "mutation_sentinel_and_host_complete_mediation"
    )
    assert mutation["policy_ref"] == "config/AUTHORITY_WRITE_POLICY.json"
    authority = load(mutation["policy_ref"])
    assert authority["persistent_asset_policy"] == "config/PERSISTENT_ASSET_POLICY.json"


def test_persistent_asset_policy_does_not_claim_native_chatgpt_physical_mediation():
    policy = load("config/PERSISTENT_ASSET_POLICY.json")
    assert "NO_REPOSITORY_CONTROLLED_PHYSICAL_INTERCEPTION" in policy["native_chatgpt_boundary"]
    assert policy["role_constraints"]["BOOTSTRAP"]["forbidden_as_business_authority"] is True
    assert policy["role_constraints"]["DELIVERY_HISTORY"]["forbidden_as_business_authority"] is True
