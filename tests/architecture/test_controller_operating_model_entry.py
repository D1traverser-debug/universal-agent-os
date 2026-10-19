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
    assert "flaws in the controller's own answer or method" in entry
    assert "Continue authorized work" in entry
    assert "state/TASK_INDEX.json" in entry
    assert "config/RETRIEVAL_POLICY.json#knowledge_inventory_routing" in entry
    assert "docs/adr/0030-controller-role-state-context-operating-model.md" in entry


def test_operating_model_has_one_owner_and_does_not_shadow_existing_kernel():
    entry = _read("ENTRYPOINT.md")
    policy = _j("config/SESSION_INTERACTION_POLICY.json")
    task = _j("state/tasks/uaos-inheritance-review-20261018.json")
    assert policy["mandatory_selected_context_entry"]["required"]
    assert "no second cognitive state machine" in entry
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
    assert "only affected owner rules, evidence, research and child sources" in entry
    assert "not exhaustive" in entry


def test_bootstrap_has_no_competing_status_value_after_source_lifecycle_changes():
    import re
    current = _j("CURRENT_SYSTEM.json")
    entry = _read("ENTRYPOINT.md")
    assert current["status"] == "ACTIVE_PRIMARY_CONTROLLER"
    assert "Status source: `CURRENT_SYSTEM.json#status`" in entry
    assert not re.search(r"^Status:\\s+`", entry, flags=re.MULTILINE)


def test_current_entry_and_selected_task_have_bounded_runtime_context_and_pinned_history():
    entry = _read("ENTRYPOINT.md")
    task_text = _read("state/tasks/uaos-inheritance-review-20261018.json")
    task = json.loads(task_text)
    assert len(entry) <= 22000
    assert len(task_text) <= 45000
    assert "one integrated, adaptive work loop" in entry
    assert "one feedback process" in entry
    assert "Continue authorized work" in entry
    assert "native" in entry.lower()
    archive = task["historical_case_compaction_20261019"]["source_archive_ref"]
    assert "@d15dfcc885c1684915202a252add13b202f1e3e4:" in archive
    assert archive.endswith("state/tasks/uaos-inheritance-review-20261018.json")
    for key in task["historical_case_compaction_20261019"]["compacted_keys"]:
        current = task[key]
        assert current["status"]
        assert current["historical_detail_ref"] == archive + "#" + key
    assert task["status"] == "RUNNING"
    assert task["evolution_ref"] == "state/evolution/EVO-20261018-INHERITANCE-REVIEW.json"
