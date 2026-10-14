import hashlib
import json
from pathlib import Path

import pytest

from uaos.evolution import ProposalState, run_self_change_drill
from uaos.execution import ExecutionDisposition, ExecutionRequest, LocalWorkspaceExecutor
from uaos.migration import LegacyControlRejected, LegacyRecord, SelectiveLegacyImporter
from uaos.state import SQLiteVersionedRepository

ROOT = Path(__file__).resolve().parents[1]


def _git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def _bundle():
    return json.loads((ROOT / "docs" / "migration" / "LEGACY_CUTOVER_V1.json").read_text(encoding="utf-8"))


def test_legacy_requirement_is_the_exact_frozen_blob():
    bundle = _bundle()
    requirement = next(item for item in bundle["records"] if item["record_type"] == "REQUIREMENT")
    data = (ROOT / requirement["payload"]["target_ref"]).read_bytes()
    assert _git_blob_sha(data) == requirement["payload"]["git_blob_sha"] == "2f51531a0f34bc7fe59e022d3c70c454c5608453"


def test_selective_cutover_is_idempotent_and_keeps_provenance(tmp_path):
    bundle = _bundle()
    records = tuple(LegacyRecord(item["record_id"], item["record_type"], item["source_ref"], item["payload"]) for item in bundle["records"])
    importer = SelectiveLegacyImporter(tmp_path / "uaos.db")
    first = importer.import_records(records)
    second = importer.import_records(records)
    assert len(first.imported_ids) == len(records)
    assert len(second.already_present_ids) == len(records)
    stored = SQLiteVersionedRepository(tmp_path / "uaos.db", "migrated:requirement").get("requirements:clean-slate-v1.0")
    assert stored.value["source_ref"].endswith("03_frozen_requirements_spec_v1_0.md")


def test_legacy_control_machinery_is_rejected(tmp_path):
    importer = SelectiveLegacyImporter(tmp_path / "uaos.db")
    with pytest.raises(LegacyControlRejected):
        importer.import_records((LegacyRecord("lease:1", "WRITER_LEASE", "legacy:lease", {}),))


def test_new_runtime_source_has_no_old_control_identifiers():
    forbidden = ("CONTINUITY_V3_7", "SINGLE_ACTIVE_CHAT", "MAINTENANCE_CONTROLLER_STATE", "monitor_historical_issue_12_status")
    offenders = []
    for path in (ROOT / "src" / "uaos").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                offenders.append((str(path.relative_to(ROOT)), token))
    assert not offenders


def test_local_workspace_rejects_path_escape(tmp_path):
    executor = LocalWorkspaceExecutor(tmp_path / "root")
    outcome = executor.execute(ExecutionRequest("a", "local.write_text", "../escape.txt", {"content": "x"}))
    assert outcome.disposition is ExecutionDisposition.FAILED


def test_controlled_self_change_really_rolls_back_and_retires(tmp_path):
    result = run_self_change_drill(tmp_path / "drill", run_id="test")
    assert result.recommendation == "ROLLBACK"
    assert result.final_state is ProposalState.RETIRED
    assert result.ledger_events == 6
    assert (tmp_path / "drill" / "policy.txt").read_text(encoding="utf-8") == "mode=stable\n"
