import pytest

from uaos.execution import AuthorityScopeGate, AuthorityScopeViolation, ExecutionRequest


def request(*, side_effect_class="WRITE", target_authority=None):
    return ExecutionRequest(
        "a1",
        "write",
        "repo:file",
        {},
        side_effect_class=side_effect_class,
        target_authority=target_authority,
    )


def test_cross_scope_read_is_not_blocked_by_write_authority_gate():
    AuthorityScopeGate().require(
        request(side_effect_class="READ", target_authority="UAOS"),
        active_authority="DOMAIN:video",
    )


def test_mutation_without_selected_authority_fails_closed():
    with pytest.raises(AuthorityScopeViolation, match="selected authority context"):
        AuthorityScopeGate().require(
            request(target_authority="UAOS"), active_authority=None
        )


def test_mutation_without_target_authority_fails_closed():
    with pytest.raises(AuthorityScopeViolation, match="target_authority"):
        AuthorityScopeGate().require(request(), active_authority="UAOS")


def test_child_cannot_mutate_parent_uaos():
    with pytest.raises(AuthorityScopeViolation, match="cross-authority mutation"):
        AuthorityScopeGate().require(
            request(target_authority="UAOS"), active_authority="DOMAIN:video"
        )


def test_child_cannot_mutate_sibling_domain():
    with pytest.raises(AuthorityScopeViolation, match="cross-authority mutation"):
        AuthorityScopeGate().require(
            request(target_authority="DOMAIN:financial_writing"),
            active_authority="DOMAIN:video",
        )


def test_controller_cannot_impersonate_domain_owner_for_direct_business_write():
    with pytest.raises(AuthorityScopeViolation, match="cross-authority mutation"):
        AuthorityScopeGate().require(
            request(target_authority="DOMAIN:video"), active_authority="UAOS"
        )


def test_uaos_can_mutate_uaos_authority():
    AuthorityScopeGate().require(
        request(target_authority="UAOS"), active_authority="UAOS"
    )


def test_domain_can_mutate_its_own_authority():
    AuthorityScopeGate().require(
        request(target_authority="DOMAIN:video"), active_authority="DOMAIN:video"
    )
