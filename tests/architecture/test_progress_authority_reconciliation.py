"""Progress is an authority-derived view, not an alternative task state store.

These tests check a controlled Python runtime only, never native ChatGPT interception.
"""
import json
import subprocess
import sys
from pathlib import Path

from uaos.observability.session_adherence import (
    SessionAdherenceViolation,
    SessionProgressExpectation,
    evaluate_session_progress_response,
)

ROOT = Path(__file__).resolve().parents[2]
TASK_REF = "state/tasks/uaos-inheritance-review-20261018.json"


def task():
    return json.loads((ROOT / TASK_REF).read_text(encoding="utf-8"))


def report(*, status=None, stage=None, authority=None):
    current = task()
    status = current["status"] if status is None else status
    stage = current["current_stage"] if stage is None else stage
    authority = current["authority_context"] if authority is None else authority
    return f"""当前 Agent：UAOS
当前范围或任务：{current['task_id']}
Authority：{authority}
状态：{status}
当前阶段：{stage}
下一动作或阻塞：继续有授权且可验证的总控治理
Evolution：EVALUATED_NO_DURABLE_EVOLUTION
Deliberation：TRIGGERED
版本：UAOS 2.8.0
进度时间：2026-10-18 22:16:00（北京时间）
"""


def trusted_reader(state_ref):
    if state_ref != TASK_REF:
        return None
    return task()


def test_false_done_report_is_rejected_against_exact_owner_task():
    bad = evaluate_session_progress_response(
        report(status="COMPLETE"),
        SessionProgressExpectation(context_selected=True, authoritative_task_ref=TASK_REF,
                                   read_authoritative_task=trusted_reader),
    )
    assert SessionAdherenceViolation.AUTHORITATIVE_PROGRESS_MISMATCH in bad.violations


def test_false_stage_or_authority_is_rejected_and_real_status_passes():
    for wrong in ({"stage": "PRODUCTION_COMPLETE"}, {"authority": "DOMAIN:financial_writing"}):
        bad = evaluate_session_progress_response(
            report(**wrong),
            SessionProgressExpectation(context_selected=True, authoritative_task_ref=TASK_REF,
                                       read_authoritative_task=trusted_reader),
        )
        assert SessionAdherenceViolation.AUTHORITATIVE_PROGRESS_MISMATCH in bad.violations
    good = evaluate_session_progress_response(
        report(),
        SessionProgressExpectation(context_selected=True, authoritative_task_ref=TASK_REF,
                                   read_authoritative_task=trusted_reader),
    )
    assert good.passed


def test_authority_binding_fails_closed_without_real_host_reader_or_matching_ref():
    absent = evaluate_session_progress_response(
        report(),
        SessionProgressExpectation(context_selected=True, authoritative_task_ref=TASK_REF),
    )
    assert SessionAdherenceViolation.UNVERIFIED_PROGRESS_AUTHORITY in absent.violations
    mismatch = evaluate_session_progress_response(
        report(),
        SessionProgressExpectation(context_selected=True,
                                   authoritative_task_ref="state/tasks/forged-task.json",
                                   read_authoritative_task=trusted_reader),
    )
    assert SessionAdherenceViolation.UNVERIFIED_PROGRESS_AUTHORITY in mismatch.violations


def test_status_script_reports_active_exact_task_separately_from_old_readiness():
    output = subprocess.check_output([sys.executable, "scripts/uaos_status.py"], cwd=ROOT, text=True)
    parsed = json.loads(output)
    current = task()
    index = json.loads((ROOT / "state/TASK_INDEX.json").read_text(encoding="utf-8"))
    default = [i for i in index["controller_tasks"] if i["default_resume"]]
    assert len(default) == 1
    assert parsed["current_task"]["task_id"] == current["task_id"] == default[0]["task_id"]
    assert parsed["current_task"]["status"] == current["status"]
    assert parsed["current_task"]["current_stage"] == current["current_stage"]
    assert parsed["readiness_snapshot"]["role"] == "HISTORICAL_ASSURANCE_ONLY__NOT_LIVE_TASK_STATE"
    assert parsed["readiness_snapshot"]["status"] != parsed["current_task"]["status"]


def test_parent_task_does_not_duplicate_mutable_skill_source_sha():
    active = task()
    observation_ref = active["native_account_cutover"]["observation_ref"]
    observation = json.loads((ROOT / observation_ref).read_text(encoding="utf-8"))
    assert "skill_source_sha" not in active["native_account_cutover"]
    assert observation["source_git_blobs"]["skill"] != observation["source_git_blobs"]["previously_supplied_skill"]
    assert observation["latest_repo_skill_generation_20261018"]["installed_skill_blob_status"].startswith("UNKNOWN")


def test_progress_identity_requires_exact_match_not_substring_or_negation():
    current = task()
    bad_labels = (
        f"not {current['task_id']}",
        f"another-task (see {current['task_id']})",
        f"{current['task_id']}/copy",
    )
    for label in bad_labels:
        fake = report().replace(
            f"当前范围或任务：{current['task_id']}",
            f"当前范围或任务：{label}",
        )
        receipt = evaluate_session_progress_response(
            fake,
            SessionProgressExpectation(
                context_selected=True, authoritative_task_ref=TASK_REF,
                read_authoritative_task=trusted_reader,
            ),
        )
        assert SessionAdherenceViolation.AUTHORITATIVE_PROGRESS_MISMATCH in receipt.violations


def test_status_cli_handles_controller_root_and_still_rejects_two_defaults(tmp_path, monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("uaos_status", ROOT / "scripts" / "uaos_status.py")
    assert spec and spec.loader
    uaos_status = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(uaos_status)
    monkeypatch.setattr(uaos_status, "ROOT", tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "docs" / "assurance").mkdir(parents=True)
    (tmp_path / "CURRENT_SYSTEM.json").write_text(
        json.dumps({"system_release_version": "test"}), encoding="utf-8"
    )
    (tmp_path / "docs" / "assurance" / "PRODUCTION_READINESS.json").write_text(
        json.dumps({"status": "historical-only"}), encoding="utf-8"
    )
    index_path = tmp_path / "state" / "TASK_INDEX.json"
    index_path.write_text(json.dumps({"controller_tasks": []}), encoding="utf-8")
    result = uaos_status.current_status()
    assert result["current_task"] is None
    assert result["readiness_snapshot"]["status"] == "historical-only"

    entries = [
        {"task_id": name, "resume_eligible": True, "default_resume": True}
        for name in ("test-one", "test-two")
    ]
    index_path.write_text(json.dumps({"controller_tasks": entries}), encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="ambiguous"):
        uaos_status.current_status()
