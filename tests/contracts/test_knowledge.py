import pytest
from uaos.contracts.enums import KnowledgeState
from uaos.contracts.models import KnowledgeItem
from uaos.contracts.state_machines import transition_knowledge


def item(state=KnowledgeState.RAW_EVIDENCE):
    return KnowledgeItem(knowledge_id="k1", content="a technique observed in one source", source_refs=("source:1",), applicable_scope="novel/source-1", state=state, confidence=0.6)


def test_knowledge_cannot_jump_from_raw_evidence_to_canonical():
    with pytest.raises(ValueError, match="invalid knowledge transition"):
        transition_knowledge(item(), KnowledgeState.CANONICAL)


def test_knowledge_promotion_requires_evaluated_stage_and_usage_link():
    candidate = transition_knowledge(item(), KnowledgeState.CANDIDATE)
    evaluated = transition_knowledge(candidate, KnowledgeState.EVALUATED)
    with pytest.raises(ValueError, match="usage"):
        transition_knowledge(evaluated, KnowledgeState.CANONICAL)
    canonical = transition_knowledge(evaluated, KnowledgeState.CANONICAL, usage_links=("eval:e1",))
    assert canonical.state is KnowledgeState.CANONICAL
