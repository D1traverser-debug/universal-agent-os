from __future__ import annotations

import re
from dataclasses import replace

from uaos.contracts.enums import WorkStatus
from uaos.contracts.models import Plan, WorkUnit
from uaos.contracts.planning import validate_plan

_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")


def _safe_key(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("fanout item key is required")
    return _SAFE.sub("_", value)


def expand_fanout(
    plan: Plan,
    *,
    source_unit_id: str,
    source_artifact: str,
    merge_unit_id: str,
    item_keys: tuple[str, ...],
    child_name: str,
    executor_constraints: tuple[str, ...],
    output_namespace: str,
    new_plan_id: str,
    risk: str = "MEDIUM",
) -> Plan:
    validate_plan(plan)
    if len(set(item_keys)) != len(item_keys):
        raise ValueError("duplicate fanout item key")
    if not item_keys:
        raise ValueError("fanout requires at least one item")
    safe_keys = tuple(_safe_key(item) for item in item_keys)
    if len(set(safe_keys)) != len(safe_keys):
        raise ValueError("fanout item keys collide after normalization")

    units = {u.work_unit_id: u for u in plan.work_units}
    try:
        source = units[source_unit_id]
        merge = units[merge_unit_id]
    except KeyError as exc:
        raise ValueError(f"unknown fanout unit: {exc.args[0]}") from exc
    if source_artifact not in source.expected_outputs:
        raise ValueError("source_artifact is not produced by source_unit")
    if merge.status not in {WorkStatus.HOLD, WorkStatus.PENDING, WorkStatus.INVALIDATED}:
        raise ValueError("merge unit already advanced; fanout expansion is unsafe")

    children: list[WorkUnit] = []
    child_outputs: list[str] = []
    for item, safe in zip(item_keys, safe_keys, strict=True):
        child_id = f"{plan.task_id}:fanout:{safe}"
        if child_id in units:
            raise ValueError(f"fanout child already exists: {child_id}")
        output = f"{output_namespace}:{safe}"
        child_outputs.append(output)
        children.append(
            WorkUnit(
                work_unit_id=child_id,
                task_id=plan.task_id,
                name=f"{child_name}: {item}",
                dependencies=(source_unit_id,),
                required_inputs=(source_artifact,),
                expected_outputs=(output,),
                executor_constraints=executor_constraints,
                risk=risk,
                status=WorkStatus.PENDING,
                bindings=(("item_key", item),),
            )
        )

    merge_deps = tuple(dict.fromkeys((*merge.dependencies, *(c.work_unit_id for c in children))))
    merge_inputs = tuple(dict.fromkeys((*merge.required_inputs, *child_outputs)))
    updated_merge = replace(merge, dependencies=merge_deps, required_inputs=merge_inputs, status=WorkStatus.PENDING)
    updated_units = tuple(updated_merge if u.work_unit_id == merge_unit_id else u for u in plan.work_units) + tuple(children)
    updated = replace(plan, plan_id=new_plan_id, version=plan.version + 1, work_units=updated_units)
    validate_plan(updated)
    return updated
