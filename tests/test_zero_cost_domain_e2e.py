import json
from pathlib import Path

import pytest

from uaos.domain_sdk import LocalWorkflowRunner, load_domain_package
from uaos.execution import ActionCoordinator, CapabilityCostClass, CapabilityRegistry, HostCapabilitySpec, register_host_capability
from uaos.integrations import AgentLinkRegistry
from uaos.kernel import expand_fanout

ROOT = Path(__file__).resolve().parents[1]


def _callback(request):
    outputs = {}
    for name in request.payload["expected_outputs"]:
        if request.action_name == "video.pre_generation_review" and name == "authorized_shot_specs":
            outputs[name] = {"shots": [{"shot_id": "shot_01"}, {"shot_id": "shot_02"}]}
        elif request.action_name == "ashare.recall" and name == "candidate_universe":
            outputs[name] = ("000001.SZ", "600000.SH")
        else:
            outputs[name] = {"produced_by": request.action_name, "name": name}
    return outputs


def _runner_for(template, extra_actions=()):
    registry = CapabilityRegistry()
    actions = {constraint for unit in template.units for constraint in unit.executor_constraints}
    actions.update(extra_actions)
    for action in actions:
        register_host_capability(
            registry,
            HostCapabilitySpec(
                capability_id=f"host:{action}",
                supported_actions=(action,),
                callback=_callback,
                quality_score=0.8,
                cost_class=CapabilityCostClass.INCLUDED,
                provider="test-host",
                read_only_actions=frozenset({action}),
            ),
        )
    return LocalWorkflowRunner(ActionCoordinator(registry))


def _template(domain, template_id):
    _, templates = load_domain_package(ROOT / "domains" / domain)
    return next(item for item in templates if item.template_id == template_id)


def test_financial_writing_zero_cost_control_e2e_uses_external_domain_binding():
    links = AgentLinkRegistry.from_paths(ROOT / "config/AGENT_REGISTRY.json", ROOT / "state/TASK_INDEX.json")
    financial = links.resolve_agent("financial_writing")
    router = links.resolve_task("financial-writing:main")
    system_map = json.loads((ROOT / "config/SYSTEM_MAP.json").read_text(encoding="utf-8"))
    assert financial.repository == "D1traverser-debug/financial-writing-agent"
    assert financial.skill_ref == "UAOS_SKILL.md"
    assert financial.agent_manifest_ref == ".uaos/MANIFEST.json"
    assert financial.capability_ref == ".uaos/CAPABILITIES.json"
    assert financial.uaos_adapter_ref == ".uaos/ADAPTER.json"
    assert financial.parent_authority == "UAOS"
    assert router.domain_id == "financial_writing"
    assert router.task_type == "article_workspace_router"
    assert router.default_resume_within_domain is True
    assert links.authority_parent_map()["DOMAIN:financial_writing"] == "UAOS"
    assert system_map["domains"]["financial_writing"]["repository"] == financial.repository
    assert not (ROOT / "domains" / "financial_writing").exists()


def test_novel_zero_cost_control_e2e():
    template = _template("novel", "distill_and_create_v1")
    result = _runner_for(template).run(template, task_id="novel:e2e", external_inputs={"user_brief": "original novel", "source_corpus": "representative corpus"})
    assert result.status == "COMPLETE"
    assert set(template.delivery_outputs).issubset(result.objects)


def test_video_zero_cost_control_e2e_with_runtime_fanout():
    template = _template("video", "short_video_v1")
    task_id = "video:e2e"

    def hook(plan, unit, produced):
        if unit.work_unit_id != f"{task_id}:pre_generation_review":
            return plan
        keys = tuple(item["shot_id"] for item in produced["authorized_shot_specs"]["shots"])
        return expand_fanout(
            plan,
            source_unit_id=unit.work_unit_id,
            source_artifact="authorized_shot_specs",
            merge_unit_id=f"{task_id}:assemble_shots",
            item_keys=keys,
            child_name="Generate shot",
            executor_constraints=("video.generate_shot",),
            output_namespace="shot_artifact",
            new_plan_id=f"{task_id}:plan:fanout",
            risk="HIGH",
        )

    result = _runner_for(template, {"video.generate_shot"}).run(template, task_id=task_id, external_inputs={"user_brief": "representative short video"}, after_unit=hook)
    assert result.status == "COMPLETE"
    assert set(template.delivery_outputs).issubset(result.objects)


def test_ashare_premarket_zero_cost_control_e2e_with_runtime_fanout():
    template = _template("ashare", "premarket_v1")
    task_id = "ashare:e2e"

    def hook(plan, unit, produced):
        if unit.work_unit_id != f"{task_id}:recall":
            return plan
        return expand_fanout(
            plan,
            source_unit_id=unit.work_unit_id,
            source_artifact="candidate_universe",
            merge_unit_id=f"{task_id}:rank_candidates",
            item_keys=tuple(produced["candidate_universe"]),
            child_name="Analyze ticker",
            executor_constraints=("ashare.stock_analysis",),
            output_namespace="stock_analysis",
            new_plan_id=f"{task_id}:plan:fanout",
            risk="HIGH",
        )

    result = _runner_for(template, {"ashare.stock_analysis"}).run(template, task_id=task_id, external_inputs={"target_trading_day": "2026-10-14"}, after_unit=hook)
    assert result.status == "COMPLETE"
    assert set(template.delivery_outputs).issubset(result.objects)


def test_ashare_postclose_zero_cost_control_e2e():
    template = _template("ashare", "postclose_v1")
    result = _runner_for(template).run(template, task_id="ashare:postclose:e2e", external_inputs={"frozen_decision_ref": "decision:1", "target_trading_day": "2026-10-14"})
    assert result.status == "COMPLETE"
    assert set(template.delivery_outputs).issubset(result.objects)
