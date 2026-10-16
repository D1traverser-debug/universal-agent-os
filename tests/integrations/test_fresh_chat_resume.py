import json
from datetime import UTC, datetime
from pathlib import Path

from uaos.contracts.enums import IntentType, TaskStatus
from uaos.integrations import BindingPolicy
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


def test_domain_level_ashare_continue_selects_parent_router_without_market_day_guess():
    result = resolve_control_target(
        ControlCommand(IntentType.CONTINUE, domain_hint="ashare"),
        _candidates_from_index(),
    )
    assert result.task_id == "ashare:main"


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


def test_ashare_has_one_unambiguous_parent_router_and_child_market_day_resolution_stays_in_domain():
    index = _load_json("state/TASK_INDEX.json")
    ashare_tasks = [item for item in index["tasks"] if item["domain_id"] == "ashare"]
    defaults = [item for item in ashare_tasks if item["default_resume_within_domain"]]

    assert [item["task_id"] for item in ashare_tasks] == ["ashare:main"]
    assert [item["task_id"] for item in defaults] == ["ashare:main"]
    router = ashare_tasks[0]
    assert "ashare:recommendation" in router["aliases"]
    summary = router["semantic_summary"].lower()
    assert "current china trading day" in summary
    assert "opaque child market-day reference" in summary


def test_plain_chatgpt_fresh_chat_bootstrap_contract_is_explicit():
    current = _load_json("CURRENT_SYSTEM.json")
    policy = _load_json("config/INTENT_RESOLUTION_POLICY.json")
    bootstrap = current["fresh_chat_bootstrap"]

    assert bootstrap["core_requires_account_custom_instructions"] is False
    assert bootstrap["deterministic_plain_chatgpt_requires_bootstrap_pointer_unless_host_injects_entrypoint"] is True
    assert bootstrap["pointer_ref"] == "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md"
    assert policy["fresh_chat"]["bootstrap_chain"][0] == "ENTRYPOINT.md"


def test_every_registered_domain_has_one_resumable_parent_route():
    registry_domains = {item["domain_id"] for item in _load_json("config/AGENT_REGISTRY.json")["agents"]}
    index = _load_json("state/TASK_INDEX.json")
    resumable_domains = {
        item["domain_id"]
        for item in index["tasks"]
        if item["resume_eligible"] and item["status"] not in {"COMPLETE", "CANCELLED"}
    }
    assert registry_domains == resumable_domains


def test_fresh_chat_domain_binding_contract_covers_all_registered_domains_not_only_router_selection():
    """Exercise the complete parent-side inheritance contract after selection.

    Remote child bytes are owner state and are live-audited separately.  This test
    proves that every registry entry can traverse the same executable handshake:
    registry -> manifest/adapter/skill pointers -> capabilities -> current common
    capability authority -> canonical deliberation owner.
    """

    registry = _load_json("config/AGENT_REGISTRY.json")["agents"]
    common = _load_json("config/COMMON_CAPABILITIES.json")
    policy = BindingPolicy.from_path(ROOT / "config" / "BINDING_POLICY.json")
    required_common = [item["capability_id"] for item in common["capabilities"]]

    for entry in registry:
        adapter = {"controller": policy.controller, "status": policy.required_adapter_status}
        manifest = {
            "controller": policy.controller,
            "status": policy.required_manifest_status,
            "skill": {"entrypoint": entry["skill_ref"]},
            "binding": {
                "controller_ref": policy.controller_ref,
                "adapter_ref": entry["uaos_adapter_ref"],
                "capability_ref": entry["capability_ref"],
            },
        }
        capabilities = {
            "domain_id": entry["domain_id"],
            "uaos_common_capabilities_ref": policy.common_capabilities_ref,
            "uaos_common_capabilities_contract_min": common["contract_version"],
            "uaos_common_behavior_assurance_ref": policy.common_behavior_ref,
            "uaos_deliberation_policy_ref": policy.deliberation_policy_ref,
            "common_capabilities_inheritance": "UAOS_HOSTED",
            "required_uaos_common_capabilities": required_common,
            "hosted_cognition_semantics": {
                "source": "CURRENT_UAOS_DELIBERATION_POLICY",
                "local_overrides": "NONE",
            },
        }
        policy.validate_domain_binding(
            registry_entry=entry,
            adapter=adapter,
            manifest=manifest,
            capabilities=capabilities,
            common_capabilities=common,
            skill_text=f"Controller: `{policy.controller}`.",
        )
