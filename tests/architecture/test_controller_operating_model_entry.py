"""Ensure the UAOS operating model is discoverable on the real boot entry.

This tests source wiring only. Native ChatGPT invocation requires observed chat traces.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _j(path):
    return json.loads(_read(path))


def test_controller_operating_contract_is_in_actual_bootstrap_entry():
    entry = _read("ENTRYPOINT.md")
    assert "## UAOS controller operating contract" in entry
    assert "## Intent before state" in entry
    assert entry.index("## UAOS controller operating contract") < entry.index("## Intent before state")
    assert "system architect, action coordinator, assurance steward" in entry
    assert "challenge assumptions INCLUDING the controller's own rules/methods" in entry
    assert "continue while authorized work remains" in entry
    assert "state/TASK_INDEX.json" in entry
    assert "state/observations/*" in entry
    assert "docs/adr/0030-controller-role-state-context-operating-model.md" in entry


def test_operating_model_has_one_owner_and_does_not_shadow_existing_kernel():
    entry = _read("ENTRYPOINT.md")
    policy = _j("config/SESSION_INTERACTION_POLICY.json")
    task = _j("state/tasks/uaos-inheritance-review-20261018.json")
    assert policy["mandatory_selected_context_entry"]["required"]
    assert "not a competing control plane" in entry
    assert task["controller_operating_model"]["entry_ref"].startswith("ENTRYPOINT.md#")
    assert task["status"] == "RUNNING"
    assert "runtime" not in task["controller_operating_model"]["owner"].lower()


def test_skill_installation_evidence_does_not_prove_source_or_behavior():
    evidence = _j("state/observations/native-account-install-handoff-20261018.json")
    task = _j("state/tasks/uaos-inheritance-review-20261018.json")
    assert "USER_CONFIRMED" in evidence["record_status"]
    assert evidence["installation_ui_evidence"]["visible_installed_item"] == "uaos controller runtime"
    assert "INSTALLED_BYTES_UNVERIFIED" in task["native_account_cutover"]["status"]
    assert "UNVERIFIED" in evidence["native_reliability"]
    assert evidence["canary"]["production_code_ci_is_native_proof"] is False
    assert evidence["canary"]["production_code_ci_is_native_proof"] is False


def test_no_full_document_loading_or_reupload_each_turn():
    entry = _read("ENTRYPOINT.md")
    assert "read `state/observations/*`, evolution transactions, research and ADRs only when" in entry
    assert "not as a mandatory full-document read on every turn" in entry
