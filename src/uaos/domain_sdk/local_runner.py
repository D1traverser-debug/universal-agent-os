from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Any, Callable, Mapping
from uaos.contracts.enums import WorkStatus
from uaos.contracts.models import Plan, WorkUnit
from uaos.contracts.planning import validate_plan
from uaos.execution import ActionCoordinator, ApprovalRequired, CapabilityUnavailable, ExecutionDisposition, ExecutionRequest
from uaos.resilience import DependencyClass, OperatingState, decide_missing_capability
from .workflows import WorkflowTemplate

PlanHook=Callable[[Plan,WorkUnit,Mapping[str,Any]],Plan]
FallbackHook=Callable[[WorkUnit,Mapping[str,Any]],Mapping[str,Any]|Any]

@dataclass(frozen=True,slots=True)
class LocalRunResult:
    status:str
    plan:Plan
    objects:Mapping[str,Any]
    capability_trace:tuple[tuple[str,str],...]
    blocked_reason:str|None=None
    operating_state:OperatingState=OperatingState.NORMAL

def _dependency_class(unit:WorkUnit)->DependencyClass:
    return DependencyClass(dict(unit.bindings).get("uaos.dependency_class","REQUIRED"))

def _requires_background(unit:WorkUnit)->bool:
    return dict(unit.bindings).get("uaos.requires_background")=="true"

class LocalWorkflowRunner:
    """Checkpoint-bound local executor with graceful capability degradation."""
    def __init__(self, coordinator:ActionCoordinator)->None:
        self.coordinator=coordinator
    def run(self,template:WorkflowTemplate,*,task_id:str,external_inputs:Mapping[str,Any],after_unit:PlanHook|None=None,fallbacks:Mapping[str,FallbackHook]|None=None,max_steps:int=1000)->LocalRunResult:
        fallbacks=fallbacks or {}
        missing=set(template.external_inputs)-external_inputs.keys()
        if missing: raise ValueError(f"missing external inputs: {sorted(missing)}")
        plan=template.compile(task_id=task_id,plan_id=f"{task_id}:plan:1")
        objects=dict(external_inputs); trace=[]; degraded=False
        for _ in range(max_steps):
            units={u.work_unit_id:u for u in plan.work_units}
            succeeded={uid for uid,u in units.items() if u.status is WorkStatus.SUCCEEDED}
            pending=[u for u in plan.work_units if u.status in {WorkStatus.PENDING,WorkStatus.READY}]
            if not pending:
                if all(name in objects for name in template.delivery_outputs):
                    state=OperatingState.DEGRADED if degraded else OperatingState.NORMAL
                    return LocalRunResult("COMPLETE_DEGRADED" if degraded else "COMPLETE",plan,objects,tuple(trace),operating_state=state)
                holds=[u.work_unit_id for u in plan.work_units if u.status is WorkStatus.HOLD]
                return LocalRunResult("BLOCKED",plan,objects,tuple(trace),f"no runnable work; holds={holds}",OperatingState.BLOCKED)
            runnable=[u for u in pending if set(u.dependencies).issubset(succeeded)]
            if not runnable:
                holds=[u.work_unit_id for u in plan.work_units if u.status is WorkStatus.HOLD]
                return LocalRunResult("BLOCKED",plan,objects,tuple(trace),f"dependencies not satisfiable; holds={holds}",OperatingState.BLOCKED)
            progressed=False
            for unit in runnable:
                if any(name not in objects for name in unit.required_inputs): continue
                if not unit.executor_constraints:
                    return LocalRunResult("BLOCKED",plan,objects,tuple(trace),f"no executor constraint for {unit.work_unit_id}",OperatingState.BLOCKED)
                action=unit.executor_constraints[0]; bindings=dict(unit.bindings)
                request=ExecutionRequest(action_id=f"{unit.work_unit_id}:attempt:1",action_name=action,target=unit.work_unit_id,payload={"inputs":{n:objects[n] for n in unit.required_inputs},"expected_outputs":unit.expected_outputs,"bindings":bindings},side_effect_class="NONE",allow_paid=False,allow_unknown_cost=False,requires_background=_requires_background(unit))
                try:
                    execution=self.coordinator.execute_with_fallback(request)
                except ApprovalRequired as exc:
                    return LocalRunResult("WAITING_APPROVAL",plan,objects,tuple(trace),str(exc),OperatingState.WAITING_APPROVAL)
                except CapabilityUnavailable as exc:
                    fallback=fallbacks.get(unit.work_unit_id) or fallbacks.get(action)
                    decision=decide_missing_capability(_dependency_class(unit),fallback_available=fallback is not None,requires_background=_requires_background(unit),background_host_available=False,optional_outputs_required_downstream=bool(unit.expected_outputs))
                    if fallback is None:
                        if decision.may_continue and _dependency_class(unit) is DependencyClass.OPTIONAL and not unit.expected_outputs:
                            degraded=True; updated=replace(unit,status=WorkStatus.SUCCEEDED)
                            plan=replace(plan,work_units=tuple(updated if x.work_unit_id==unit.work_unit_id else x for x in plan.work_units)); trace.append((unit.work_unit_id,"optional-skip")); progressed=True; break
                        return LocalRunResult(decision.state.value,plan,objects,tuple(trace),str(exc),decision.state)
                    value=fallback(unit,objects); degraded=True; capability_id="fallback"
                else:
                    trace.append((unit.work_unit_id,execution.capability_id))
                    if execution.outcome.disposition is ExecutionDisposition.UNKNOWN:
                        return LocalRunResult("UNKNOWN",plan,objects,tuple(trace),execution.outcome.error or "unknown execution outcome",OperatingState.RECOVERY_REQUIRED)
                    if execution.outcome.disposition is ExecutionDisposition.FAILED:
                        return LocalRunResult("WAITING_CAPABILITY",plan,objects,tuple(trace),execution.outcome.error or "all eligible capabilities failed",OperatingState.WAITING_CAPABILITY)
                    value=execution.outcome.output; capability_id=execution.capability_id
                if len(unit.expected_outputs)==1 and not isinstance(value,Mapping): produced={unit.expected_outputs[0]:value}
                else:
                    if not isinstance(value,Mapping): return LocalRunResult("BLOCKED",plan,objects,tuple(trace),f"{unit.work_unit_id} must return mapping for multiple outputs",OperatingState.BLOCKED)
                    missing_outputs=set(unit.expected_outputs)-value.keys()
                    if missing_outputs: return LocalRunResult("BLOCKED",plan,objects,tuple(trace),f"{unit.work_unit_id} missing outputs: {sorted(missing_outputs)}",OperatingState.BLOCKED)
                    produced={name:value[name] for name in unit.expected_outputs}
                objects.update(produced); updated=replace(unit,status=WorkStatus.SUCCEEDED)
                plan=replace(plan,work_units=tuple(updated if x.work_unit_id==unit.work_unit_id else x for x in plan.work_units))
                if capability_id=="fallback": trace.append((unit.work_unit_id,"fallback"))
                if after_unit is not None: plan=after_unit(plan,updated,produced); validate_plan(plan)
                progressed=True; break
            if not progressed: return LocalRunResult("BLOCKED",plan,objects,tuple(trace),"runnable work is missing required objects",OperatingState.BLOCKED)
        return LocalRunResult("BLOCKED",plan,objects,tuple(trace),"max_steps exceeded",OperatingState.BLOCKED)
