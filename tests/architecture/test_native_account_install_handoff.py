"""Account installation is an external UI boundary; CI must not imply native activation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _git_blob(path: str) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def test_account_handoff_tracks_real_current_source_blobs():
    evidence = _read("state/observations/native-account-install-handoff-20261018.json")
    refs = evidence["source_git_blobs"]
    assert refs["skill"] == _git_blob("skills/uaos-controller-runtime/SKILL.md")
    assert refs["pointer"] == _git_blob("docs/integration/UAOS_CHATGPT_CUSTOM_INSTRUCTIONS.txt")
    assert refs["previously_supplied_skill"] != refs["skill"]
    assert evidence["source_refs"][0] == "skills/uaos-controller-runtime/SKILL.md"


def test_account_install_is_not_self_certified_from_git_ci():
    evidence = _read("state/observations/native-account-install-handoff-20261018.json")
    assert evidence["record_status"] == "ACCOUNT_SKILL_VISIBLE_INSTALLED__INSTALLED_VERSION_UNVERIFIED"
    assert evidence["installation_ui_evidence"]["visible_installed_item"] == "uaos controller runtime"
    assert evidence["installation_ui_evidence"]["visible_created_by_me_item"] == "uaos controller runtime"
    assert "not evidence of two" in evidence["installation_ui_evidence"]["inference"]
    assert evidence["native_reliability"] == "NATIVE_BEHAVIOR_UNVERIFIED"
    assert evidence["canary"]["status"].startswith("NOT_RUN")
    assert evidence["canary"]["production_code_ci_is_native_proof"] is False


def test_one_existing_owner_still_holds_controller_continuity():
    evidence = _read("state/observations/native-account-install-handoff-20261018.json")
    owner = _read(evidence["continued_parent_task_ref"])
    assert owner["status"] == "RUNNING"
    assert owner["authority_context"] == "UAOS"
    assert evidence["exact_scope"] == "UAOS_CONTROLLER_ONLY__CHILD_REPOS_UNMODIFIED"


def test_no_spurious_account_actions_from_uncertain_skill_state():
    evidence = _read("state/observations/native-account-install-handoff-20261018.json")
    actions = " ".join(evidence["no_user_actions_needed"]).lower()
    assert "main branch protection" in actions
    assert "reenter v3" in actions
    assert "library backup" in actions
