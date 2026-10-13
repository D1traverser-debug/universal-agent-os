import pytest
from uaos.contracts.models import Plan, WorkUnit
from uaos.contracts.planning import validate_plan


def test_valid_plan_with_real_artifact_dependency():
    research = WorkUnit("research", "t1", "research", expected_outputs=("research-pack",))
    write = WorkUnit("write", "t1", "write", dependencies=("research",), required_inputs=("research-pack", "user-brief"), expected_outputs=("draft",))
    validate_plan(Plan("p1", "t1", 1, (research, write), external_inputs=("user-brief",)))


def test_dead_artifact_input_is_rejected():
    write = WorkUnit("write", "t1", "write", required_inputs=("missing-research",), expected_outputs=("draft",))
    with pytest.raises(ValueError, match="dead input"):
        validate_plan(Plan("p1", "t1", 1, (write,)))


def test_dependency_cycle_is_rejected():
    a = WorkUnit("a", "t1", "a", dependencies=("b",))
    b = WorkUnit("b", "t1", "b", dependencies=("a",))
    with pytest.raises(ValueError, match="cycle"):
        validate_plan(Plan("p1", "t1", 1, (a, b)))


def test_ambiguous_output_producer_is_rejected():
    a = WorkUnit("a", "t1", "a", expected_outputs=("same",))
    b = WorkUnit("b", "t1", "b", expected_outputs=("same",))
    with pytest.raises(ValueError, match="ambiguous producers"):
        validate_plan(Plan("p1", "t1", 1, (a, b)))
