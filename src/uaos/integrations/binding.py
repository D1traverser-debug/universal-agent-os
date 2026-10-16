from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class DomainBindingDrift(RuntimeError):
    pass


def _version_tuple(value: str) -> tuple[int, ...]:
    try:
        parts = tuple(int(part) for part in value.strip().split("."))
    except (AttributeError, ValueError) as exc:
        raise DomainBindingDrift(f"invalid semantic version: {value!r}") from exc
    if not parts:
        raise DomainBindingDrift(f"invalid semantic version: {value!r}")
    return parts


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

    @property
    def common_capabilities_ref(self) -> str:
        return f"{self.controller}:config/COMMON_CAPABILITIES.json"

    @property
    def common_behavior_ref(self) -> str:
        return f"{self.controller}:config/COMMON_BEHAVIOR_ASSURANCE.json"

    @property
    def deliberation_policy_ref(self) -> str:
        return f"{self.controller}:config/DELIBERATION_POLICY.json"

    def validate_domain_binding(
        self,
        *,
        registry_entry: Mapping[str, Any],
        adapter: Mapping[str, Any],
        manifest: Mapping[str, Any],
        capabilities: Mapping[str, Any],
        common_capabilities: Mapping[str, Any],
        skill_text: str,
    ) -> None:
        """Fail closed when a registered child cannot inherit current UAOS semantics.

        The binding contract intentionally validates both structural pointers and the
        minimum common-capability handshake.  Parent cognition semantics are owned by
        DELIBERATION_POLICY; children may point to that owner but must not freeze a
        competing copy of the problem-response algorithm in CAPABILITIES.json.
        """

        errors: list[str] = []
        domain_id = str(registry_entry.get("domain_id", "")).strip()

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
        if any(
            "continuity/" in str(registry_entry.get(field, ""))
            for field in ("skill_ref", "agent_manifest_ref", "capability_ref", "uaos_adapter_ref")
        ):
            errors.append("retired continuity namespace in active registry")

        if capabilities.get("domain_id") != domain_id:
            errors.append("capability domain match")

        inheritance = str(capabilities.get("common_capabilities_inheritance", ""))
        if not inheritance.startswith("UAOS_HOSTED"):
            errors.append("capability common inheritance")

        if capabilities.get("uaos_common_capabilities_ref") != self.common_capabilities_ref:
            errors.append("capability common capabilities ref")

        behavior_ref = capabilities.get("uaos_common_behavior_assurance_ref")
        if behavior_ref is not None and behavior_ref != self.common_behavior_ref:
            errors.append("capability common behavior ref")

        current_common_version = str(common_capabilities.get("contract_version", "")).strip()
        min_common = (
            capabilities.get("uaos_common_capabilities_contract_min")
            or capabilities.get("uaos_common_capabilities_min")
        )
        if min_common is not None:
            try:
                if _version_tuple(current_common_version) < _version_tuple(str(min_common)):
                    errors.append("capability common contract minimum")
            except DomainBindingDrift:
                errors.append("capability common contract version")

        current_common_ids = {
            str(item.get("capability_id", "")).strip()
            for item in common_capabilities.get("capabilities", ())
            if str(item.get("capability_id", "")).strip()
        }
        required_common = tuple(capabilities.get("required_uaos_common_capabilities", ()) or ())
        missing_common = sorted({str(item).strip() for item in required_common if str(item).strip()} - current_common_ids)
        if missing_common:
            errors.append("capability required common set: " + ", ".join(missing_common))

        # A child that claims the parent adaptive-deliberation capability must bind
        # to the live parent owner rather than preserve a local algorithm snapshot.
        claims_adaptive = "adaptive_deliberation_and_parent_guidance" in set(required_common)
        copied_cognition = any(
            key in capabilities
            for key in ("problem_response_floor", "problem_response_rule")
        )
        hosted_cognition = capabilities.get("hosted_cognition_semantics")
        if hosted_cognition is not None:
            claims_adaptive = True
            if not isinstance(hosted_cognition, Mapping):
                errors.append("capability hosted cognition semantics")
            else:
                if hosted_cognition.get("source") != "CURRENT_UAOS_DELIBERATION_POLICY":
                    errors.append("capability cognition source")
                if "rule" in hosted_cognition or "problem_response_floor" in hosted_cognition:
                    errors.append("capability duplicated cognition semantics")
        if copied_cognition:
            claims_adaptive = True
            errors.append("capability duplicated cognition semantics")
        if claims_adaptive and capabilities.get("uaos_deliberation_policy_ref") != self.deliberation_policy_ref:
            errors.append("capability deliberation policy ref")

        if errors:
            raise DomainBindingDrift("domain binding drift: " + ", ".join(errors))
