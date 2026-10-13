from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RunnableWork:
    task_id: str
    work_unit_id: str
    task_priority: int
    work_priority: int = 100
    resource_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.work_unit_id.strip():
            raise ValueError("task_id and work_unit_id are required")
        if len(self.resource_keys) != len(set(self.resource_keys)):
            raise ValueError("duplicate resource key")


@dataclass(frozen=True, slots=True)
class ScheduleSelection:
    selected: tuple[RunnableWork, ...]
    deferred: tuple[RunnableWork, ...]


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
