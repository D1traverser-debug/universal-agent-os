from pathlib import Path
import pytest
from uaos.contracts.enums import IntentType
from uaos.contracts.planning import execution_layers, validate_plan
from uaos.domain_sdk import (
    DomainManifest, DomainRegistry, DomainRouteNotFound,
    WorkflowTemplate, WorkUnitTemplate, load_domain_package
)

ROOT=Path(__file__).resolve().parents[1]
DOMAIN=ROOT/"domains"/"financial_writing"

def registry():
    manifest, templates=load_domain_package(DOMAIN)
    reg=DomainRegistry(); reg.register(manifest,templates); return reg,manifest,templates

def test_domain_cannot_redefine_shared_infrastructure():
    with pytest.raises(ValueError,match="infrastructure"):
        DomainManifest("bad","1","owner",("continuity.runtime",),(),(),())

def test_only_new_task_routes_create_business_workflow():
    reg,_,_=registry()
    template=reg.resolve_new_task("financial_writing",intent=IntentType.NEW_TASK,task_type="article")
    assert template.template_id=="article_v1"
    with pytest.raises(DomainRouteNotFound,match="control-plane"):
        reg.resolve_new_task("financial_writing",intent=IntentType.SYSTEM_MAINTENANCE,task_type="article")
    with pytest.raises(DomainRouteNotFound):
        reg.resolve_new_task("financial_writing",intent=IntentType.CONTINUE,task_type="article")

def test_financial_plan_is_valid_and_task_isolated():
    reg,_,_=registry()
    template=reg.resolve_new_task("financial_writing",intent=IntentType.NEW_TASK,task_type="article")
    p1=template.compile(task_id="article-1",plan_id="p1")
    p2=template.compile(task_id="article-2",plan_id="p2")
    validate_plan(p1); validate_plan(p2)
    assert set(u.work_unit_id for u in p1.work_units).isdisjoint(u.work_unit_id for u in p2.work_units)
    assert all(u.task_id=="article-1" for u in p1.work_units)

def test_financial_final_audit_inspects_rendered_documents_before_delivery():
    reg,_,_=registry()
    p=reg.resolve_new_task("financial_writing",intent=IntentType.NEW_TASK,task_type="article").compile(task_id="a",plan_id="p")
    by={u.work_unit_id.split(":",1)[1]:u for u in p.work_units}
    assert "a:render_documents" in by["mechanical_audit"].dependencies
    assert "a:mechanical_audit" in by["final_audit"].dependencies
    assert {"finance_broad_docx","finance_deep_docx"}.issubset(by["final_audit"].required_inputs)
    assert "a:final_audit" in by["deliver"].dependencies
    assert {"finance_broad_docx","finance_deep_docx","audit_docx","final_audit"}.issubset(by["deliver"].required_inputs)

def test_financial_required_delivery_outputs_have_real_producers():
    _,_,templates=registry()
    t=templates[0]
    produced={o for u in t.units for o in u.expected_outputs}
    assert set(t.delivery_outputs).issubset(produced)
    assert set(t.delivery_outputs)=={"finance_broad_docx","finance_deep_docx","audit_docx","delivery_receipt"}

def test_workflow_preserves_core_business_stages_but_not_legacy_runtime_state():
    _,_,templates=registry()
    unit_ids={u.unit_id for u in templates[0].units}
    expected={"research","research_audit","editorial","title","draft","editorial_audit","mechanical_audit","final_audit","deliver"}
    assert expected.issubset(unit_ids)
    layers=execution_layers(templates[0].compile(task_id="a",plan_id="p"))
    flattened=[x.split(":",1)[1] for layer in layers for x in layer]
    assert flattened.index("render_documents") < flattened.index("mechanical_audit") < flattened.index("final_audit") < flattened.index("deliver")
