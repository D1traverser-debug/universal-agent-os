"""Replay a *visible real* UAOS response and check post-promotion evidence closure.

These tests are deliberately NOT claims that native ChatGPT invokes UAOS Python.
They assert reproducible repository-side detection of already observed failures.
"""

import json
from pathlib import Path

from uaos.observability.session_adherence import (
    SessionAdherenceViolation,
    SessionProgressExpectation,
    evaluate_session_progress_response,
)

ROOT = Path(__file__).resolve().parents[2]


def _observation(name: str) -> dict:
    return json.loads((ROOT / "state" / "observations" / name).read_text(encoding="utf-8"))


def test_actual_previous_native_reply_fails_mandatory_progress_contract():
    evidence = _observation("native-cognition-progress-replay-20261018.json")
    assert evidence["source_kind"] == "CURRENT_CHAT_VISIBLE_ASSISTANT_OUTPUT__REPOSITORY_CODE_AND_PRODUCTION_METADATA"
    result = evaluate_session_progress_response(
        evidence["replay_assistant_excerpt"],
        SessionProgressExpectation(context_selected=True, problem_signal_observed=True),
    )
    assert not result.passed
    assert SessionAdherenceViolation.MISSING_REQUIRED_FIELD in result.violations
    assert len(result.missing_fields) >= 1
    assert evidence["verification_boundary"]["positive_native_trigger_proof"] == "NOT_ESTABLISHED"


def test_progress_evaluator_can_accept_a_valid_positive_structural_control():
    # Synthetic positive control for parser discrimination; not a live trigger success.
    response = """当前 Agent：UAOS
当前范围：live replay
Authority：UAOS
状态：REPLAYED
当前阶段：VERIFICATION
下一动作：生产再读取证
Evolution：EVALUATED_NO_DURABLE_EVOLUTION
Deliberation：TRIGGERED__REPLAY
版本：UAOS 2.8.0
进度时间：2026-10-18 14:07:06（北京时间）
"""
    result = evaluate_session_progress_response(
        response,
        SessionProgressExpectation(context_selected=True, problem_signal_observed=True),
    )
    assert result.passed
    assert not result.missing_fields


def test_observation_must_not_remain_pending_after_exact_promotion_and_ci():
    observation = _observation("native-account-asset-continuity-20261018.json")
    production = observation["production_verification"]
    assert production["merged"] is True
    assert production["production_commit"] == "7d9c8f6df7b4006dbcfca5dc1f6351048aeabbff"
    assert production["production_ci_run_number"] == 561
    assert production["production_ci_result"] == "success"
    assert observation["status"] == "PRODUCTION_VERIFIED__NATIVE_RUNTIME_ACTIVATION_UNVERIFIED"
    assert production["runtime_behavior"] == "NOT_EVALUATED_BY_THIS_CI"


def test_live_native_failure_evidence_cannot_be_passed_off_as_stability_proof():
    evidence = _observation("native-cognition-progress-replay-20261018.json")
    assert evidence["result"].startswith("NATIVE_STABILITY_UNVERIFIED")
    assert "GITHUB_CI" in evidence["verification_boundary"]["independent_judge"]
    assert evidence["evolution_disposition"].startswith("EVALUATED_NO_DURABLE_EVOLUTION")
    assert len(evidence["causal_candidates"]) >= 3
    assert {v["id"] for v in evidence["intervention_candidates"]} >= {
        "DO_NOTHING", "ADD_MORE_INSTRUCTIONS",
        "RECONCILE_PRODUCTION_OBSERVATION_AND_RUN_REAL_RESPONSE_REPLAY_WITH_NEGATIVE_CONTROLS",
    }
