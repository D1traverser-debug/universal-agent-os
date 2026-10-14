from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RunnableWork:
    task_id: str
    work_unit_id: str
    task_priority: int
    work_priority: int = 100
    resource_keys: tuple[str, ...] = ()
    work_class: str = "FOREGROUND"

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.work_unit_id.strip():
            raise ValueError("task_id and work_unit_id are required")
        if len(self.resource_keys) != len(set(self.resource_keys)):
            raise ValueError("duplicate resource key")
        if self.work_class not in {"FOREGROUND", "MAINTENANCE"}:
            raise ValueError("work_class must be FOREGROUND or MAINTENANCE")


@dataclass(frozen=True, slots=True)
class ScheduleSelection:
    selected: tuple[RunnableWork, ...]
    deferred: tuple[RunnableWork, ...]


@dataclass(frozen=True, slots=True)
class IdleAdmissionEvidence:
    allowed: bool
    foreground_work_ids: tuple[str, ...]
    conflicting_resources: tuple[str, ...]


def select_non_conflicting(items: tuple[RunnableWork, ...], *, max_slots: int) -> ScheduleSelection:
    if max_slots < 1:
        raise ValueError("max_slots must be >= 1")
    ordered = sorted(items, key=lambda x: (-x.task_priority, -x.work_priority, x.task_id, x.work_unit_id))
    selected: list[RunnableWork] = []
    deferred: list[RunnableWork] = []
    held_resources: set[str] = set()
    for item in ordered:
        if len(selected) >= max_slots or held_resources.intersection(item.resource_keys):
            deferred.append(item)
            continue
        selected.append(item)
        held_resources.update(item.resource_keys)
    return ScheduleSelection(tuple(selected), tuple(deferred))


def assess_idle_capacity(
    runnable: tuple[RunnableWork, ...],
    *,
    active_resource_keys: tuple[str, ...] = (),
    maintenance_resource_keys: tuple[str, ...] = (),
) -> IdleAdmissionEvidence:
    """Prove whether background maintenance may be admitted now.

    `runnable` is the authority-derived runnable set, not a model guess. Any
    foreground runnable work blocks IDLE maintenance. Active resources needed
    by maintenance also block admission. Maintenance items do not make the
    system non-idle by themselves.
    """
    foreground = tuple(sorted(item.work_unit_id for item in runnable if item.work_class == "FOREGROUND"))
    conflicts = tuple(sorted(set(active_resource_keys).intersection(maintenance_resource_keys)))
    return IdleAdmissionEvidence(not foreground and not conflicts, foreground, conflicts)
