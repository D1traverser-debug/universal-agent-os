from __future__ import annotations

from dataclasses import dataclass

from .models import ExecutionRequest


class AuthorityScopeViolation(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class AuthorityScopeGate:
    """Fail-closed ownership boundary for authoritative mutation.

    Reads/non-side-effect work may cross scopes under retrieval policy. Any mutating
    action must execute inside the same authority owner as its target. Cross-scope
    changes are proposals/handoffs, not direct writes.
    """

    non_mutating_side_effects: frozenset[str] = frozenset({"NONE", "READ"})

    def require(self, request: ExecutionRequest, *, active_authority: str | None) -> None:
        if request.side_effect_class.upper() in self.non_mutating_side_effects:
            return
        if active_authority is None or not active_authority.strip():
            raise AuthorityScopeViolation("mutating action requires selected authority context")
        if request.target_authority is None or not request.target_authority.strip():
            raise AuthorityScopeViolation(
                f"mutating action={request.action_id} requires target_authority"
            )
        if active_authority != request.target_authority:
            raise AuthorityScopeViolation(
                "cross-authority mutation blocked: "
                f"active={active_authority}, target={request.target_authority}; "
                "use owner handoff/proposal instead"
            )
