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
    assert agents["final_response_enforcement"] == "BLOCKING_OUTPUT_GUARDRAIL_WHEN_UAOS_GUARDRAIL_IS_ATTACHED"
    assert agents["output_guardrail_builder"].endswith("#build_uaos_output_guardrail")


def test_custom_instruction_pointer_is_bootstrap_not_a_policy_copy():
    text = (ROOT / "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")
    assert "bootstrap from `D1traverser-debug/universal-agent-os@main:ENTRYPOINT.md`" in text
    assert "never use `next` or another no-op user message as the workflow clock" in text
    assert "do not prove that the ChatGPT product runs a UAOS pre-send validator" in text
    assert "Do not paste the full UAOS policy" in text
