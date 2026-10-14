from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class DomainBindingDrift(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class BindingPolicy:
    controller: str
    controller_ref: str
    required_adapter_status: str
    required_manifest_status: str

    @classmethod
    def from_path(cls, path: str | Path) -> "BindingPolicy":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            controller=data["controller"],
            controller_ref=data["controller_ref"],
            required_adapter_status=data["required_adapter_status"],
            required_manifest_status=data["required_manifest_status"],
        )

    def validate_domain_binding(
        self,
        *,
        registry_entry: Mapping[str, Any],
        adapter: Mapping[str, Any],
        manifest: Mapping[str, Any],
        skill_text: str,
    ) -> None:
        errors: list[str] = []
        if adapter.get("controller") != self.controller:
            errors.append("adapter controller")
        if adapter.get("status") != self.required_adapter_status:
            errors.append("adapter status")
        if manifest.get("controller") != self.controller:
            errors.append("manifest controller")
        if manifest.get("status") != self.required_manifest_status:
            errors.append("manifest status")
        if manifest.get("skill", {}).get("entrypoint") != registry_entry.get("skill_ref"):
            errors.append("skill entrypoint")
        binding = manifest.get("binding", {})
        if binding.get("controller_ref") != self.controller_ref:
            errors.append("manifest controller ref")
        if binding.get("adapter_ref") != registry_entry.get("uaos_adapter_ref"):
            errors.append("manifest adapter ref")
        if binding.get("capability_ref") != registry_entry.get("capability_ref"):
            errors.append("manifest capability ref")
        if self.controller not in skill_text:
            errors.append("skill controller marker")
        if any("continuity/" in str(registry_entry.get(field, "")) for field in ("skill_ref", "agent_manifest_ref", "capability_ref", "uaos_adapter_ref")):
            errors.append("retired continuity namespace in active registry")
        if errors:
            raise DomainBindingDrift("domain binding drift: " + ", ".join(errors))
