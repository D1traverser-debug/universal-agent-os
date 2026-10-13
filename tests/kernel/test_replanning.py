from uaos.contracts.enums import WorkStatus
from uaos.contracts.models import Plan, WorkUnit
from uaos.kernel import invalidate_impacted, ready_work_units, reusable_successes


def plan():
    research = WorkUnit("research", "t", "research", expected_outputs=("facts",), status=WorkStatus.SUCCEEDED)
    outline = WorkUnit("outline", "t", "outline", dependencies=("research",), required_inputs=("facts",), expected_outputs=("outline",), status=WorkStatus.SUCCEEDED)
    draft = WorkUnit("draft", "t", "draft", dependencies=("outline",), required_inputs=("outline",), expected_outputs=("draft",))
    qa = WorkUnit("qa", "t", "qa", dependencies=("draft",), required_inputs=("draft",))
    return Plan("p1", "t", 1, (research, outline, draft, qa), external_inputs=("brief",))


def test_ready_units_require_successful_dependencies():
    assert [unit.work_unit_id for unit in ready_work_units(plan())] == ["draft"]


def test_requirement_change_invalidates_only_impacted_subgraph():
    old = plan()
    new = invalidate_impacted(old, {"outline"}, new_plan_id="p2")
    states = {unit.work_unit_id: unit.status for unit in new.work_units}
    assert new.version == 2
    assert states["research"] is WorkStatus.SUCCEEDED
    assert states["outline"] is WorkStatus.INVALIDATED
    assert states["draft"] is WorkStatus.INVALIDATED
    assert states["qa"] is WorkStatus.INVALIDATED
    assert reusable_successes(old, new) == frozenset({"research"})
