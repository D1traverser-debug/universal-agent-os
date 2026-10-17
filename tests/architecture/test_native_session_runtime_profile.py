import json
from pathlib import Path

from uaos.kernel import (
    ArchitectureCandidate,
    ArchitectureConcern,
    ArchitectureScenario,
    InputSignal,
    Representation,
    SignalKind,
    WalkthroughStep,
    require_architecture_experience_admission,
)
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


def test_current_agent_dogfood_and_recovery_admit_compiled_profile_architecture():
    concerns = (
        ArchitectureConcern("operability", "A native selected-context Agent consumes one effective hot-path profile instead of reconstructing several policy surfaces.", actor_operability_material=True),
        ArchitectureConcern("authority", "The runtime profile is generated projection only and canonical policy ownership remains singular.", structural_relationships_material=True),
        ArchitectureConcern("recovery", "Profile drift fails visibly and returns the session to canonical source policy rather than silently creating a second truth.", temporal_behavior_material=True),
    )
    dogfood = ArchitectureScenario(
        "native-session-repeated-correction",
        "CURRENT_AGENT_DOGFOOD",
        "Handle repeated user correction without promoting the latest framing directly into a repair.",
        "UAOS selected; native ChatGPT bootstrap completed",
        (
            WalkthroughStep("load-effective-profile", "CURRENT_AGENT", "load the compiled native runtime profile after CURRENT_SYSTEM", "one current hot-path projection is available", "reconstruct several policy documents ad hoc", "fall back to canonical source policies if projection drift is detected"),
            WalkthroughStep("classify-repeat", "CURRENT_AGENT", "apply projected correction/repeated-failure search-mode semantics", "repeated failure selects STRUCTURED evidence search", "treat the latest user or model theory as causal authority", "use projected cognition/search-mode contract and canonical evidence owners"),
            WalkthroughStep("act-only-after-admission", "CURRENT_AGENT", "select one bounded intervention only after falsification and evidence admission", "mutation is separated from diagnosis", "patch the first plausible layer", "apply projected mutation/closure rules and owner authority"),
        ),
        frozenset({"operability", "authority"}),
    )
    recovery = ArchitectureScenario(
        "native-profile-drift-recovery",
        "FAILURE_AND_RECOVERY",
        "Recover when canonical policy changes but the committed runtime projection is stale.",
        "source policy version or selected fields changed",
        (
            WalkthroughStep("detect-drift", "CI_OR_CURRENT_AGENT", "rebuild the projection from canonical policy and compare it with the committed profile", "drift is explicit rather than silently tolerated", "stale projection becomes a shadow authority", "fail CI or reread canonical source policies before material execution"),
        ),
        frozenset({"authority", "recovery"}),
    )
    receipt = require_architecture_experience_admission(
        signals=(
            InputSignal("goal", SignalKind.GOAL_OR_OUTCOME, "improve native-session adherence without another policy owner or false hard-enforcement claim"),
            InputSignal("user-analogy", SignalKind.EXAMPLE, "avoid patching one wall by breaking another", promoted_to_requirement=False),
        ),
        concerns=concerns,
        scenarios=(dogfood, recovery),
        representations=(
            Representation("COGNITIVE_WALKTHROUGH", frozenset({"operability"}), "test://native-session-runtime-profile"),
            Representation("AUTHORITY_MAP", frozenset({"authority"}), "test://compiled-projection-authority-boundary"),
            Representation("SEQUENCE", frozenset({"recovery"}), "test://profile-drift-recovery"),
        ),
        candidates=(
            ArchitectureCandidate("keep-distributed-hot-path", "Keep native execution assembled from current distributed authority surfaces.", frozenset({"operability", "authority", "recovery"}), ("tradeoff://observed-live-adherence-failure",), True),
            ArchitectureCandidate("add-more-rules", "Add another native cognition rule or incident-specific policy layer.", frozenset({"operability", "authority", "recovery"}), ("tradeoff://duplication-without-enforcement",)),
            ArchitectureCandidate("compiled-runtime-projection", "Compile one non-authoritative effective native profile from canonical sources and verify equality in CI.", frozenset({"operability", "authority", "recovery"}), ("tradeoff://generated-artifact-versus-lower-runtime-assembly-cost",)),
            ArchitectureCandidate("controlled-runtime-only", "Move all user-visible interaction to a host with mechanical UAOS input/output guardrails.", frozenset({"operability", "authority", "recovery"}), ("tradeoff://stronger-enforcement-versus-ux-deployment-cost",)),
        ),
        material_control_plane_or_agent_experience_change=True,
    )
    assert receipt.dogfood_present is True
    assert receipt.failure_recovery_scenario_ids == ("native-profile-drift-recovery",)
    assert receipt.candidate_ids == (
        "keep-distributed-hot-path",
        "add-more-rules",
        "compiled-runtime-projection",
        "controlled-runtime-only",
    )
    assert "user-analogy" in receipt.user_examples_kept_nonbinding
