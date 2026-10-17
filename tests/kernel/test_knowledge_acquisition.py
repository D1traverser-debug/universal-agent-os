import pytest

from uaos.kernel import (
    AcquisitionMethod,
    AcquisitionProbe,
    Contradiction,
    ContradictionDisposition,
    KnowledgeAcquisitionAdmissionError,
    KnowledgeAcquisitionAssessment,
    KnowledgeSource,
    KnowledgeSourceRole,
    MethodFamily,
    SaturationRound,
    require_knowledge_acquisition_admission,
)


def _assessment(**overrides):
    values = dict(
        acquisition_id="knowledge:test",
        objective="Compare instruction and research methods before changing UAOS.",
        knowledge_modules=("instruction-language", "research-acquisition"),
        required_source_roles=(
            KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY,
            KnowledgeSourceRole.INDEPENDENT_RESEARCH_OR_BENCHMARK,
            KnowledgeSourceRole.IMPLEMENTATION_EVIDENCE,
        ),
        sources=(
            KnowledgeSource(
                "official",
                "https://developers.openai.com/",
                KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY,
                ("official-guidance",),
            ),
            KnowledgeSource(
                "benchmark",
                "paper://skills-benchmark",
                KnowledgeSourceRole.INDEPENDENT_RESEARCH_OR_BENCHMARK,
                ("benchmark-result",),
            ),
            KnowledgeSource(
                "repo",
                "https://github.com/openai/skills",
                KnowledgeSourceRole.IMPLEMENTATION_EVIDENCE,
                ("repo-sample",),
            ),
        ),
        probes=(
            AcquisitionProbe(
                "seed",
                AcquisitionMethod.DIRECT_SEARCH,
                "skill description triggering guidance",
                "Seed search established metadata guidance.",
                ("official-guidance",),
            ),
            AcquisitionProbe(
                "expand",
                AcquisitionMethod.QUERY_EXPANSION,
                "progressive disclosure context economy negative instructions",
                "Expanded vocabulary exposed competing instruction-design methods.",
                ("benchmark-result",),
            ),
            AcquisitionProbe(
                "repo",
                AcquisitionMethod.REPOSITORY_TRAVERSAL,
                "openai/skills curated examples",
                "Repository traversal confirmed concise and mandatory-trigger examples coexist by risk class.",
                ("repo-sample",),
            ),
        ),
        method_families=(
            MethodFamily(
                "principle-first",
                "Use concise operating invariants for contextual judgment.",
                ("official-guidance", "benchmark-result"),
            ),
            MethodFamily(
                "hard-gate",
                "Use explicit mandatory constraints at fragile chokepoints.",
                ("repo-sample",),
            ),
        ),
        contradictions=(
            Contradiction(
                "positive-vs-negative",
                "Some guidance favors positive principles while real skills use MUST/NEVER at hard prerequisites.",
                ContradictionDisposition.BOUNDED,
                ("official-guidance", "repo-sample"),
                "Use principles for judgment and hard negatives only for genuine cliffs/fragile operations.",
            ),
        ),
        saturation_rounds=(
            SaturationRound(
                "sat-1",
                (AcquisitionMethod.BACKWARD_REFERENCE,),
                (),
                (),
                (),
                False,
                ("benchmark-result",),
            ),
            SaturationRound(
                "sat-2",
                (AcquisitionMethod.REPOSITORY_TRAVERSAL,),
                (),
                (),
                (),
                False,
                ("repo-sample",),
            ),
        ),
        stop_reason="Required source roles are covered and two terminal expansion rounds produced no material new family/failure/constraint.",
        holdout_or_validation_plan="Evaluate on fresh trigger/non-trigger and autonomous-continuation holdouts.",
    )
    values.update(overrides)
    return KnowledgeAcquisitionAssessment(**values)


def test_comprehensive_acquisition_admits_coverage_expansion_and_saturation():
    receipt = require_knowledge_acquisition_admission(_assessment())
    assert receipt.acquisition_id == "knowledge:test"
    assert KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY in receipt.source_roles
    assert AcquisitionMethod.QUERY_EXPANSION in receipt.acquisition_methods
    assert receipt.method_family_ids == ("principle-first", "hard-gate")


def test_comprehensive_acquisition_requires_primary_authority():
    sources = tuple(
        item for item in _assessment().sources
        if item.role is not KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY
    )
    required = tuple(
        role for role in _assessment().required_source_roles
        if role is not KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY
    )
    with pytest.raises(KnowledgeAcquisitionAdmissionError, match="current/primary"):
        require_knowledge_acquisition_admission(
            _assessment(sources=sources, required_source_roles=required)
        )


def test_discovery_and_community_only_cannot_claim_comprehensive_learning():
    sources = (
        KnowledgeSource(
            "official",
            "authority://current",
            KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY,
            ("official-guidance",),
        ),
        KnowledgeSource(
            "catalog",
            "catalog://skills",
            KnowledgeSourceRole.DISCOVERY_INDEX,
            ("catalog-hit",),
        ),
        KnowledgeSource(
            "community",
            "community://discussion",
            KnowledgeSourceRole.COMMUNITY_SIGNAL,
            ("community-signal",),
        ),
    )
    with pytest.raises(KnowledgeAcquisitionAdmissionError, match="beyond primary authority"):
        require_knowledge_acquisition_admission(
            _assessment(
                sources=sources,
                required_source_roles=(
                    KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY,
                    KnowledgeSourceRole.DISCOVERY_INDEX,
                ),
            )
        )


def test_seed_search_without_expansion_cannot_claim_comprehensive_learning():
    probes = (
        AcquisitionProbe(
            "seed-search",
            AcquisitionMethod.DIRECT_SEARCH,
            "seed query",
            "Seed search finding.",
            ("official-guidance",),
        ),
        AcquisitionProbe(
            "seed-browse",
            AcquisitionMethod.SOURCE_NATIVE_BROWSE,
            "known source navigation",
            "A second seed-level acquisition method found supporting material but did not expand the search space.",
            ("repo-sample",),
        ),
    )
    with pytest.raises(KnowledgeAcquisitionAdmissionError, match="requires query/reference/repository/adjacent expansion"):
        require_knowledge_acquisition_admission(_assessment(probes=probes))


def test_terminal_novelty_blocks_saturation_claim():
    rounds = (
        _assessment().saturation_rounds[0],
        SaturationRound(
            "sat-2",
            (AcquisitionMethod.REPOSITORY_TRAVERSAL,),
            ("new-family",),
            (),
            (),
            False,
            ("repo-sample",),
        ),
    )
    with pytest.raises(KnowledgeAcquisitionAdmissionError, match="saturation is not established"):
        require_knowledge_acquisition_admission(_assessment(saturation_rounds=rounds))


def test_duplicate_saturation_round_id_cannot_claim_two_rounds():
    round_one = _assessment().saturation_rounds[0]
    duplicate_id = SaturationRound(
        round_one.round_id,
        (AcquisitionMethod.REPOSITORY_TRAVERSAL,),
        (),
        (),
        (),
        False,
        ("repo-sample",),
    )
    with pytest.raises(KnowledgeAcquisitionAdmissionError, match="saturation round ids must be unique"):
        require_knowledge_acquisition_admission(_assessment(saturation_rounds=(round_one, duplicate_id)))


def test_terminal_saturation_rounds_must_each_be_expansion_work():
    rounds = (
        SaturationRound(
            "sat-1",
            (AcquisitionMethod.DIRECT_SEARCH,),
            (),
            (),
            (),
            False,
            ("official-guidance",),
        ),
        _assessment().saturation_rounds[1],
    )
    with pytest.raises(KnowledgeAcquisitionAdmissionError, match="each terminal round to contain expansion work"):
        require_knowledge_acquisition_admission(_assessment(saturation_rounds=rounds))


def test_repeated_terminal_saturation_evidence_cannot_claim_distinct_rounds():
    repeated = SaturationRound(
        "sat-2b",
        (AcquisitionMethod.BACKWARD_REFERENCE,),
        (),
        (),
        (),
        False,
        ("benchmark-result",),
    )
    with pytest.raises(KnowledgeAcquisitionAdmissionError, match="two distinct terminal expansion rounds"):
        require_knowledge_acquisition_admission(
            _assessment(saturation_rounds=(_assessment().saturation_rounds[0], repeated))
        )


def test_narrow_known_need_lookup_can_remain_lightweight():
    assessment = KnowledgeAcquisitionAssessment(
        acquisition_id="knowledge:narrow",
        objective="Read one known current specification fact.",
        knowledge_modules=("known-spec",),
        required_source_roles=(KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY,),
        sources=(
            KnowledgeSource(
                "official",
                "authority://spec",
                KnowledgeSourceRole.CURRENT_OR_PRIMARY_AUTHORITY,
                ("spec-fact",),
            ),
        ),
        probes=(
            AcquisitionProbe(
                "lookup",
                AcquisitionMethod.SOURCE_NATIVE_BROWSE,
                "known spec section",
                "Located the exact known fact.",
                ("spec-fact",),
            ),
        ),
        method_families=(),
        contradictions=(),
        saturation_rounds=(),
        stop_reason="Exact authoritative fact retrieved; broad method search is not part of the objective.",
        holdout_or_validation_plan="Cross-check the returned value against the cited source section.",
    )
    receipt = require_knowledge_acquisition_admission(assessment, comprehensive=False)
    assert receipt.method_family_ids == ()
