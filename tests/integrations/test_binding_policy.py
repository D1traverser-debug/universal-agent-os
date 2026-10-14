import json
from pathlib import Path

import pytest

from uaos.integrations import BindingPolicy, DomainBindingDrift

ROOT = Path(__file__).resolve().parents[2]
POLICY = BindingPolicy.from_path(ROOT / "config" / "BINDING_POLICY.json")


def base_objects():
    registry = json.loads((ROOT / "config" / "AGENT_REGISTRY.json").read_text(encoding="utf-8"))["agents"][0]
    adapter = {"controller": "D1traverser-debug/universal-agent-os@main", "status": "UAOS_CONTROL_PLANE_ACTIVE"}
    manifest = {
        "controller": "D1traverser-debug/universal-agent-os@main",
        "status": "UAOS_CONTROL_PLANE_ACTIVE",
        "skill": {"entrypoint": registry["skill_ref"]},
        "continuity": {
            "controller_ref": "D1traverser-debug/universal-agent-os@main:CURRENT_SYSTEM.json",
            "uaos_adapter_ref": registry["uaos_adapter_ref"],
        },
    }
    skill = "Controller: `D1traverser-debug/universal-agent-os@main`."
    return registry, adapter, manifest, skill


def test_consistent_binding_passes():
    POLICY.validate_domain_binding(registry_entry=base_objects()[0], adapter=base_objects()[1], manifest=base_objects()[2], skill_text=base_objects()[3])


@pytest.mark.parametrize("target", ["adapter_controller", "adapter_status", "manifest_controller", "manifest_status", "skill_path", "adapter_ref", "skill_marker"])
def test_binding_drift_fails_closed(target):
    registry, adapter, manifest, skill = base_objects()
    registry = dict(registry); adapter = dict(adapter); manifest = json.loads(json.dumps(manifest))
    if target == "adapter_controller": adapter["controller"] = "other"
    elif target == "adapter_status": adapter["status"] = "OLD"
    elif target == "manifest_controller": manifest["controller"] = "other"
    elif target == "manifest_status": manifest["status"] = "OLD"
    elif target == "skill_path": manifest["skill"]["entrypoint"] = "other.md"
    elif target == "adapter_ref": manifest["continuity"]["uaos_adapter_ref"] = "other.json"
    elif target == "skill_marker": skill = "no controller marker"
    with pytest.raises(DomainBindingDrift):
        POLICY.validate_domain_binding(registry_entry=registry, adapter=adapter, manifest=manifest, skill_text=skill)
