from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .models import ExecutionRequest


class AuthorityScopeViolation(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class AuthorityScopeGate:
    """Fail-closed hierarchical ownership boundary for authoritative mutation.

    Same-owner mutation is allowed. A registered ancestor may govern a descendant only
    when the request carries an explicit governance basis. Upward and sibling mutation
    remain blocked. Reads/non-side-effect work remain outside this write gate.
    """

    authority_parents: Mapping[str, str] = field(default_factory=dict)
    non_mutating_side_effects: frozenset[str] = frozenset({"NONE", "READ"})

    @classmethod
    def for_registered_domains(cls, domain_ids: tuple[str, ...]) -> "AuthorityScopeGate":
        return cls({f"DOMAIN:{domain_id}": "UAOS" for domain_id in domain_ids})

    def _is_ancestor(self, ancestor: str, target: str) -> bool:
        current = target
        seen: set[str] = set()
        while current in self.authority_parents:
            if current in seen:
                raise AuthorityScopeViolation("authority hierarchy cycle detected")
            seen.add(current)
            parent = self.authority_parents[current]
            if parent == ancestor:
                return True
            current = parent
        return False

    def require(self, request: ExecutionRequest, *, active_authority: str | None) -> None:
        if request.side_effect_class.upper() in self.non_mutating_side_effects:
            return
        if active_authority is None or not active_authority.strip():
            raise AuthorityScopeViolation("mutating action requires selected authority context")
        if request.target_authority is None or not request.target_authority.strip():
            raise AuthorityScopeViolation(
                f"mutating action={request.action_id} requires target_authority"
            )
        if active_authority == request.target_authority:
            return
        if self._is_ancestor(active_authority, request.target_authority):
            if request.governance_basis is None or not request.governance_basis.strip():
                raise AuthorityScopeViolation(
                    "ancestor-to-descendant mutation requires explicit governance_basis"
                )
            return
        raise AuthorityScopeViolation(
            "cross-authority mutation blocked: "
            f"active={active_authority}, target={request.target_authority}; "
            "child-to-parent and sibling writes are prohibited"
        )
