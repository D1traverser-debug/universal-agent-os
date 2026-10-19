from pathlib import Path
import json

import pytest

from uaos.integrations import RetrievalDenied, RetrievalPolicy, RetrievalPurpose

ROOT = Path(__file__).resolve().parents[2]
POLICY = RetrievalPolicy.from_path(ROOT / "config" / "RETRIEVAL_POLICY.json")


def test_retired_controller_blocked_in_active_execution():
    with pytest.raises(RetrievalDenied):
        POLICY.authorize("D1traverser-debug/universal-continuity-agent", "ENTRYPOINT.md")


def test_retired_controller_historical_access_requires_explicit_intent():
    with pytest.raises(RetrievalDenied):
        POLICY.authorize("D1traverser-debug/universal-continuity-agent", "README.md", purpose=RetrievalPurpose.HISTORICAL_QUERY)
    POLICY.authorize("D1traverser-debug/universal-continuity-agent", "README.md", purpose=RetrievalPurpose.HISTORICAL_QUERY, explicit_historical=True)


def test_retired_domain_control_paths_are_blocked():
    assert not POLICY.is_allowed("D1traverser-debug/video-growth-agent", "continuity/tasks/video-growth-main/TASK_MANIFEST.json")
    assert not POLICY.is_allowed("D1traverser-debug/financial-writing-agent", "continuity/UNIVERSAL_PROTOCOL_ADAPTER.json")
    assert not POLICY.is_allowed("D1traverser-debug/novel-writing-agent", "continuity/TASK_INDEX.json")
    assert not POLICY.is_allowed("D1traverser-debug/a-share-event-driven-agent", "config/cutover_status.json")


def test_current_binding_surfaces_are_allowed():
    for repo in (
        "D1traverser-debug/video-growth-agent",
        "D1traverser-debug/financial-writing-agent",
        "D1traverser-debug/a-share-event-driven-agent",
        "D1traverser-debug/novel-writing-agent",
    ):
        assert POLICY.is_allowed(repo, "UAOS_SKILL.md")
        assert POLICY.is_allowed(repo, ".uaos/MANIFEST.json")
        assert POLICY.is_allowed(repo, ".uaos/ADAPTER.json")
        assert POLICY.is_allowed(repo, ".uaos/CAPABILITIES.json")


def test_normal_business_evidence_remains_retrievable():
    assert POLICY.is_allowed("D1traverser-debug/video-growth-agent", "projects/ai-self-media-commercialization/PROJECT_MANIFEST.json")
    assert POLICY.is_allowed("D1traverser-debug/novel-writing-agent", "projects/FQ001_MINGRI_ORDER/checkpoints/CURRENT_CHECKPOINT.json")
    assert POLICY.is_allowed("D1traverser-debug/financial-writing-agent", "workspaces/articles/example/STATE.json")


# Controlled knowledge-library inventory admission: latest four studies are
# only a subset. These synthetic host callbacks do not prove native ChatGPT
# performs this routing without a connected, trusted invocation path.
def _knowledge_sources():
    system_map = json.loads((ROOT / "config" / "SYSTEM_MAP.json").read_text(encoding="utf-8"))
    expected = {
        system_map["controller"]["repository"],
        *(owner["repository"] for owner in system_map["domains"].values()),
    }
    return system_map, {repo: "test:github:" + repo for repo in expected}


def _historical():
    return {
        "GOOGLE_DRIVE": "SEARCHED_WITH_EVIDENCE",
        "NOTION": "SEARCHED_WITH_EVIDENCE",
        "CHATGPT_LIBRARY": "SEARCHED_WITH_EVIDENCE",
        "PRIOR_CONVERSATIONS": "SEARCHED_WITH_EVIDENCE",
    }


def test_broad_knowledge_inventory_requires_every_registered_owner_not_just_recent_skill_folder():
    current, refs = _knowledge_sources()
    receipt = POLICY.admit_broad_knowledge_inventory(
        system_map=current,
        repository_evidence_refs=refs,
        verify_source_ref=lambda ref: ref.startswith("test:github:"),
        prior_work_requested=False,
    )
    assert set(receipt.checked_repositories) == set(refs)
    assert "CONTENT_EXHAUSTIVENESS" in receipt.assurance
    assert len(receipt.checked_repositories) > 1
    with pytest.raises(RetrievalDenied, match="omitted registered repositories"):
        POLICY.admit_broad_knowledge_inventory(
            system_map=current,
            repository_evidence_refs={current["controller"]["repository"]: "test:recent-four-only"},
            verify_source_ref=lambda _: True,
            prior_work_requested=False,
        )


def test_broad_knowledge_inventory_needs_host_verified_source_read_refs():
    current, refs = _knowledge_sources()
    with pytest.raises(RetrievalDenied, match="trusted host verifier"):
        POLICY.admit_broad_knowledge_inventory(
            system_map=current, repository_evidence_refs=refs,
            verify_source_ref=None, prior_work_requested=False,
        )
    with pytest.raises(RetrievalDenied, match="unverified knowledge repository"):
        POLICY.admit_broad_knowledge_inventory(
            system_map=current, repository_evidence_refs=refs,
            verify_source_ref=lambda _: False, prior_work_requested=False,
        )


def test_prior_knowledge_inventory_cannot_silently_skip_drive_notion_library_and_conversations():
    current, refs = _knowledge_sources()
    call = dict(
        system_map=current, repository_evidence_refs=refs,
        verify_source_ref=lambda ref: ref.startswith("test:"),
        prior_work_requested=True,
    )
    with pytest.raises(RetrievalDenied, match="historical source disposition"):
        POLICY.admit_broad_knowledge_inventory(**call)
    with pytest.raises(RetrievalDenied, match="left unexamined"):
        POLICY.admit_broad_knowledge_inventory(**call, historical_surface_outcomes={"NOTION": "UNAVAILABLE_OR_NOT_CONNECTED"})
    with pytest.raises(RetrievalDenied, match="unverified historical knowledge source"):
        POLICY.admit_broad_knowledge_inventory(**call, historical_surface_outcomes=_historical())
    receipt = POLICY.admit_broad_knowledge_inventory(
        **call,
        historical_surface_outcomes=_historical(),
        historical_surface_evidence_refs={k: "test:historical:" + k for k in _historical()},
    )
    assert receipt.unavailable_historical_surfaces == ()
    assert len(receipt.checked_repositories) == 5


def test_unavailable_historical_source_remains_explicitly_unverified_not_assumed_empty():
    current, refs = _knowledge_sources()
    historical = _historical()
    historical["NOTION"] = "UNAVAILABLE_OR_NOT_CONNECTED"
    receipt = POLICY.admit_broad_knowledge_inventory(
        system_map=current,
        repository_evidence_refs=refs,
        verify_source_ref=lambda ref: ref.startswith("test:"),
        prior_work_requested=True,
        historical_surface_outcomes=historical,
        historical_surface_evidence_refs={k: "test:historical:" + k for k in historical},
    )
    assert receipt.unavailable_historical_surfaces == ("NOTION",)
    assert "UNVERIFIED" in receipt.assurance


def test_knowledge_scope_policy_preserves_original_owner_and_never_publicizes_external_file_ids():
    guide = POLICY.knowledge_inventory_routing
    assert guide["role"].startswith("NON_AUTHORITATIVE")
    assert "DO_NOT_REDUCE_ALL_KNOWLEDGE_TO_RECENT_FOUR_EXTERNAL_SKILL_STUDIES" in guide["completeness_invariants"]
    assert "NEVER_COPY_PRIVATE_EXTERNAL_CONNECTOR_URLS_IDENTIFIERS_OR_CONTENT_INTO_PUBLIC_GITHUB_METADATA" in guide["completeness_invariants"]
    assert set(guide["source_roles"]["registered_child_git"]["root_hints_by_domain"]) == set(
        _knowledge_sources()[0]["domains"]
    )
    kinds = {item["surface"] for item in guide["source_roles"]["optional_connected_historical_surfaces"]}
    assert kinds == {"GOOGLE_DRIVE", "NOTION", "CHATGPT_LIBRARY", "PRIOR_CONVERSATIONS"}
    assert "NATIVE" in guide["native_limit"]


def test_bootstrap_explicitly_routes_full_knowledge_questions_to_existing_retrieval_owner():
    entry = (ROOT / "ENTRYPOINT.md").read_text(encoding="utf-8")
    assert "config/RETRIEVAL_POLICY.json#knowledge_inventory_routing" in entry
    assert "A four-skill source-study list is never proof" in entry
    assert "no claim of native ChatGPT non-bypassable invocation" in entry


from uaos.integrations.retrieval import build_source_read_plan


def _current_read_plan_source():
    return (
        json.loads((ROOT / "config/SYSTEM_MAP.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "state/TASK_INDEX.json").read_text(encoding="utf-8")),
    )


def test_controller_resume_reads_exact_default_task_and_not_large_cold_entry():
    system, index = _current_read_plan_source()
    plan = build_source_read_plan(system_map=system, task_index=index, retrieval_policy=POLICY)
    paths = [(item.repository, item.path) for item in plan.reads]
    parent = system["controller"]["repository"]
    assert paths == [
        (parent, "config/SYSTEM_MAP.json"),
        (parent, "state/TASK_INDEX.json"),
        (parent, next(t for t in index["controller_tasks"] if t["default_resume"])["state_ref"]),
    ]
    assert "NO_FILES_FETCHED_OR_NATIVE_ACTIVATION" in plan.assurance


def test_cold_controller_bootstrap_is_distinct_from_every_turn_task_read():
    system, index = _current_read_plan_source()
    plan = build_source_read_plan(
        system_map=system, task_index=index, retrieval_policy=POLICY, cold_start=True,
    )
    paths = [item.path for item in plan.reads]
    assert paths[:4] == [
        "ENTRYPOINT.md", "CURRENT_SYSTEM.json", "config/SYSTEM_MAP.json", "state/TASK_INDEX.json"
    ]
    assert paths[-1] == "state/tasks/uaos-inheritance-review-20261018.json"


@pytest.mark.parametrize("domain", ["financial_writing", "ashare", "novel", "video"])
def test_domain_plan_uses_registered_child_entry_and_never_guesses_business_project(domain):
    system, index = _current_read_plan_source()
    plan = build_source_read_plan(
        system_map=system, task_index=index, retrieval_policy=POLICY, selected_domain=domain,
    )
    child = system["domains"][domain]
    paths = {(item.repository, item.path) for item in plan.reads}
    assert (child["repository"], child["entrypoint"]) in paths
    assert (child["repository"], ".uaos/MANIFEST.json") in paths
    assert (child["repository"], ".uaos/ADAPTER.json") in paths
    assert (child["repository"], ".uaos/CAPABILITIES.json") in paths
    assert all(not path.startswith("projects/") for _, path in paths)
    assert all(repo == child["repository"] for repo, _ in plan.discovery_roots)


def test_broad_knowledge_plan_resolves_all_five_owners_and_root_discovery_not_fake_files():
    system, index = _current_read_plan_source()
    plan = build_source_read_plan(
        system_map=system, task_index=index, retrieval_policy=POLICY, broad_knowledge=True,
    )
    expected = {system["controller"]["repository"]} | {
        item["repository"] for item in system["domains"].values()
    }
    observed = {item.repository for item in plan.reads}
    assert observed == expected
    assert {repo for repo, _ in plan.discovery_roots} == expected
    assert all(path.endswith("/") for _, path in plan.discovery_roots)
    assert "NO_FILES_FETCHED" in plan.assurance


def test_read_plan_rejects_wrong_domain_and_ambiguous_default_instead_of_guessing():
    system, index = _current_read_plan_source()
    with pytest.raises(RetrievalDenied, match="not registered"):
        build_source_read_plan(
            system_map=system, task_index=index, retrieval_policy=POLICY, selected_domain="made-up",
        )
    changed = dict(index)
    changed["controller_tasks"] = [dict(t) for t in index["controller_tasks"]]
    next(t for t in changed["controller_tasks"] if t["default_resume"])["default_resume"] = False
    with pytest.raises(RetrievalDenied, match="exactly one"):
        build_source_read_plan(system_map=system, task_index=changed, retrieval_policy=POLICY)


@pytest.mark.parametrize(
    "field,invalid_value",
    [
        ("resume_eligible", False),
        ("resume_eligible", None),
        ("task_type", "article_workspace_router"),
        ("authority_context", "DOMAIN:video"),
        ("status", "COMPLETE"),
    ],
)
def test_controller_source_plan_rejects_ineligible_or_noncontroller_default(field, invalid_value):
    system, index = _current_read_plan_source()
    changed = dict(index)
    changed["controller_tasks"] = [dict(t) for t in index["controller_tasks"]]
    target = next(t for t in changed["controller_tasks"] if t["default_resume"])
    target[field] = invalid_value
    with pytest.raises(RetrievalDenied, match="controller task authority, type, eligibility or status"):
        build_source_read_plan(system_map=system, task_index=changed, retrieval_policy=POLICY)


def test_read_plan_rejects_unsafe_task_refs_and_missing_children_instead_of_search_guess():
    system, index = _current_read_plan_source()
    changed = dict(index)
    changed["controller_tasks"] = [dict(t) for t in index["controller_tasks"]]
    target = next(t for t in changed["controller_tasks"] if t["default_resume"])
    target["state_ref"] = "state/tasks/../PRIVATE.json"
    with pytest.raises(RetrievalDenied, match="unsafe"):
        build_source_read_plan(system_map=system, task_index=changed, retrieval_policy=POLICY)
    changed = dict(index)
    changed["tasks"] = [t for t in index["tasks"] if t["domain_id"] != "video"]
    with pytest.raises(RetrievalDenied, match="missing or ambiguous"):
        build_source_read_plan(
            system_map=system, task_index=changed, retrieval_policy=POLICY,
            selected_domain="video",
        )


def test_source_plan_is_not_a_state_machine_or_a_host_fetch_receipt():
    system, index = _current_read_plan_source()
    plan = build_source_read_plan(system_map=system, task_index=index, retrieval_policy=POLICY)
    assert plan.selected_domain is None
    assert not hasattr(plan, "completed")
    assert not hasattr(plan, "fetch")
    assert "NATIVE_ACTIVATION" in plan.assurance
