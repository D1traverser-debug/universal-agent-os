from dataclasses import replace
from pathlib import Path
import pytest

from uaos.contracts.enums import IntentType, WorkStatus
from uaos.contracts.planning import execution_layers, validate_plan
from uaos.domain_sdk import DomainRegistry, load_domain_package
from uaos.kernel import expand_fanout

ROOT=Path(__file__).resolve().parents[1]

def load(name):
    manifest, templates=load_domain_package(ROOT/'domains'/name)
    reg=DomainRegistry(); reg.register(manifest,templates)
    return reg, templates[0]

def test_novel_whole_source_coverage_precedes_distillation_and_original_architecture():
    reg,_=load('novel')
    plan=reg.resolve_new_task('novel',intent=IntentType.NEW_TASK,task_type='novel_project').compile(task_id='n1',plan_id='p1')
    order=[x.split(':',1)[1] for layer in execution_layers(plan) for x in layer]
    assert order.index('source_coverage') < order.index('distill') < order.index('architecture') < order.index('draft')
    assert order.index('review') < order.index('revise') < order.index('artifact_qa') < order.index('release')

def test_video_merge_is_held_until_dynamic_shot_fanout_is_expanded():
    reg,_=load('video')
    plan=reg.resolve_new_task('video',intent=IntentType.NEW_TASK,task_type='short_video').compile(task_id='v1',plan_id='p1')
    merge=next(u for u in plan.work_units if u.work_unit_id=='v1:assemble_shots')
    assert merge.status is WorkStatus.HOLD
    expanded=expand_fanout(plan,source_unit_id='v1:pre_generation_review',source_artifact='authorized_shot_specs',merge_unit_id='v1:assemble_shots',item_keys=('shot-001','shot-002','shot-003'),child_name='Generate and review shot',executor_constraints=('video.generate_shot','video.shot_review'),output_namespace='approved_shot',new_plan_id='p2',risk='HIGH')
    validate_plan(expanded)
    merge=next(u for u in expanded.work_units if u.work_unit_id=='v1:assemble_shots')
    children=[u for u in expanded.work_units if ':fanout:' in u.work_unit_id]
    assert len(children)==3
    assert merge.status is WorkStatus.PENDING
    assert set(c.work_unit_id for c in children).issubset(merge.dependencies)
    assert {'approved_shot:shot-001','approved_shot:shot-002','approved_shot:shot-003'}.issubset(merge.required_inputs)

def test_fanout_rejects_duplicates_and_late_expansion():
    reg,_=load('video')
    plan=reg.resolve_new_task('video',intent=IntentType.NEW_TASK,task_type='short_video').compile(task_id='v1',plan_id='p1')
    with pytest.raises(ValueError,match='duplicate'):
        expand_fanout(plan,source_unit_id='v1:pre_generation_review',source_artifact='authorized_shot_specs',merge_unit_id='v1:assemble_shots',item_keys=('a','a'),child_name='x',executor_constraints=('video.generate_shot',),output_namespace='shot',new_plan_id='p2')
    units=tuple(replace(u,status=WorkStatus.SUCCEEDED) if u.work_unit_id=='v1:assemble_shots' else u for u in plan.work_units)
    advanced=replace(plan,work_units=units)
    with pytest.raises(ValueError,match='advanced'):
        expand_fanout(advanced,source_unit_id='v1:pre_generation_review',source_artifact='authorized_shot_specs',merge_unit_id='v1:assemble_shots',item_keys=('a',),child_name='x',executor_constraints=('video.generate_shot',),output_namespace='shot',new_plan_id='p2')

def test_video_pre_generation_review_is_upstream_of_any_generated_shot():
    reg,_=load('video')
    plan=reg.resolve_new_task('video',intent=IntentType.NEW_TASK,task_type='short_video').compile(task_id='v1',plan_id='p1')
    expanded=expand_fanout(plan,source_unit_id='v1:pre_generation_review',source_artifact='authorized_shot_specs',merge_unit_id='v1:assemble_shots',item_keys=('s1','s2'),child_name='shot',executor_constraints=('video.generate_shot','video.shot_review'),output_namespace='approved_shot',new_plan_id='p2',risk='HIGH')
    for child in [u for u in expanded.work_units if ':fanout:' in u.work_unit_id]:
        assert child.dependencies==('v1:pre_generation_review',)
        assert child.required_inputs==('authorized_shot_specs',)
        assert child.bindings in {(('item_key','s1'),),(('item_key','s2'),)}
