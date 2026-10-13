from __future__ import annotations

from dataclasses import replace
from typing import Mapping

from uaos.contracts.enums import WorkStatus
from uaos.contracts.models import Plan, WorkUnit
from uaos.contracts.planning import transitive_dependents, validate_plan


_SUCCESS = {WorkStatus.SUCCEEDED}


def ready_work_units(plan: Plan, status_by_id: Mapping[str, WorkStatus] | None = None) -> tuple[WorkUnit, ...]:
    validate_plan(plan)
    status_by_id = status_by_id or {unit.work_unit_id: unit.status for unit in plan.work_units}
    ready = []
    for unit in plan.work_units:
        current = status_by_id.get(unit.work_unit_id, unit.status)
        if current not in {WorkStatus.PENDING, WorkStatus.READY, WorkStatus.INVALIDATED}:
            continue
        if all(status_by_id.get(dep, WorkStatus.PENDING) in _SUCCESS for dep in unit.dependencies):
            ready.append(unit)
    return tuple(sorted(ready, key=lambda unit: unit.work_unit_id))


def invalidate_impacted(plan: Plan, roots: set[str] | frozenset[str], *, new_plan_id: str) -> Plan:
    impacted = transitive_dependents(plan, roots)
    units = tuple(
        replace(unit, status=WorkStatus.INVALIDATED)
        if unit.work_unit_id in impacted
        else unit
        for unit in plan.work_units
    )
    updated = replace(plan, plan_id=new_plan_id, version=plan.version + 1, work_units=units)
    validate_plan(updated)
    return updated


def reusable_successes(old_plan: Plan, new_plan: Plan) -> frozenset[str]:
    """Return succeeded work units whose contract is unchanged in the new plan."""
    old = {unit.work_unit_id: unit for unit in old_plan.work_units}
    reusable = set()
    for unit in new_plan.work_units:
        prior = old.get(unit.work_unit_id)
        if prior is None or prior.status is not WorkStatus.SUCCEEDED:
            continue
        if unit.status is WorkStatus.INVALIDATED:
            continue
        if replace(prior, status=WorkStatus.PENDING) == replace(unit, status=WorkStatus.PENDING):
            reusable.add(unit.work_unit_id)
    return frozenset(reusable)
