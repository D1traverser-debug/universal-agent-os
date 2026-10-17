import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

PROTECTED_NATIVE_CONTROL_PLANE = {
    "config/INTENT_RESOLUTION_POLICY.json",
    "config/SESSION_INTERACTION_POLICY.json",
    "config/DELIBERATION_POLICY.json",
    "config/HOST_PROFILES.json",
    "config/NATIVE_SESSION_RUNTIME_PROFILE.json",
    "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md",
    "skills/uaos-controller-runtime/SKILL.md",
    "src/uaos/runtime/native_session_profile.py",
    "src/uaos/runtime/native_runtime_skill.py",
}


def _changed_paths() -> set[str]:
    try:
        parents = subprocess.check_output(
            ["git", "rev-list", "--parents", "-n", "1", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip().split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("git history unavailable; native control-plane diff admission is a VCS/CI gate")

    if len(parents) < 2:
        return set()
    base = parents[1]
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", base, "HEAD"],
        cwd=ROOT,
        text=True,
    )
    return {line.strip() for line in changed.splitlines() if line.strip()}


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_material_native_control_plane_change_carries_durable_evolution_and_task_admission():
    changed = _changed_paths()
    protected = changed & PROTECTED_NATIVE_CONTROL_PLANE
    if not protected:
        return

    evolution_changes = sorted(path for path in changed if path.startswith("state/evolution/") and path.endswith(".json"))
    task_changes = sorted(path for path in changed if path.startswith("state/tasks/") and path.endswith(".json"))

    assert evolution_changes, (
        "native control-plane semantics changed without a same-candidate durable EvolutionTransaction update: "
        f"{sorted(protected)}"
    )
    assert task_changes, (
        "native control-plane semantics changed without a same-candidate controller task/admission update: "
        f"{sorted(protected)}"
    )

    implementation_refs: set[str] = set()
    for path in evolution_changes:
        data = _json(path)
        implementation_refs.update(data.get("implementation_refs", []))

    missing_trace = sorted(path for path in protected if path not in implementation_refs)
    assert not missing_trace, (
        "native control-plane changed files are not traceable from the changed evolution evidence: "
        f"{missing_trace}"
    )


def test_generated_runtime_skill_is_not_a_hand_edit_escape_hatch():
    changed = _changed_paths()
    if "skills/uaos-controller-runtime/SKILL.md" not in changed:
        return
    assert "src/uaos/runtime/native_runtime_skill.py" in changed or any(
        path in changed
        for path in (
            "config/INTENT_RESOLUTION_POLICY.json",
            "config/SESSION_INTERACTION_POLICY.json",
            "config/DELIBERATION_POLICY.json",
            "config/EVOLUTION_POLICY.json",
            "config/HOST_PROFILES.json",
        )
    ), "runtime Skill changed without a canonical source or generator change"
