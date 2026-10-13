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


def topological_order(plan: Plan) -> tuple[str, ...]:
    validate_plan(plan)
    indegree, children = _graph(plan)
    queue = deque(sorted(unit_id for unit_id, degree in indegree.items() if degree == 0))
    result: list[str] = []
    while queue:
        current = queue.popleft()
        result.append(current)
        for child in sorted(children[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    return tuple(result)


def execution_layers(plan: Plan) -> tuple[tuple[str, ...], ...]:
    validate_plan(plan)
    indegree, children = _graph(plan)
    current = sorted(unit_id for unit_id, degree in indegree.items() if degree == 0)
    layers: list[tuple[str, ...]] = []
    while current:
        layers.append(tuple(current))
        nxt: list[str] = []
        for unit_id in current:
            for child in children[unit_id]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    nxt.append(child)
        current = sorted(nxt)
    return tuple(layers)


def transitive_dependents(plan: Plan, roots: set[str] | frozenset[str]) -> frozenset[str]:
    validate_plan(plan)
    unit_ids = {unit.work_unit_id for unit in plan.work_units}
    unknown = set(roots) - unit_ids
    if unknown:
        raise ValueError(f"unknown impacted work units: {sorted(unknown)}")
    _, children = _graph(plan)
    impacted = set(roots)
    queue = deque(roots)
    while queue:
        current = queue.popleft()
        for child in children[current]:
            if child not in impacted:
                impacted.add(child)
                queue.append(child)
    return frozenset(impacted)


def _graph(plan: Plan) -> tuple[dict[str, int], dict[str, list[str]]]:
    indegree = {unit.work_unit_id: 0 for unit in plan.work_units}
    children: dict[str, list[str]] = defaultdict(list)
    for unit in plan.work_units:
        for dep in unit.dependencies:
            indegree[unit.work_unit_id] += 1
            children[dep].append(unit.work_unit_id)
    return indegree, children


def _assert_acyclic(plan: Plan) -> None:
    indegree, children = _graph(plan)
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


def _ancestors(plan: Plan) -> dict[str, set[str]]:
    dependencies = {unit.work_unit_id: set(unit.dependencies) for unit in plan.work_units}
    memo: dict[str, set[str]] = {}

    def visit(unit_id: str) -> set[str]:
        if unit_id in memo:
            return memo[unit_id]
        result: set[str] = set()
        for dep in dependencies[unit_id]:
            result.add(dep)
            result.update(visit(dep))
        memo[unit_id] = result
        return result

    for unit_id in dependencies:
        visit(unit_id)
    return memo


def _assert_artifact_reachability(plan: Plan) -> None:
    producers: dict[str, str] = {}
    counts = Counter(output for unit in plan.work_units for output in unit.expected_outputs)
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"ambiguous producers for outputs: {duplicates}")
    for unit in plan.work_units:
        for output in unit.expected_outputs:
            producers[output] = unit.work_unit_id

    external = set(plan.external_inputs)
    overlap = sorted(external.intersection(producers))
    if overlap:
        raise ValueError(f"ambiguous external/produced inputs: {overlap}")

    ancestors = _ancestors(plan)
    for unit in plan.work_units:
        for required in unit.required_inputs:
            if required in external:
                continue
            producer = producers.get(required)
            if producer is None:
                raise ValueError(f"dead input: {unit.work_unit_id} requires {required!r} with no producer")
            if producer not in ancestors[unit.work_unit_id]:
                raise ValueError(
                    f"unreachable input: {unit.work_unit_id} requires {required!r} "
                    f"from producer {producer!r} that is not an upstream dependency"
                )
