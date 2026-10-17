import json
from pathlib import Path

from uaos.runtime import (
    REF_CONDITIONAL_POLICY_STATUS,
    PolicyActivationState,
    ProductionRefIdentity,
    resolve_ref_conditioned_policy_activation,
)

ROOT = Path(__file__).resolve().parents[2]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_policy_projection_and_evolution_share_one_ref_conditioned_activation_owner():
    policy = load("config/PERSISTENT_ASSET_POLICY.json")
    current = load("CURRENT_SYSTEM.json")
    evolution = load("state/evolution/EVO-20261017-PERSISTENT-ASSET-GOVERNANCE.json")

    resolver = "src/uaos/runtime/policy_activation.py#resolve_ref_conditioned_policy_activation"
    assert policy["status"] == REF_CONDITIONAL_POLICY_STATUS
    assert policy["activation"]["resolver_ref"] == resolver
    assert current["runtime"]["persistent_asset_policy_activation"] == resolver
    assert evolution["activation_resolver_ref"] == resolver

    expected_identity = {
        "repository": policy["activation"]["production_repository"],
        "ref": policy["activation"]["production_ref"],
    }
    assert evolution["production_identity"] == expected_identity
    assert policy["activation"]["production_effective_status"] == "ACTIVE_EXECUTION_POLICY"
    assert policy["activation"]["non_production_effective_status"] == "AUTHORIZED_NOT_PRODUCTION_ACTIVE"
    assert "EFFECTIVE_PROMOTION_RESOLVED_BY_PRODUCTION_REF" in evolution["status"]
    assert "CANDIDATE_AUTHORIZED_FOR_PROMOTION" not in current["assurance"]["persistent_assets"]


def test_same_authorized_tree_is_inactive_on_candidate_and_active_on_parent_main():
    policy = load("config/PERSISTENT_ASSET_POLICY.json")
    production = ProductionRefIdentity(
        policy["activation"]["production_repository"],
        policy["activation"]["production_ref"],
    )
    candidate = resolve_ref_conditioned_policy_activation(
        declared_status=policy["status"],
        current_repository=production.repository,
        current_ref="refs/heads/maintenance/persistent-asset-governance-20261017",
        production_identity=production,
    )
    main = resolve_ref_conditioned_policy_activation(
        declared_status=policy["status"],
        current_repository=production.repository,
        current_ref=production.ref,
        production_identity=production,
    )
    assert candidate is PolicyActivationState.AUTHORIZED_NOT_PRODUCTION_ACTIVE
    assert main is PolicyActivationState.ACTIVE_EXECUTION_POLICY
