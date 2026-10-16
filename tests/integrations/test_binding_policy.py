import json
from pathlib import Path

import pytest

from uaos.integrations import BindingPolicy, DomainBindingDrift

ROOT = Path(__file__).resolve().parents[2]
POLICY = BindingPolicy.from_path(ROOT / "config" / "BINDING_POLICY.json")
COMMON = json.loads((ROOT / "config" / "COMMON_CAPABILITIES.json").read_text(encoding="utf-8"))


def base_objects():
    registry = json.loads((ROOT / "config" / "AGENT_REGISTRY.json").read_text(encoding="utf-8"))["agents"][0]
    adapter = {"controller": "D1traverser-debug/universal-agent-os@main", "status": "UAOS_CONTROL_PLANE_ACTIVE"}
    manifest = {
        "controller": "D1traverser-debug/universal-agent-os@main",
        "status": "UAOS_CONTROL_PLANE_ACTIVE",
        "skill": {"entrypoint": registry["skill_ref"]},
        "binding": {
            "controller_ref": "D1traverser-debug/universal-agent-os@main:CURRENT_SYSTEM.json",
            "adapter_ref": registry["uaos_adapter_ref"],
            "capability_ref": registry["capability_ref"],
        },
    }
    required = [item["capability_id"] for item in COMMON["capabilities"]]
    capabilities = {
        "domain_id": registry["domain_id"],
        "uaos_common_capabilities_ref": "D1traverser-debug/universal-agent-os@main:config/COMMON_CAPABILITIES.json",
        "uaos_common_capabilities_contract_min": "1.6.0",
        "uaos_common_behavior_assurance_ref": "D1traverser-debug/universal-agent-os@main:config/COMMON_BEHAVIOR_ASSURANCE.json",
        "uaos_deliberation_policy_ref": "D1traverser-debug/universal-agent-os@main:config/DELIBERATION_POLICY.json",
        "common_capabilities_inheritance": "UAOS_HOSTED",
        "required_uaos_common_capabilities": required,
        "hosted_cognition_semantics": {
            "source": "CURRENT_UAOS_DELIBERATION_POLICY",
            "local_overrides": "NONE",
        },
    }
    skill = "Controller: `D1traverser-debug/universal-agent-os@main`."
    return registry, adapter, manifest, capabilities, skill


def validate(registry, adapter, manifest, capabilities, skill):
    POLICY.validate_domain_binding(
        registry_entry=registry,
        adapter=adapter,
        manifest=manifest,
        capabilities=capabilities,
        common_capabilities=COMMON,
        skill_text=skill,
    )


def test_consistent_binding_passes():
    validate(*base_objects())


def test_owner_native_work_plane_status_and_established_parent_aliases_pass():
    registry, adapter, manifest, capabilities, skill = base_objects()
    adapter = {
        "parent_control_plane": POLICY.controller,
        "status": "DIRECT_DOMAIN_WORK_PLANE_ACTIVE",
        "binding_status": POLICY.required_adapter_status,
    }
    manifest = {
        "parent_control_plane": POLICY.controller,
        "status": "DIRECT_DOMAIN_WORK_PLANE_ACTIVE",
        "binding_status": POLICY.required_manifest_status,
        "skill": {"entrypoint": registry["skill_ref"]},
        "binding": {
            "parent_system_ref": POLICY.controller_ref,
            "adapter_ref": registry["uaos_adapter_ref"],
            "capability_ref": registry["capability_ref"],
        },
    }
    validate(registry, adapter, manifest, capabilities, skill)


@pytest.mark.parametrize(
    "target",
    [
        "adapter_controller",
        "adapter_status",
        "manifest_controller",
        "manifest_status",
        "skill_path",
        "adapter_ref",
        "capability_ref",
        "skill_marker",
        "retired_registry_path",
        "capability_domain",
        "common_inheritance",
        "common_ref",
        "common_contract_min",
        "required_common_set",
        "deliberation_ref",
        "duplicated_cognition",
    ],
)
def test_binding_drift_fails_closed(target):
    registry, adapter, manifest, capabilities, skill = base_objects()
    registry = dict(registry)
    adapter = dict(adapter)
    manifest = json.loads(json.dumps(manifest))
    capabilities = json.loads(json.dumps(capabilities))
    if target == "adapter_controller":
        adapter["controller"] = "other"
    elif target == "adapter_status":
        adapter["status"] = "OLD"
    elif target == "manifest_controller":
        manifest["controller"] = "other"
    elif target == "manifest_status":
        manifest["status"] = "OLD"
    elif target == "skill_path":
        manifest["skill"]["entrypoint"] = "other.md"
    elif target == "adapter_ref":
        manifest["binding"]["adapter_ref"] = "other.json"
    elif target == "capability_ref":
        manifest["binding"]["capability_ref"] = "other.json"
    elif target == "skill_marker":
        skill = "no controller marker"
    elif target == "retired_registry_path":
        registry["uaos_adapter_ref"] = "continuity/UAOS_ADAPTER.json"
    elif target == "capability_domain":
        capabilities["domain_id"] = "wrong-domain"
    elif target == "common_inheritance":
        capabilities["common_capabilities_inheritance"] = "LOCAL_COPY"
    elif target == "common_ref":
        capabilities["uaos_common_capabilities_ref"] = "old/common.json"
    elif target == "common_contract_min":
        capabilities["uaos_common_capabilities_contract_min"] = "99.0.0"
    elif target == "required_common_set":
        capabilities["required_uaos_common_capabilities"].append("missing-parent-capability")
    elif target == "deliberation_ref":
        capabilities["uaos_deliberation_policy_ref"] = "old/deliberation.json"
    elif target == "duplicated_cognition":
        capabilities["hosted_cognition_semantics"] = {
            "source": "CURRENT_UAOS_DELIBERATION_POLICY",
            "rule": "EVERY_DETECTED_PROBLEM_REQUIRES_RESEARCH_AND_REFLECTION",
        }
    with pytest.raises(DomainBindingDrift):
        validate(registry, adapter, manifest, capabilities, skill)


def test_parent_cognition_is_referenced_not_reimplemented_in_child_capability_handshake():
    _, _, _, capabilities, _ = base_objects()
    hosted = capabilities["hosted_cognition_semantics"]
    assert hosted == {"source": "CURRENT_UAOS_DELIBERATION_POLICY", "local_overrides": "NONE"}
    assert "problem_response_floor" not in capabilities
    assert "problem_response_rule" not in capabilities
