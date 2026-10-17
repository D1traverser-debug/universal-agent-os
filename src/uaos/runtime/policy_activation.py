from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PolicyActivationViolation(ValueError):
    pass


class PolicyActivationState(StrEnum):
    ACTIVE_EXECUTION_POLICY = "ACTIVE_EXECUTION_POLICY"
    AUTHORIZED_NOT_PRODUCTION_ACTIVE = "AUTHORIZED_NOT_PRODUCTION_ACTIVE"


REF_CONDITIONAL_POLICY_STATUS = "REF_CONDITIONAL__RESOLVE_EFFECTIVE_STATUS"


@dataclass(frozen=True, slots=True)
class ProductionRefIdentity:
    repository: str
    ref: str

    def __post_init__(self) -> None:
        if not isinstance(self.repository, str) or not self.repository.strip():
            raise PolicyActivationViolation("production repository identity is required")
        if not isinstance(self.ref, str) or not self.ref.strip():
            raise PolicyActivationViolation("production ref identity is required")


def _normalize_ref(ref: str) -> str:
    if not isinstance(ref, str) or not ref.strip():
        raise PolicyActivationViolation("trusted current ref identity is required")
    value = ref.strip()
    if value.startswith("refs/heads/"):
        return value[len("refs/heads/") :]
    return value


def resolve_ref_conditioned_policy_activation(
    *,
    declared_status: str,
    current_repository: str,
    current_ref: str,
    production_identity: ProductionRefIdentity,
) -> PolicyActivationState:
    """Resolve one authorized policy's effective state from trusted repository/ref identity.

    The committed policy does not mutate itself after merge. Instead, the same validated
    tree is explicitly ref-conditional: it is non-active on candidate refs and becomes
    active exactly when that tree is reachable as the configured production ref. Callers
    must supply repository/ref identity from the host/VCS boundary; model/request text is
    not a trusted source for these values.
    """

    if declared_status != REF_CONDITIONAL_POLICY_STATUS:
        raise PolicyActivationViolation(
            "policy is not declared for ref-conditioned activation"
        )
    if not isinstance(current_repository, str) or not current_repository.strip():
        raise PolicyActivationViolation("trusted current repository identity is required")

    current_repo = current_repository.strip()
    current_branch = _normalize_ref(current_ref)
    production_branch = _normalize_ref(production_identity.ref)

    if (
        current_repo == production_identity.repository.strip()
        and current_branch == production_branch
    ):
        return PolicyActivationState.ACTIVE_EXECUTION_POLICY
    return PolicyActivationState.AUTHORIZED_NOT_PRODUCTION_ACTIVE


def require_active_ref_conditioned_policy(**kwargs: object) -> PolicyActivationState:
    state = resolve_ref_conditioned_policy_activation(**kwargs)  # type: ignore[arg-type]
    if state is not PolicyActivationState.ACTIVE_EXECUTION_POLICY:
        raise PolicyActivationViolation(
            f"policy is not active on the current repository/ref: {state.value}"
        )
    return state
