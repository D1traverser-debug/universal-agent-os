import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from uaos.contracts.enums import IntentType, TaskStatus
from uaos.integrations import BindingPolicy
from uaos.kernel import AmbiguousControlTarget, ControlCommand, TaskCandidate, resolve_control_target

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 10, 16, tzinfo=UTC)


def _load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _candidates_from_index():
    index = _load_json("state/TASK_INDEX.json")
    domain_candidates = [
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
    ]
    controller_candidates = [
        TaskCandidate(
            task_id=item["task_id"],
            owner_domain="UAOS",
            task_type=item["task_type"],
            status=TaskStatus(item["status"]),
            updated_at=NOW,
            resume_eligible=item["resume_eligible"],
            default_resume=item["default_resume"],
        )
        for item in index.get("controller_tasks", [])
    ]
    return tuple(domain_candidates + controller_candidates)


def _running_controller_candidate(task_id: str = "uaos:maintenance:synthetic", *, default_resume: bool = True):
    return TaskCandidate(
        task_id=task_id,
        owner_domain="UAOS",
        task_type="controller_maintenance",
        status=TaskStatus.RUNNING,
        updated_at=NOW,
        resume_eligible=True,
        default_resume=default_resume,
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


def test_selecting_controller_resumes_one_default_running_controller_maintenance_task():
    domain_only = tuple(candidate for candidate in _candidates_from_index() if candidate.owner_domain != "UAOS")
    maintenance = _running_controller_candidate()
    result = resolve_control_target(
        ControlCommand(IntentType.SYSTEM_MAINTENANCE),
        domain_only + (maintenance,),
    )
    assert result.mode == "MAINTENANCE"
    assert result.scope == "UAOS"
    assert result.task_id == maintenance.task_id


def test_current_controller_index_keeps_completed_tasks_nonresumable_and_resumes_only_active_default():
    controller_candidates = [candidate for candidate in _candidates_from_index() if candidate.owner_domain == "UAOS"]
    assert controller_candidates

    completed = [candidate for candidate in controller_candidates if candidate.status is TaskStatus.COMPLETE]
    assert completed
    assert all(candidate.resume_eligible is False for candidate in completed)
    assert all(candidate.default_resume is False for candidate in completed)

    active_defaults = [
        candidate
        for candidate in controller_candidates
        if candidate.status is TaskStatus.RUNNING and candidate.resume_eligible and candidate.default_resume
    ]
    assert len(active_defaults) == 1

    result = resolve_control_target(ControlCommand(IntentType.SYSTEM_MAINTENANCE), _candidates_from_index())
    assert result.mode == "MAINTENANCE"
    assert result.scope == "UAOS"
    assert result.task_id == active_defaults[0].task_id


def test_controller_maintenance_without_persisted_task_remains_at_controller_root():
    domain_only = tuple(candidate for candidate in _candidates_from_index() if candidate.owner_domain != "UAOS")
    result = resolve_control_target(ControlCommand(IntentType.SYSTEM_MAINTENANCE), domain_only)
    assert result.mode == "MAINTENANCE"
    assert result.task_id is None
    assert result.scope == "GLOBAL"


def test_multiple_default_controller_tasks_fail_closed():
    domain_only = tuple(candidate for candidate in _candidates_from_index() if candidate.owner_domain != "UAOS")
    first = _running_controller_candidate("uaos:maintenance:first")
    second = _running_controller_candidate("uaos:maintenance:second")
    with pytest.raises(AmbiguousControlTarget):
        resolve_control_target(
            ControlCommand(IntentType.SYSTEM_MAINTENANCE),
            domain_only + (first, second),
        )


def test_aliases_are_hints_not_phrase_grammar():
    policy = _load_json("config/INTENT_RESOLUTION_POLICY.json")
    index = _load_json("state/TASK_INDEX.json")

    assert policy["natural_language_resolution"] == "SEMANTIC_FIRST"
    assert any("not a phrase grammar" in rule for rule in policy["rules"])
    assert any("Do not add or mutate aliases" in rule for rule in policy["prohibitions"])
    assert "resolution_note" in index


def test_controller_option_uses_persisted_controller_task_source_without_second_index():
    policy = _load_json("config/SESSION_INTERACTION_POLICY.json")
    selector = policy["bare_inheritance_selector"]
    controller = selector["controller_option"]
    continuity = policy["controller_maintenance_continuity"]

    assert controller["controller_task_source"] == "state/TASK_INDEX.json#controller_tasks"
    assert selector["task_source"] == "state/TASK_INDEX.json#tasks"
    assert continuity["index_ref"] == "state/TASK_INDEX.json#controller_tasks"
    assert continuity["state_root"] == "state/tasks"
    assert "DO_NOT_CREATE_A_SECOND_CONTROLLER_INDEX" in continuity["anti_duplication"]


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


def test_fresh_chat_binding_validator_schema_contract_covers_all_registered_domains():
    """Exercise the parent validator with synthetic contract-conformant payloads.

    This is intentionally NOT evidence that current remote child ``main`` bytes were
    fetched or validated. Remote child authority is live-audited separately during
    promotion/runtime. The regression proves only that every registry entry can use
    the same executable semantic handshake when given conformant owner payloads.
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
            skill_text=(
                f"Controller: `{policy.controller}`.\n"
                "Parent cognition authority: `config/DELIBERATION_POLICY.json`."
            ),
        )
