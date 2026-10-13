from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from uaos.contracts.enums import IntentType, RequirementState, ScopeType, TaskStatus
from uaos.contracts.models import RequirementRecord


class ControlResolutionError(RuntimeError):
    pass


class AmbiguousControlTarget(ControlResolutionError):
    pass


@dataclass(frozen=True, slots=True)
class ControlCommand:
    intent: IntentType
    domain_hint: str | None = None
    task_id_hint: str | None = None
    task_type_hint: str | None = None


@dataclass(frozen=True, slots=True)
class TaskCandidate:
    task_id: str
    owner_domain: str
    task_type: str
    status: TaskStatus
    updated_at: datetime
    resume_eligible: bool = True
    default_resume: bool = False


@dataclass(frozen=True, slots=True)
class ControlResolution:
    mode: str
    task_id: str | None = None
    scope: str | None = None


@dataclass(frozen=True, slots=True)
class RequirementContext:
    owner_domain: str
    task_type: str
    task_id: str
    one_shot_requirement_ids: frozenset[str] = frozenset()


def _eligible(candidate: TaskCandidate) -> bool:
    return candidate.resume_eligible and candidate.status not in {TaskStatus.COMPLETE, TaskStatus.CANCELLED}


def resolve_control_target(command: ControlCommand, candidates: tuple[TaskCandidate, ...]) -> ControlResolution:
    if command.intent is IntentType.NEW_TASK:
        return ControlResolution("CREATE_NEW", scope=command.domain_hint)
    if command.intent is IntentType.SYSTEM_MAINTENANCE:
        return ControlResolution("MAINTENANCE", scope=command.domain_hint or "GLOBAL")
    if command.intent is IntentType.QUERY and command.task_id_hint is None:
        return ControlResolution("QUERY", scope=command.domain_hint or "GLOBAL")

    eligible = [candidate for candidate in candidates if _eligible(candidate)]
    if command.task_id_hint:
        exact = [candidate for candidate in eligible if candidate.task_id == command.task_id_hint]
        if len(exact) != 1:
            raise ControlResolutionError(f"requested task is not uniquely resumable: {command.task_id_hint}")
        return ControlResolution(command.intent.value, task_id=exact[0].task_id, scope=exact[0].owner_domain)

    if command.domain_hint:
        eligible = [candidate for candidate in eligible if candidate.owner_domain == command.domain_hint]
    if command.task_type_hint:
        eligible = [candidate for candidate in eligible if candidate.task_type == command.task_type_hint]

    defaults = [candidate for candidate in eligible if candidate.default_resume]
    if len(defaults) == 1:
        selected = defaults[0]
    elif len(defaults) > 1:
        raise AmbiguousControlTarget("multiple default-resume tasks match")
    elif len(eligible) == 1:
        selected = eligible[0]
    elif not eligible:
        raise ControlResolutionError("no resumable task matches the control request")
    else:
        raise AmbiguousControlTarget("multiple resumable tasks match; exact task identity is required")
    return ControlResolution(command.intent.value, task_id=selected.task_id, scope=selected.owner_domain)


def effective_requirements(requirements: tuple[RequirementRecord, ...], context: RequirementContext) -> tuple[RequirementRecord, ...]:
    def applies(req: RequirementRecord) -> bool:
        if req.lifecycle_state is not RequirementState.ACTIVE:
            return False
        if req.scope_type is ScopeType.GLOBAL:
            return True
        if req.scope_type is ScopeType.SUBSYSTEM:
            return req.scope_id == context.owner_domain
        if req.scope_type is ScopeType.TASK_TYPE:
            return req.scope_id == context.task_type
        if req.scope_type is ScopeType.TASK:
            return req.scope_id == context.task_id
        if req.scope_type is ScopeType.ONE_SHOT:
            return req.requirement_id in context.one_shot_requirement_ids
        return False

    matched = [req for req in requirements if applies(req)]
    superseded_ids = {old_id for req in matched for old_id in req.supersedes}
    active = [req for req in matched if req.requirement_id not in superseded_ids]
    specificity = {ScopeType.GLOBAL: 0, ScopeType.SUBSYSTEM: 1, ScopeType.TASK_TYPE: 2, ScopeType.TASK: 3, ScopeType.ONE_SHOT: 4}
    return tuple(sorted(active, key=lambda req: (-req.priority, -specificity[req.scope_type], req.requirement_id)))
