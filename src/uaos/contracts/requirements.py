from __future__ import annotations

from dataclasses import replace

from .enums import RequirementState
from .models import RequirementRecord


def supersede_requirement(old: RequirementRecord, replacement: RequirementRecord) -> tuple[RequirementRecord, RequirementRecord]:
    if old.lifecycle_state is not RequirementState.ACTIVE:
        raise ValueError("only ACTIVE requirements may be superseded")
    if replacement.lifecycle_state is not RequirementState.ACTIVE:
        raise ValueError("replacement requirement must be ACTIVE")
    if old.scope_type != replacement.scope_type or old.scope_id != replacement.scope_id:
        raise ValueError("replacement must preserve scope unless a new scoped requirement is created explicitly")
    if old.requirement_id not in replacement.supersedes:
        raise ValueError("replacement must explicitly name the requirement it supersedes")
    return replace(old, lifecycle_state=RequirementState.SUPERSEDED), replacement


def cancel_requirement(requirement: RequirementRecord) -> RequirementRecord:
    if requirement.lifecycle_state is not RequirementState.ACTIVE:
        raise ValueError("only ACTIVE requirements may be cancelled")
    return replace(requirement, lifecycle_state=RequirementState.CANCELLED)
