from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PolicyActivationViolation(ValueError):
    pass


class PolicyActivationState(StrEnum):
    ACTIVE_EXECUTION_POLICY = "ACTIVE_EXECUTION_POLICY"
    AUTHORIZED_NOT_PRODUCTION_ACTIVE = "AUTHORIZED_NOT_PRODUCTION_ACTIVE"


REF_CONDITIONAL_POLICY_STATUS = "REF_CONDITIONAL__RESOLVE_EFFECTIVE_STATUS"
UAOS_PRODUCTION_REPOSITORY = "D1traverser-debug/universal-agent-os"
UAOS_PRODUCTION_REF = "refs/heads/main"


@dataclass(frozen=True, slots=True)
class ProductionRefIdentity:
    repository: str
    ref: str

    def __post_init__(self) -> None:
        if not isinstance(self.repository, str) or not self.repository.strip():
            raise PolicyActivationViolation("production repository identity is required")
        if not isinstance(self.ref, str) or not self.ref.strip():
            raise PolicyActivationViolation("production ref identity is required")
        repository = self.repository.strip()
        ref = self.ref.strip()
        if not ref.startswith("refs/heads/") or ref == "refs/heads/":
            raise PolicyActivationViolation(
                "production ref identity must be a fully qualified non-empty branch ref"
            )
        if repository != UAOS_PRODUCTION_REPOSITORY or ref != UAOS_PRODUCTION_REF:
            raise PolicyActivationViolation(
                "production identity does not match the pinned UAOS production authority"
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
    """Resolve effective state against the pinned trusted UAOS production authority.

    Activation requires the exact repository plus fully qualified branch identity
    ``D1traverser-debug/universal-agent-os`` + ``refs/heads/main``. Short refs, tags,
    pull refs, alternate repositories/branches, and malformed or misloaded production
    identities fail closed. Model/request text is never sufficient identity evidence.
    """

    if declared_status != REF_CONDITIONAL_POLICY_STATUS:
        raise PolicyActivationViolation(
            "policy is not declared for ref-conditioned activation"
        )
    if not isinstance(current_repository, str) or not current_repository.strip():
        raise PolicyActivationViolation("trusted current repository identity is required")

    # Revalidate at the decision point even though ProductionRefIdentity validates on
    # construction; callers may deserialize/reconstruct objects through unusual paths.
    if (
        production_identity.repository.strip() != UAOS_PRODUCTION_REPOSITORY
        or production_identity.ref.strip() != UAOS_PRODUCTION_REF
    ):
        raise PolicyActivationViolation(
            "production identity does not match the pinned UAOS production authority"
        )

    current_repo = current_repository.strip()
    trusted_current_ref = _require_current_ref(current_ref)

    if (
        current_repo == UAOS_PRODUCTION_REPOSITORY
        and trusted_current_ref == UAOS_PRODUCTION_REF
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
