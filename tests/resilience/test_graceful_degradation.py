from uaos.domain_sdk import LocalWorkflowRunner,WorkflowTemplate,WorkUnitTemplate
from uaos.execution import ActionCoordinator,CapabilityCostClass,CapabilityHealth,CapabilityObservation,CapabilityRegistry,ExecutionDisposition,ExecutionOutcome,ExecutionRequest
from uaos.resilience import CapabilityCircuitBreaker,CircuitState,DependencyClass,OperatingState

class Executor:
    def __init__(self,outcomes): self.outcomes=list(outcomes)
    def execute(self,request): return self.outcomes.pop(0)

def observation(capability_id,action,quality=0.8):
    return CapabilityObservation(capability_id,CapabilityHealth.AVAILABLE,1.0,(action,),quality_score=quality,cost_class=CapabilityCostClass.FREE)

def test_circuit_breaker_opens_then_recovers():
    circuit=CapabilityCircuitBreaker(failure_threshold=2,cooldown_seconds=10)
    circuit.record("cap",ExecutionDisposition.FAILED,now=1); circuit.record("cap",ExecutionDisposition.FAILED,now=2)
    assert circuit.state("cap",now=3) is CircuitState.OPEN
    assert not circuit.allows("cap",now=3)
    assert circuit.allows("cap",now=12)
    circuit.record("cap",ExecutionDisposition.CONFIRMED,now=12)
    assert circuit.state("cap",now=13) is CircuitState.CLOSED

def test_read_execution_fails_over_to_second_free_capability():
    registry=CapabilityRegistry(); registry.register(observation("first","research",0.9),Executor([ExecutionOutcome(ExecutionDisposition.FAILED,error="temporary")]))
    registry.register(observation("second","research",0.8),Executor([ExecutionOutcome(ExecutionDisposition.CONFIRMED,output="ok")]))
    result=ActionCoordinator(registry).execute_with_fallback(ExecutionRequest("a","research","topic",{},side_effect_class="READ"))
    assert result.capability_id=="second" and result.outcome.output=="ok"

def test_required_missing_capability_waits():
    template=WorkflowTemplate("t","required",(WorkUnitTemplate("u","U",expected_outputs=("x",),executor_constraints=("missing",)),),(),("x",))
    result=LocalWorkflowRunner(ActionCoordinator(CapabilityRegistry())).run(template,task_id="task",external_inputs={})
    assert result.status=="WAITING_CAPABILITY" and result.operating_state is OperatingState.WAITING_CAPABILITY

def test_preferred_uses_explicit_fallback_and_marks_degraded():
    template=WorkflowTemplate("t","preferred",(WorkUnitTemplate("u","U",expected_outputs=("x",),executor_constraints=("missing",),capability_requirement=DependencyClass.PREFERRED),),(),("x",))
    result=LocalWorkflowRunner(ActionCoordinator(CapabilityRegistry())).run(template,task_id="task",external_inputs={},fallbacks={"missing":lambda unit,objects:"cached"})
    assert result.status=="COMPLETE_DEGRADED" and result.objects["x"]=="cached"

def test_optional_no_output_can_skip():
    template=WorkflowTemplate("t","optional",(WorkUnitTemplate("optional","Optional",executor_constraints=("missing",),capability_requirement=DependencyClass.OPTIONAL),WorkUnitTemplate("main","Main",dependencies=("optional",),expected_outputs=("x",),executor_constraints=("main",))),(),("x",))
    registry=CapabilityRegistry(); registry.register(observation("main-cap","main"),Executor([ExecutionOutcome(ExecutionDisposition.CONFIRMED,output="ok")]))
    result=LocalWorkflowRunner(ActionCoordinator(registry)).run(template,task_id="task",external_inputs={})
    assert result.status=="COMPLETE_DEGRADED"
