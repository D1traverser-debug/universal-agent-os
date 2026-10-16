import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_turn_level_problem_detection_is_always_on():
    deliberation = _json("config/DELIBERATION_POLICY.json")
    sentinel = deliberation["always_on_problem_detection_sentinel"]
    assert sentinel["enabled"] is True
    assert "EVERY_ASSISTANT_TURN" in sentinel["scope"]

    session = _json("config/SESSION_INTERACTION_POLICY.json")
    session_sentinel = session["always_on_problem_detection_sentinel"]
    assert session_sentinel["required"] is True
    assert "EVERY_ASSISTANT_TURN" in session_sentinel["scope"]

    report = session["inherited_session_progress_report"]
    assert "must not be NOT_TRIGGERED" in report["deliberation_rule"]
    assert "NO_EVOLUTION_TRIGGER only when no problem" in report["evolution_rule"]


def test_entrypoint_release_matches_current_system():
    current = _json("CURRENT_SYSTEM.json")
    text = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    match = re.search(r"^System release: `([^`]+)`", text, re.MULTILINE)
    assert match is not None
    assert match.group(1) == current["system_release_version"]


def test_entrypoint_declares_turn_level_problem_detection():
    text = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8").lower()
    assert "problem detection lightweight and always on" in text
    assert "after authority selection" in text
