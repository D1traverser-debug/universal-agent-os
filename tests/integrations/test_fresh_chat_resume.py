import json
from datetime import UTC, datetime
from pathlib import Path

from uaos.contracts.enums import IntentType, TaskStatus
from uaos.kernel import ControlCommand, TaskCandidate, resolve_control_target

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 10, 14, tzinfo=UTC)


def _load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _candidates_from_index():
    index = _load_json("state/TASK_INDEX.json")
    return tuple(
        TaskCandidate(
            task_id=item["task_id"],
            owner_domain=item["domain_id"],
            task_type=item["task_type"],
            status=TaskStatus(item["status"]),
            updated_at=NOW,
            resume_eligible=item["resume_eligible"],
            default_resume=item["default_resume_within_domain"],
        )
        for item in index["tasks"]
    )


def test_domain_level_video_continue_selects_parent_router_without_child_identity_guess():
    result = resolve_control_target(
        ControlCommand(IntentType.CONTINUE, domain_hint="video"),
        _candidates_from_index(),
    )
    assert result.task_id == "video:main"


def test_aliases_are_hints_not_phrase_grammar():
    policy = _load_json("config/INTENT_RESOLUTION_POLICY.json")
    index = _load_json("state/TASK_INDEX.json")

    assert policy["natural_language_resolution"] == "SEMANTIC_FIRST"
    assert any("not a phrase grammar" in rule for rule in policy["rules"])
    assert any("Do not add or mutate aliases" in rule for rule in policy["prohibitions"])
    assert "resolution_note" in index


def test_video_has_one_unambiguous_parent_router_and_child_resolution_stays_in_domain():
    index = _load_json("state/TASK_INDEX.json")
    video_tasks = [item for item in index["tasks"] if item["domain_id"] == "video"]
    defaults = [item for item in video_tasks if item["default_resume_within_domain"]]

    assert [item["task_id"] for item in video_tasks] == ["video:main"]
    assert [item["task_id"] for item in defaults] == ["video:main"]
    router = video_tasks[0]
    assert "video-growth:main" in router["aliases"]
    assert "video:ai-self-media-commercialization" in router["aliases"]
    assert "child project" in router["semantic_summary"].lower()
    assert "opaque child reference" in router["semantic_summary"].lower()


def test_plain_chatgpt_fresh_chat_bootstrap_contract_is_explicit():
    current = _load_json("CURRENT_SYSTEM.json")
    policy = _load_json("config/INTENT_RESOLUTION_POLICY.json")
    bootstrap = current["fresh_chat_bootstrap"]

    assert bootstrap["core_requires_account_custom_instructions"] is False
    assert bootstrap["deterministic_plain_chatgpt_requires_bootstrap_pointer_unless_host_injects_entrypoint"] is True
    assert bootstrap["pointer_ref"] == "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md"
    assert policy["fresh_chat"]["bootstrap_chain"][0] == "ENTRYPOINT.md"
