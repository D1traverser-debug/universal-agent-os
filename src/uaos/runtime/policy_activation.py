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


def _exact_nonempty_str(value: object, *, field: str) -> str:
    """Accept host/VCS identity only as an exact builtin string.

    Identity values are a trust boundary. A ``str`` subclass may override ``strip`` or
    comparison methods, so accepting ``isinstance(value, str)`` would let the object
    execute caller-defined normalization while policy activation is being decided.
    """

    if type(value) is not str:
        raise PolicyActivationViolation(f"{field} must be an exact builtin string")
    stripped = value.strip()
    if not stripped:
        raise PolicyActivationViolation(f"{field} is required")
    return stripped


@dataclass(frozen=True, slots=True)
class ProductionRefIdentity:
    repository: str
    ref: str

    def __post_init__(self) -> None:
        repository = _exact_nonempty_str(
            self.repository,
            field="production repository identity",
        )
        ref = _exact_nonempty_str(self.ref, field="production ref identity")
        if not ref.startswith("refs/heads/") or ref == "refs/heads/":
            raise PolicyActivationViolation(
                "production ref identity must be a fully qualified non-empty branch ref"
            )
        if repository != UAOS_PRODUCTION_REPOSITORY or ref != UAOS_PRODUCTION_REF:
            raise PolicyActivationViolation(
                "production identity does not match the pinned UAOS production authority"
            )
        object.__setattr__(self, "repository", repository)
        object.__setattr__(self, "ref", ref)


def _require_current_ref(ref: object) -> str:
    value = _exact_nonempty_str(ref, field="trusted current ref identity")
    if not value.startswith("refs/heads/") or value == "refs/heads/":
        raise PolicyActivationViolation(
            "trusted current ref identity must be a fully qualified non-empty branch ref"
        )
    return value


def resolve_ref_conditioned_policy_activation(
    *,
    declared_status: str,
    current_repository: str,
    current_ref: str,
    production_identity: ProductionRefIdentity,
) -> PolicyActivationState:
    """Resolve effective state against the pinned trusted UAOS production authority.

    Activation requires exact builtin-string identities for the repository and fully
    qualified branch ref. Short refs, tags, subclasses with custom normalization,
    alternate repositories/branches, and malformed/misloaded production identities
    fail closed. Model/request text is never sufficient identity evidence.
    """

    status = _exact_nonempty_str(declared_status, field="declared policy status")
    if status != REF_CONDITIONAL_POLICY_STATUS:
        raise PolicyActivationViolation(
            "policy is not declared for ref-conditioned activation"
        )
    current_repo = _exact_nonempty_str(
        current_repository,
        field="trusted current repository identity",
    )
    trusted_current_ref = _require_current_ref(current_ref)

    if type(production_identity) is not ProductionRefIdentity:
        raise PolicyActivationViolation("production identity must use the canonical value type")
    # Revalidate exact builtin values even if a caller attempted object.__setattr__ after
    # construction. Never dispatch subclass methods while making the activation decision.
    production_repo = _exact_nonempty_str(
        object.__getattribute__(production_identity, "repository"),
        field="production repository identity",
    )
    production_ref = _exact_nonempty_str(
        object.__getattribute__(production_identity, "ref"),
        field="production ref identity",
    )
    if (
        production_repo != UAOS_PRODUCTION_REPOSITORY
        or production_ref != UAOS_PRODUCTION_REF
    ):
        raise PolicyActivationViolation(
            "production identity does not match the pinned UAOS production authority"
        )

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
