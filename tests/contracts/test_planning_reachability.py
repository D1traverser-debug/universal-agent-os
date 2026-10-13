import pytest
from uaos.contracts.models import Plan, WorkUnit
from uaos.contracts.planning import execution_layers, topological_order, validate_plan


def test_artifact_producer_must_be_upstream():
    producer = WorkUnit("producer", "t", "produce", expected_outputs=("x",))
    consumer = WorkUnit("consumer", "t", "consume", required_inputs=("x",))
    with pytest.raises(ValueError, match="unreachable input"):
        validate_plan(Plan("p", "t", 1, (producer, consumer)))


def test_transitive_dependency_makes_artifact_reachable():
    first = WorkUnit("a", "t", "a", expected_outputs=("x",))
    second = WorkUnit("b", "t", "b", dependencies=("a",), required_inputs=("x",), expected_outputs=("y",))
    third = WorkUnit("c", "t", "c", dependencies=("b",), required_inputs=("x", "y"))
    validate_plan(Plan("p", "t", 1, (first, second, third)))


def test_external_and_produced_name_cannot_be_ambiguous():
    producer = WorkUnit("a", "t", "a", expected_outputs=("brief",))
    with pytest.raises(ValueError, match="ambiguous external"):
        validate_plan(Plan("p", "t", 1, (producer,), external_inputs=("brief",)))


def test_execution_layers_expose_parallelism():
    first = WorkUnit("a", "t", "a")
    second = WorkUnit("b", "t", "b")
    join = WorkUnit("c", "t", "c", dependencies=("a", "b"))
    plan = Plan("p", "t", 1, (first, second, join))
    assert execution_layers(plan) == (("a", "b"), ("c",))
    assert topological_order(plan)[-1] == "c"
