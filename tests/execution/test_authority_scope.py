import pytest

from uaos.execution import AuthorityScopeGate, AuthorityScopeViolation, ExecutionRequest


PARENTS={
    "DOMAIN:financial_writing":"UAOS",
    "DOMAIN:video":"UAOS",
    "DOMAIN:ashare":"UAOS",
    "DOMAIN:novel":"UAOS",
}


def request(*, side_effect_class="WRITE", target_authority=None, governance_basis=None):
    return ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {},
        side_effect_class=side_effect_class,
        target_authority=target_authority,
        governance_basis=governance_basis,
    )


def gate():
    return AuthorityScopeGate(PARENTS)


def test_cross_scope_read_is_not_blocked_by_write_authority_gate():
    gate().require(
        request(side_effect_class="READ", target_authority="UAOS"),
        active_authority="DOMAIN:video",
    )


def test_mutation_without_selected_authority_fails_closed():
    with pytest.raises(AuthorityScopeViolation, match="selected authority context"):
        gate().require(request(target_authority="UAOS"), active_authority=None)


def test_mutation_without_target_authority_fails_closed():
    with pytest.raises(AuthorityScopeViolation, match="target_authority"):
        gate().require(request(), active_authority="UAOS")


def test_child_cannot_mutate_parent_uaos():
    with pytest.raises(AuthorityScopeViolation, match="cross-authority mutation"):
        gate().require(request(target_authority="UAOS"), active_authority="DOMAIN:video")


def test_child_cannot_mutate_sibling_domain():
    with pytest.raises(AuthorityScopeViolation, match="cross-authority mutation"):
        gate().require(
            request(target_authority="DOMAIN:financial_writing"),
            active_authority="DOMAIN:video",
        )


def test_parent_can_govern_registered_descendant_with_explicit_basis():
    gate().require(
        request(target_authority="DOMAIN:video", governance_basis="SYSTEM_GOVERNANCE"),
        active_authority="UAOS",
    )


def test_parent_descendant_mutation_without_basis_fails_closed():
    with pytest.raises(AuthorityScopeViolation, match="governance_basis"):
        gate().require(request(target_authority="DOMAIN:video"), active_authority="UAOS")


def test_parent_cannot_write_unregistered_peer_like_target():
    with pytest.raises(AuthorityScopeViolation, match="cross-authority mutation"):
        gate().require(
            request(target_authority="DOMAIN:unknown", governance_basis="SYSTEM_GOVERNANCE"),
            active_authority="UAOS",
        )


def test_uaos_can_mutate_uaos_authority():
    gate().require(request(target_authority="UAOS"), active_authority="UAOS")


def test_domain_can_mutate_its_own_authority():
    gate().require(
        request(target_authority="DOMAIN:video"), active_authority="DOMAIN:video"
    )
