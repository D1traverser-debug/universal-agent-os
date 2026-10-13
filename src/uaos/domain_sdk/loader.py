from __future__ import annotations
import json
from pathlib import Path
from uaos.contracts.enums import IntentType, WorkStatus
from .manifest import DomainManifest, WorkflowRoute
from .workflows import WorkflowTemplate, WorkUnitTemplate

def load_domain_package(path: Path) -> tuple[DomainManifest, tuple[WorkflowTemplate, ...]]:
    manifest_data = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    routes = tuple(
        WorkflowRoute(IntentType(item["intent"]), item["task_type"], item["template_id"])
        for item in manifest_data.get("routes", [])
    )
    manifest = DomainManifest(
        domain_id=manifest_data["domain_id"],
        version=manifest_data["version"],
        owner=manifest_data["owner"],
        capabilities=tuple(manifest_data.get("capabilities", [])),
        workflow_template_ids=tuple(manifest_data.get("workflow_template_ids", [])),
        routes=routes,
        knowledge_namespaces=tuple(manifest_data.get("knowledge_namespaces", [])),
        required_tools=tuple(manifest_data.get("required_tools", [])),
        eval_suites=tuple(manifest_data.get("eval_suites", [])),
        dependencies=tuple(manifest_data.get("dependencies", [])),
        risk_profile=manifest_data.get("risk_profile", {}),
        legacy_refs=tuple(manifest_data.get("legacy_refs", [])),
    )
    templates=[]
    for template_id in manifest.workflow_template_ids:
        data=json.loads((path / f"{template_id}.json").read_text(encoding="utf-8"))
        units=tuple(WorkUnitTemplate(
            unit_id=u["unit_id"],name=u["name"],
            dependencies=tuple(u.get("dependencies",[])),
            required_inputs=tuple(u.get("required_inputs",[])),
            expected_outputs=tuple(u.get("expected_outputs",[])),
            executor_constraints=tuple(u.get("executor_constraints",[])),
            risk=u.get("risk","LOW"),
            initial_status=WorkStatus(u.get("initial_status","PENDING")),
        ) for u in data["units"])
        templates.append(WorkflowTemplate(
            template_id=data["template_id"], description=data["description"], units=units,
            external_inputs=tuple(data.get("external_inputs",[])),
            delivery_outputs=tuple(data.get("delivery_outputs",[]))
        ))
    return manifest, tuple(templates)
