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
