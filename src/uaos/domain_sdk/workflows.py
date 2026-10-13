from __future__ import annotations
from dataclasses import dataclass
from uaos.contracts.enums import WorkStatus
from uaos.contracts.models import Plan, WorkUnit
from uaos.contracts.planning import validate_plan

@dataclass(frozen=True, slots=True)
class WorkUnitTemplate:
    unit_id: str
    name: str
    dependencies: tuple[str, ...] = ()
    required_inputs: tuple[str, ...] = ()
    expected_outputs: tuple[str, ...] = ()
    executor_constraints: tuple[str, ...] = ()
    risk: str = "LOW"
    initial_status: WorkStatus = WorkStatus.PENDING

    def __post_init__(self) -> None:
        if not self.unit_id.strip() or not self.name.strip():
            raise ValueError("unit_id and name are required")
        if self.unit_id in self.dependencies:
            raise ValueError("template unit cannot depend on itself")

@dataclass(frozen=True, slots=True)
class WorkflowTemplate:
    template_id: str
    description: str
    units: tuple[WorkUnitTemplate, ...]
    external_inputs: tuple[str, ...]
    delivery_outputs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.template_id.strip() or not self.description.strip():
            raise ValueError("template_id and description are required")
        unit_ids = [u.unit_id for u in self.units]
        if len(unit_ids) != len(set(unit_ids)):
            raise ValueError("duplicate template unit_id")
        produced = {o for u in self.units for o in u.expected_outputs}
        missing_delivery = set(self.delivery_outputs) - produced
        if missing_delivery:
            raise ValueError(f"delivery outputs have no producer: {sorted(missing_delivery)}")

    def compile(self, *, task_id: str, plan_id: str, version: int = 1) -> Plan:
        if not task_id.strip() or not plan_id.strip():
            raise ValueError("task_id and plan_id are required")
        id_map = {unit.unit_id: f"{task_id}:{unit.unit_id}" for unit in self.units}
        work_units = tuple(
            WorkUnit(
                work_unit_id=id_map[unit.unit_id],
                task_id=task_id,
                name=unit.name,
                dependencies=tuple(id_map[dep] for dep in unit.dependencies),
                required_inputs=unit.required_inputs,
                expected_outputs=unit.expected_outputs,
                executor_constraints=unit.executor_constraints,
                risk=unit.risk,
                status=unit.initial_status,
            )
            for unit in self.units
        )
        plan = Plan(
            plan_id=plan_id,
            task_id=task_id,
            version=version,
            work_units=work_units,
            external_inputs=self.external_inputs,
        )
        validate_plan(plan)
        return plan
