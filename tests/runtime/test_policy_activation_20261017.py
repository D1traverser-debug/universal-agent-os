import pytest

from uaos.runtime import (
    REF_CONDITIONAL_POLICY_STATUS,
    PolicyActivationState,
    PolicyActivationViolation,
    ProductionRefIdentity,
    require_active_ref_conditioned_policy,
    resolve_ref_conditioned_policy_activation,
)


PRODUCTION = ProductionRefIdentity(
    repository="D1traverser-debug/universal-agent-os",
    ref="refs/heads/main",
)


def resolve(repository: str, ref: str):
    return resolve_ref_conditioned_policy_activation(
        declared_status=REF_CONDITIONAL_POLICY_STATUS,
        current_repository=repository,
        current_ref=ref,
        production_identity=PRODUCTION,
    )


def test_candidate_branch_is_authorized_but_not_production_active():
    assert (
        resolve(
            "D1traverser-debug/universal-agent-os",
            "refs/heads/maintenance/persistent-asset-governance-20261017",
        )
        is PolicyActivationState.AUTHORIZED_NOT_PRODUCTION_ACTIVE
    )


def test_exact_fully_qualified_production_main_identity_activates_same_authorized_tree():
    assert (
        resolve("D1traverser-debug/universal-agent-os", "refs/heads/main")
        is PolicyActivationState.ACTIVE_EXECUTION_POLICY
    )


def test_short_or_tag_main_do_not_masquerade_as_production_branch():
    assert (
        resolve("D1traverser-debug/universal-agent-os", "main")
        is PolicyActivationState.AUTHORIZED_NOT_PRODUCTION_ACTIVE
    )
    assert (
        resolve("D1traverser-debug/universal-agent-os", "refs/tags/main")
        is PolicyActivationState.AUTHORIZED_NOT_PRODUCTION_ACTIVE
    )
    assert (
        resolve("D1traverser-debug/universal-agent-os", "refs/pull/71/merge")
        is PolicyActivationState.AUTHORIZED_NOT_PRODUCTION_ACTIVE
    )


def test_other_repository_main_does_not_activate_policy():
    assert (
        resolve("D1traverser-debug/financial-writing-agent", "refs/heads/main")
        is PolicyActivationState.AUTHORIZED_NOT_PRODUCTION_ACTIVE
    )


def test_production_identity_is_pinned_to_exact_uaos_main():
    invalid = (
        ("D1traverser-debug/universal-agent-os", "main", "fully qualified"),
        ("D1traverser-debug/universal-agent-os", "refs/tags/main", "fully qualified"),
        ("D1traverser-debug/universal-agent-os", "refs/heads/", "non-empty"),
        ("evil/repo", "refs/heads/main", "pinned UAOS"),
        ("D1traverser-debug/universal-agent-os", "refs/heads/release", "pinned UAOS"),
    )
    for repository, ref, message in invalid:
        with pytest.raises(PolicyActivationViolation, match=message):
            ProductionRefIdentity(repository=repository, ref=ref)


def test_missing_or_wrong_declaration_fails_closed():
    with pytest.raises(PolicyActivationViolation, match="not declared"):
        resolve_ref_conditioned_policy_activation(
            declared_status="ACTIVE_EXECUTION_POLICY",
            current_repository="D1traverser-debug/universal-agent-os",
            current_ref="refs/heads/main",
            production_identity=PRODUCTION,
        )
    with pytest.raises(PolicyActivationViolation, match="current ref"):
        resolve_ref_conditioned_policy_activation(
            declared_status=REF_CONDITIONAL_POLICY_STATUS,
            current_repository="D1traverser-debug/universal-agent-os",
            current_ref="",
            production_identity=PRODUCTION,
        )


def test_require_active_rejects_candidate_and_short_ref_and_accepts_full_main():
    for ref in (
        "refs/heads/maintenance/persistent-asset-governance-20261017",
        "maintenance/persistent-asset-governance-20261017",
        "main",
        "refs/tags/main",
    ):
        with pytest.raises(PolicyActivationViolation, match="not active"):
            require_active_ref_conditioned_policy(
                declared_status=REF_CONDITIONAL_POLICY_STATUS,
                current_repository="D1traverser-debug/universal-agent-os",
                current_ref=ref,
                production_identity=PRODUCTION,
            )
    assert (
        require_active_ref_conditioned_policy(
            declared_status=REF_CONDITIONAL_POLICY_STATUS,
            current_repository="D1traverser-debug/universal-agent-os",
            current_ref="refs/heads/main",
            production_identity=PRODUCTION,
        )
        is PolicyActivationState.ACTIVE_EXECUTION_POLICY
    )
