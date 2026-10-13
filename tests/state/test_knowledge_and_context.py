import pytest
from uaos.contracts.context import CompactionArtifact, ProgressCursor
from uaos.contracts.enums import KnowledgeState
from uaos.contracts.models import KnowledgeItem
from uaos.state import KnowledgeCatalog, snapshot_bytes, validate_compaction


def test_source_snapshot_is_content_bound():
    first = snapshot_bytes(snapshot_id="s1", source_uri="web:x", content=b"abc", storage_uri="obj:a")
    second = snapshot_bytes(snapshot_id="s2", source_uri="web:x", content=b"abd", storage_uri="obj:b")
    assert first.content_hash != second.content_hash


def test_progress_cursor_cannot_resume_against_changed_source():
    cursor = ProgressCursor("book", "hash1", "ch10", "ch11", 0.4)
    cursor.assert_source("book", "hash1")
    with pytest.raises(ValueError, match="mismatch"):
        cursor.assert_source("book", "hash2")


def test_candidate_does_not_enter_canonical_retrieval():
    catalog = KnowledgeCatalog()
    catalog.add(KnowledgeItem("k1", "technique", ("source:s1",), "domain:novel", KnowledgeState.RAW_EVIDENCE, 0.5))
    catalog.transition("k1", KnowledgeState.CANDIDATE)
    assert catalog.retrieve(scopes={"domain:novel"}) == ()
    assert [item.knowledge_id for item in catalog.retrieve(scopes={"domain:novel"}, include_candidate=True)] == ["k1"]


def test_canonical_requires_evaluation_and_usage_link():
    catalog = KnowledgeCatalog()
    catalog.add(KnowledgeItem("k1", "method", ("s1",), "domain:novel", KnowledgeState.RAW_EVIDENCE, 0.7))
    catalog.transition("k1", KnowledgeState.CANDIDATE)
    catalog.transition("k1", KnowledgeState.EVALUATED)
    with pytest.raises(ValueError, match="usage"):
        catalog.transition("k1", KnowledgeState.CANONICAL)
    item = catalog.transition("k1", KnowledgeState.CANONICAL, usage_links=("eval:e1",))
    assert item.state is KnowledgeState.CANONICAL


def test_compaction_must_preserve_pending_semantics():
    artifact = CompactionArtifact(
        "c1",
        "ctxhash",
        "outhash",
        retained_obligations=("finish-book",),
        retained_approval_ids=("ap1",),
        tool_result_pairs=(("tool1", "result1"),),
        provenance_refs=("source:s1",),
        next_actions=("continue-ch11",),
    )
    validate_compaction(
        artifact,
        required_obligations={"finish-book"},
        required_approval_ids={"ap1"},
        required_tool_result_pairs={("tool1", "result1")},
        required_provenance_refs={"source:s1"},
    )
    with pytest.raises(ValueError, match="obligations"):
        validate_compaction(
            artifact,
            required_obligations={"finish-book", "audit"},
            required_approval_ids={"ap1"},
            required_tool_result_pairs={("tool1", "result1")},
            required_provenance_refs={"source:s1"},
        )
