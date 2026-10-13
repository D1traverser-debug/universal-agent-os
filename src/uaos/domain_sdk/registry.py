from __future__ import annotations
from uaos.contracts.enums import IntentType
from .manifest import DomainManifest
from .workflows import WorkflowTemplate

class DomainRouteNotFound(LookupError):
    pass

class DomainRegistry:
    def __init__(self) -> None:
        self._manifests: dict[str, DomainManifest] = {}
        self._templates: dict[tuple[str, str], WorkflowTemplate] = {}

    def register(self, manifest: DomainManifest, templates: tuple[WorkflowTemplate, ...]) -> None:
        if manifest.domain_id in self._manifests:
            raise ValueError(f"duplicate domain_id: {manifest.domain_id}")
        by_id = {template.template_id: template for template in templates}
        if set(by_id) != set(manifest.workflow_template_ids):
            missing = set(manifest.workflow_template_ids) - set(by_id)
            extra = set(by_id) - set(manifest.workflow_template_ids)
            raise ValueError(f"template registration mismatch missing={sorted(missing)} extra={sorted(extra)}")
        self._manifests[manifest.domain_id] = manifest
        for template_id, template in by_id.items():
            self._templates[(manifest.domain_id, template_id)] = template

    def manifest(self, domain_id: str) -> DomainManifest:
        try:
            return self._manifests[domain_id]
        except KeyError as exc:
            raise DomainRouteNotFound(f"unknown domain: {domain_id}") from exc

    def resolve_new_task(self, domain_id: str, *, intent: IntentType, task_type: str) -> WorkflowTemplate:
        manifest = self.manifest(domain_id)
        if intent is not IntentType.NEW_TASK:
            raise DomainRouteNotFound(
                f"intent {intent} does not create a new domain workflow; resume/requirement/maintenance are control-plane operations"
            )
        for route in manifest.routes:
            if route.intent is intent and route.task_type == task_type:
                return self._templates[(domain_id, route.template_id)]
        raise DomainRouteNotFound(f"no route for domain={domain_id} intent={intent} task_type={task_type}")
