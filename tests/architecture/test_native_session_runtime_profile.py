import json
from pathlib import Path

from uaos.runtime.native_session_profile import build_native_session_runtime_profile


ROOT = Path(__file__).resolve().parents[2]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_committed_native_profile_is_exact_compiled_projection():
    expected = build_native_session_runtime_profile(
        session_policy=_json("config/SESSION_INTERACTION_POLICY.json"),
        deliberation_policy=_json("config/DELIBERATION_POLICY.json"),
        host_profiles=_json("config/HOST_PROFILES.json"),
    )
    committed = _json("config/NATIVE_SESSION_RUNTIME_PROFILE.json")
    assert committed == expected


def test_native_profile_is_projection_not_second_policy_authority():
    profile = _json("config/NATIVE_SESSION_RUNTIME_PROFILE.json")
    assert profile["projection_role"] == "COMPILED_EFFECTIVE_RUNTIME_PROJECTION__NON_AUTHORITATIVE"
    assert profile["turn_contract"]["cognition"]["canonical_ref"] == "config/DELIBERATION_POLICY.json#cognition_kernel"
    assert profile["assurance"]["semantic_signals"].startswith("BEHAVIORAL_SESSION_SELF_CLASSIFICATION")
    assert "NO_VERIFIED_CHATGPT_PRE_SEND_HOOK" in profile["assurance"]["final_response"]


def test_native_profile_exposes_repeated_correction_without_new_semantics():
    profile = _json("config/NATIVE_SESSION_RUNTIME_PROFILE.json")
    modes = profile["turn_contract"]["cognition"]["search_modes"]
    assert "USER_CORRECTION" in modes["CONTRASTIVE"]["use_when"]
    assert "REPEATED" in modes["STRUCTURED"]["use_when"]
    assert "three action candidates" in modes["STRUCTURED"]["minimum"]
    assert "NO_CHANGE" in modes["STRUCTURED"]["minimum"]
    assert "cannot by itself support" in profile["turn_contract"]["cognition"]["claim_rule"]


def test_native_profile_has_context_budget_and_free_first_cost_policy():
    path = ROOT / "config/NATIVE_SESSION_RUNTIME_PROFILE.json"
    assert len(path.read_text(encoding="utf-8")) <= 12000
    profile = _json("config/NATIVE_SESSION_RUNTIME_PROFILE.json")
    assert profile["assurance"]["cost"] == "INCLUDED_FREE_FIRST__PAID_AND_UNKNOWN_DENY_BY_DEFAULT"


def test_native_host_and_fresh_chat_bootstrap_prefer_compiled_profile():
    host = _json("config/HOST_PROFILES.json")["profiles"]["CHATGPT_GITHUB"]
    current = _json("CURRENT_SYSTEM.json")
    assert host["native_session_runtime_profile"] == "config/NATIVE_SESSION_RUNTIME_PROFILE.json"
    assert "COMPILED_EFFECTIVE_RUNTIME_PROJECTION" in host["native_session_runtime_profile_role"]
    assert "NATIVE_SESSION_RUNTIME_PROFILE.json" in current["fresh_chat_bootstrap"]["native_session_runtime_profile"]
    assert "NON_AUTHORITATIVE" in current["fresh_chat_bootstrap"]["native_session_runtime_profile"]
    assert "native_session_runtime_profile_builder" in current["runtime"]
