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
        if not self.ref.strip().startswith("refs/heads/"):
            raise PolicyActivationViolation(
                "production ref identity must be a fully qualified branch ref"
            )


def _require_current_ref(ref: str) -> str:
    if not isinstance(ref, str) or not ref.strip():
        raise PolicyActivationViolation("trusted current ref identity is required")
    return ref.strip()


def resolve_ref_conditioned_policy_activation(
    *,
    declared_status: str,
    current_repository: str,
    current_ref: str,
    production_identity: ProductionRefIdentity,
) -> PolicyActivationState:
    """Resolve one authorized policy's effective state from trusted repository/ref identity.

    Activation requires the exact fully qualified production branch ref. Short names such
    as ``main`` are deliberately non-active because they do not identify ref type and can
    be ambiguous with a tag of the same name. The host/VCS boundary must therefore supply
    a trusted ``refs/heads/...`` identity; model/request text is never sufficient.
    """

    if declared_status != REF_CONDITIONAL_POLICY_STATUS:
        raise PolicyActivationViolation(
            "policy is not declared for ref-conditioned activation"
        )
    if not isinstance(current_repository, str) or not current_repository.strip():
        raise PolicyActivationViolation("trusted current repository identity is required")

    current_repo = current_repository.strip()
    trusted_current_ref = _require_current_ref(current_ref)
    production_ref = production_identity.ref.strip()

    if (
        current_repo == production_identity.repository.strip()
        and trusted_current_ref.startswith("refs/heads/")
        and trusted_current_ref == production_ref
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
