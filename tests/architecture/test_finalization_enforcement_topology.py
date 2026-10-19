import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_chatgpt_host_does_not_claim_a_verified_pre_send_gate():
    profiles = json.loads((ROOT / "config/HOST_PROFILES.json").read_text(encoding="utf-8"))["profiles"]
    chatgpt = profiles["CHATGPT_GITHUB"]
    assert "NO_VERIFIED_CHATGPT_PRE_SEND_HOOK" in chatgpt["final_response_enforcement"]
    assert chatgpt["custom_instructions_role"] == "BOOTSTRAP_ONLY__NON_AUTHORITATIVE"
    assert chatgpt["uaos_finalization_gate_ref"] == "src/uaos/runtime/finalization.py"


def test_openai_agents_host_exposes_blocking_output_guardrail_path():
    profiles = json.loads((ROOT / "config/HOST_PROFILES.json").read_text(encoding="utf-8"))["profiles"]
    agents = profiles["OPENAI_AGENTS_SDK"]
    assert agents["final_response_enforcement"] == "USER_VISIBLE_ADAPTER_INLINE_FINALIZATION_MANDATORY__SDK_GUARDRAIL_OPTIONAL_DEFENSE_IN_DEPTH"
    assert "NOT_NATIVE_CHATGPT" in agents["enforcement_scope"]
    assert "user_visible=True" in agents["user_visible_delivery_contract"]
    assert agents["output_guardrail_builder"].endswith("#build_uaos_output_guardrail")


def test_custom_instruction_pointer_is_bootstrap_not_a_policy_copy():
    text = (ROOT / "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")
    lower = text.lower()
    assert "bootstrap from `d1traverser-debug/universal-agent-os@main:entrypoint.md`" in lower
    assert "bootstrap-only" in lower
    assert "non-authoritative" in lower
    assert "while the governing objective is unfinished" in lower
    assert "no genuine user-input, authorization, safety, budget, capability, or external blocker exists" in lower
    assert "choose the next evidence-supported action, execute, verify, reassess, and continue" in lower
    assert "do not prove a repository-controlled chatgpt pre-send/pre-tool hook" in lower
    assert "do not paste the full cognition kernel" in lower
