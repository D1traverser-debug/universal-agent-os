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
    "config/SYSTEM_MAP.json",
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

    valid_admissions: list[tuple[str, str]] = []
    for task_path in task_changes:
        task = _json(task_path)
        if task.get("authority_context") != "UAOS" or task.get("task_type") != "controller_maintenance":
            continue
        evolution_ref = task.get("evolution_ref")
        if evolution_ref not in evolution_changes:
            continue
        evolution = _json(evolution_ref)
        implementation_refs = set(evolution.get("implementation_refs", []))
        if task_path not in implementation_refs:
            continue
        if not protected.issubset(implementation_refs):
            continue
        valid_admissions.append((task_path, evolution_ref))

    assert valid_admissions, (
        "native control-plane change lacks a linked UAOS controller-maintenance admission: a changed task must "
        "explicitly reference a changed evolution record, and that evolution must trace both the task and every "
        f"protected changed file. protected={sorted(protected)} task_changes={task_changes} "
        f"evolution_changes={evolution_changes}"
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
