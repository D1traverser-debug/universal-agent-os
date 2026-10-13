from __future__ import annotations

from collections import Counter, defaultdict, deque

from .models import Plan


def validate_plan(plan: Plan) -> None:
    units = {unit.work_unit_id: unit for unit in plan.work_units}
    if len(units) != len(plan.work_units):
        raise ValueError("duplicate work_unit_id")
    if any(unit.task_id != plan.task_id for unit in plan.work_units):
        raise ValueError("all work units must belong to plan.task_id")
    for unit in plan.work_units:
        missing = set(unit.dependencies) - units.keys()
        if missing:
            raise ValueError(f"unknown dependencies for {unit.work_unit_id}: {sorted(missing)}")
    _assert_acyclic(plan)
    _assert_artifact_reachability(plan)


def _assert_acyclic(plan: Plan) -> None:
    indegree = {unit.work_unit_id: 0 for unit in plan.work_units}
    children: dict[str, list[str]] = defaultdict(list)
    for unit in plan.work_units:
        for dep in unit.dependencies:
            indegree[unit.work_unit_id] += 1
            children[dep].append(unit.work_unit_id)
    queue = deque([unit_id for unit_id, degree in indegree.items() if degree == 0])
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        for child in children[current]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(plan.work_units):
        raise ValueError("plan contains a dependency cycle")


def _assert_artifact_reachability(plan: Plan) -> None:
    producer_counts = Counter(output for unit in plan.work_units for output in unit.expected_outputs)
    duplicates = sorted(name for name, count in producer_counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"ambiguous producers for outputs: {duplicates}")
    externally_available = set(plan.external_inputs)
    produced = set(producer_counts)
    for unit in plan.work_units:
        for required in unit.required_inputs:
            if required not in externally_available and required not in produced:
                raise ValueError(f"dead input: {unit.work_unit_id} requires {required!r} with no producer")
