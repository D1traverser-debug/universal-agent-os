from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Mapping

from uaos.contracts.enums import WorkStatus
from uaos.contracts.models import Plan, WorkUnit
from uaos.contracts.planning import validate_plan
from uaos.execution import ActionCoordinator, ExecutionDisposition, ExecutionRequest

from .workflows import WorkflowTemplate

PlanHook = Callable[[Plan, WorkUnit, Mapping[str, Any]], Plan]


@dataclass(frozen=True, slots=True)
class LocalRunResult:
    status: str
    plan: Plan
    objects: Mapping[str, Any]
    capability_trace: tuple[tuple[str, str], ...]
    blocked_reason: str | None = None


class LocalWorkflowRunner:
    """Execute a Domain workflow against currently registered zero-cost capabilities.

    It is intentionally simple and checkpoint-bound: it advances one WorkUnit at
    a time and never assumes an unavailable plugin/model/tool. HOLD nodes require
    an explicit plan hook (for example dynamic fan-out) before they may proceed.
    """

    def __init__(self, coordinator: ActionCoordinator) -> None:
        self.coordinator = coordinator

    def run(
        self,
        template: WorkflowTemplate,
        *,
        task_id: str,
        external_inputs: Mapping[str, Any],
        after_unit: PlanHook | None = None,
        max_steps: int = 1000,
    ) -> LocalRunResult:
        missing = set(template.external_inputs) - external_inputs.keys()
        if missing:
            raise ValueError(f"missing external inputs: {sorted(missing)}")
        plan = template.compile(task_id=task_id, plan_id=f"{task_id}:plan:1")
        objects = dict(external_inputs)
        trace: list[tuple[str, str]] = []

        for _ in range(max_steps):
            units = {u.work_unit_id: u for u in plan.work_units}
            succeeded = {uid for uid, unit in units.items() if unit.status is WorkStatus.SUCCEEDED}
            pending = [u for u in plan.work_units if u.status in {WorkStatus.PENDING, WorkStatus.READY}]
            if not pending:
                if all(name in objects for name in template.delivery_outputs):
                    return LocalRunResult("COMPLETE", plan, objects, tuple(trace))
                holds = [u.work_unit_id for u in plan.work_units if u.status is WorkStatus.HOLD]
                return LocalRunResult("BLOCKED", plan, objects, tuple(trace), f"no runnable work; holds={holds}")

            runnable = [u for u in pending if set(u.dependencies).issubset(succeeded)]
            if not runnable:
                holds = [u.work_unit_id for u in plan.work_units if u.status is WorkStatus.HOLD]
                return LocalRunResult("BLOCKED", plan, objects, tuple(trace), f"dependencies not satisfiable; holds={holds}")

            progressed = False
            for unit in runnable:
                if any(name not in objects for name in unit.required_inputs):
                    continue
                if not unit.executor_constraints:
                    return LocalRunResult("BLOCKED", plan, objects, tuple(trace), f"no executor constraint for {unit.work_unit_id}")
                action = unit.executor_constraints[0]
                request = ExecutionRequest(
                    action_id=f"{unit.work_unit_id}:attempt:1",
                    action_name=action,
                    target=unit.work_unit_id,
                    payload={
                        "inputs": {name: objects[name] for name in unit.required_inputs},
                        "expected_outputs": unit.expected_outputs,
                        "bindings": dict(unit.bindings),
                    },
                    side_effect_class="NONE",
                    allow_paid=False,
                    allow_unknown_cost=False,
                )
                try:
                    execution = self.coordinator.execute(request)
                except Exception as exc:
                    return LocalRunResult("BLOCKED", plan, objects, tuple(trace), f"{type(exc).__name__}: {exc}")
                trace.append((unit.work_unit_id, execution.capability_id))
                if execution.outcome.disposition is ExecutionDisposition.UNKNOWN:
                    return LocalRunResult("UNKNOWN", plan, objects, tuple(trace), execution.outcome.error or "unknown execution outcome")
                if execution.outcome.disposition is ExecutionDisposition.FAILED:
                    return LocalRunResult("FAILED", plan, objects, tuple(trace), execution.outcome.error or "execution failed")

                value = execution.outcome.output
                if len(unit.expected_outputs) == 1 and not isinstance(value, Mapping):
                    produced = {unit.expected_outputs[0]: value}
                else:
                    if not isinstance(value, Mapping):
                        return LocalRunResult("FAILED", plan, objects, tuple(trace), f"{unit.work_unit_id} must return mapping for multiple outputs")
                    missing_outputs = set(unit.expected_outputs) - value.keys()
                    if missing_outputs:
                        return LocalRunResult("FAILED", plan, objects, tuple(trace), f"{unit.work_unit_id} missing outputs: {sorted(missing_outputs)}")
                    produced = {name: value[name] for name in unit.expected_outputs}
                objects.update(produced)
                updated = replace(unit, status=WorkStatus.SUCCEEDED)
                plan = replace(plan, work_units=tuple(updated if x.work_unit_id == unit.work_unit_id else x for x in plan.work_units))
                if after_unit is not None:
                    plan = after_unit(plan, updated, produced)
                    validate_plan(plan)
                progressed = True
                break

            if not progressed:
                return LocalRunResult("BLOCKED", plan, objects, tuple(trace), "runnable work is missing required objects")

        return LocalRunResult("FAILED", plan, objects, tuple(trace), "max_steps exceeded")
