import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_session_policy_requires_user_independent_execution_depth_routing():
    policy = _json("config/SESSION_INTERACTION_POLICY.json")
    sentinel = policy["always_on_execution_depth_sentinel"]
    assert sentinel["required"] is True
    assert "EVERY_ASSISTANT_TURN" in sentinel["scope"]
    assert "user is not responsible" in sentinel["responsibility"].lower()
    checks = " ".join(sentinel["checks"]).lower()
    assert "not as the only path" in checks
    assert "ordinary structured" in checks
    assert "assess_deep_task_requirement" in sentinel["assessment_ref"]


def test_chatgpt_pointer_is_activation_not_shadow_policy():
    text = (ROOT / "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")
    lower = text.lower()
    assert "for every request, independently assess" in lower
    assert "mandatory escalation signal, not the only trigger" in lower
    assert "user is not the classifier" in lower
    assert "bootstrap/activation guidance only and non-authoritative" in lower
    # Detailed Deep Task evidence dimensions belong to repository authority, not the account pointer.
    recommended = text.split("## Recommended Custom Instructions", 1)[1].split("Do not paste", 1)[0].lower()
    assert "professional-practice gap" not in recommended
    assert "holdout/replay" not in recommended


def test_host_and_projection_preserve_native_chatgpt_boundary():
    hosts = _json("config/HOST_PROFILES.json")["profiles"]["CHATGPT_GITHUB"]
    current = _json("CURRENT_SYSTEM.json")
    assert "EVERY_SELECTED_CONTEXT_TURN" in hosts["session_execution_depth_routing"]
    assert "NO_VERIFIED_REPOSITORY_CONTROLLED_NON_BYPASSABLE_SIGNAL_INJECTOR" in hosts["semantic_signal_assurance"]
    assert "execution_depth_detection_sentinel" in current["fresh_chat_bootstrap"]
    assert current["physical_complete_mediation_assurance"] == "CONTROLLED_RUNTIME_GATE_VERIFIED__NATIVE_CHATGPT_COMPLETE_MEDIATION_NOT_CLAIMED"
