"""Verify existing cold research navigation; not a semantic or native host judge."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "docs/research/uaos-inheritance-review-20261018/knowledge-study-20261019"
REQUIRED = tuple(
    f"{index:02d}_" for index in range(1, 9)
)


def test_cross_topic_research_index_points_to_current_original_sources():
    index = (LIBRARY / "README.md").read_text(encoding="utf-8")
    targets = re.findall(r"(?<!!)\[[^\]]+\]\(([^)#]+\.md)\)", index)
    assert targets, "no source links"
    for target in set(targets):
        path = (LIBRARY / target).resolve()
        assert path.is_relative_to(LIBRARY.resolve()), "source routing escaped original library"
        assert path.is_file(), f"stale or invented index link: {target}"
    assert all(any(target.startswith(prefix) for target in targets) for prefix in REQUIRED)
    assert "MethodTransfer" in index and "非适用" in index


def test_new_meta_study_does_not_masquerade_as_a_promoted_native_skill():
    study = (LIBRARY / "08_meta_knowledge_fusion_hierarchy_index_application.md").read_text(encoding="utf-8")
    assert "SOURCE_STUDY__METHOD_CANDIDATES__NOT_NATIVE_SKILL" in study
    assert "https://www.w3.org/TR/skos-reference/" in study
    assert "https://www.w3.org/TR/prov-o/" in study
    assert "https://microsoft.github.io/graphrag/query/drift_search/" in study
    assert "context conditions" in study and "nonfit" in study
    assert "未通过项" in study
