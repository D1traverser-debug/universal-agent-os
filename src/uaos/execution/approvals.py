from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .models import ExecutionRequest


class ApprovalRequired(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class ApprovalGrant:
    approval_id: str
    action_id: str
    target: str
    parameter_hash: str
    expires_at: datetime

    def authorizes(self, request: ExecutionRequest, now: datetime) -> bool:
        return (
            now < self.expires_at
            and self.action_id == request.action_id
            and self.target == request.target
            and self.parameter_hash == request.parameter_hash
        )


class ApprovalGate:
    def require(self, request: ExecutionRequest, grant: ApprovalGrant | None, *, now: datetime) -> None:
        if not request.approval_required:
            return
        if grant is None or not grant.authorizes(request, now):
            raise ApprovalRequired(
                f"exact approval required for action={request.action_id}, target={request.target}"
            )
