from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping
from uaos.contracts.enums import IntentType

RESERVED_INFRASTRUCTURE_CAPABILITIES = frozenset({
    "continuity.runtime",
    "action.authority",
    "knowledge.lifecycle",
    "system.maintenance",
    "assurance.completion",
})

@dataclass(frozen=True, slots=True)
class WorkflowRoute:
    intent: IntentType
    task_type: str
    template_id: str

    def __post_init__(self) -> None:
        if not self.task_type.strip() or not self.template_id.strip():
            raise ValueError("task_type and template_id are required")
        if self.intent is not IntentType.NEW_TASK:
            raise ValueError("domain workflow routes may only create NEW_TASK workflows; CONTINUE and maintenance use shared control-plane paths")

@dataclass(frozen=True, slots=True)
class DomainManifest:
    domain_id: str
    version: str
    owner: str
    capabilities: tuple[str, ...]
    workflow_template_ids: tuple[str, ...]
    routes: tuple[WorkflowRoute, ...]
    knowledge_namespaces: tuple[str, ...] = ()
    required_tools: tuple[str, ...] = ()
    eval_suites: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    risk_profile: Mapping[str, str] = field(default_factory=dict)
    legacy_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all((self.domain_id.strip(), self.version.strip(), self.owner.strip())):
            raise ValueError("domain_id, version and owner are required")
        for label, values in (
            ("capabilities", self.capabilities),
            ("workflow_template_ids", self.workflow_template_ids),
            ("knowledge_namespaces", self.knowledge_namespaces),
        ):
            if len(set(values)) != len(values):
                raise ValueError(f"duplicate {label}")
        reserved = RESERVED_INFRASTRUCTURE_CAPABILITIES.intersection(self.capabilities)
        if reserved:
            raise ValueError(f"domain may not redefine shared infrastructure capabilities: {sorted(reserved)}")
        route_keys = [(r.intent, r.task_type) for r in self.routes]
        if len(route_keys) != len(set(route_keys)):
            raise ValueError("duplicate domain workflow route")
        unknown_templates = {r.template_id for r in self.routes} - set(self.workflow_template_ids)
        if unknown_templates:
            raise ValueError(f"route references undeclared templates: {sorted(unknown_templates)}")
