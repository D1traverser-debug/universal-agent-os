from pathlib import Path

from uaos.evolution import ProposalState, run_self_change_drill
from uaos.execution import ExecutionDisposition, ExecutionRequest, LocalWorkspaceExecutor

ROOT = Path(__file__).resolve().parents[1]


def test_retired_migration_runtime_is_absent_from_current_tree():
    retired = (
        ROOT / "src" / "uaos" / "migration",
        ROOT / "scripts" / "migrate_legacy_cutover.py",
        ROOT / "docs" / "migration",
    )
    assert [str(path.relative_to(ROOT)) for path in retired if path.exists()] == []


def test_active_runtime_source_has_no_old_controller_identifiers():
    forbidden = (
        "CONTINUITY_V3_7",
        "SINGLE_ACTIVE_CHAT",
        "MAINTENANCE_CONTROLLER_STATE",
        "resume_epoch",
        "legacy_protocol_ref",
        "legacy_source_refs",
        "MigrationDisposition",
        "LegacyTaskSeed",
    )
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
