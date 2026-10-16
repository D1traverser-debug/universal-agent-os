import pytest

from uaos.kernel import (
    CapabilityDiscoveryAdmissionError,
    CapabilityDiscoveryAssessment,
    DiscoveryLens,
    DiscoveryProbe,
    ExternalSourceModel,
    ExternalSkillCandidate,
    assess_external_skill_candidate,
    require_outside_in_capability_discovery,
)


def _source() -> ExternalSourceModel:
    return ExternalSourceModel(
        source_id="skills-catalog",
        source_ref="https://example.test/skills",
        organization_axes=("occupation", "category", "creator", "repository", "task"),
        evidence_refs=("evidence://source-index",),
    )


def test_broad_discovery_rejects_known_need_only_keyword_search():
    assessment = CapabilityDiscoveryAssessment(
        objective="discover capabilities we may not yet know we need",
        source_model=_source(),
        probes=(
            DiscoveryProbe(
                lens=DiscoveryLens.TASK_OR_ACTIVITY,
                finding="searched only for a previously named debugging need",
                evidence_refs=("evidence://debug-search",),
            ),
            DiscoveryProbe(
                lens=DiscoveryLens.CATEGORY_OR_TAXONOMY,
                finding="filtered only within the already selected debugging category",
                evidence_refs=("evidence://debug-category",),
            ),
        ),
        latent_gap_candidates=("debugging",),
        known_need_seeded_only=True,
    )
    with pytest.raises(CapabilityDiscoveryAdmissionError, match="known-need"):
        require_outside_in_capability_discovery(assessment)


def test_broad_discovery_requires_multiple_outside_in_lenses_not_one_job_example():
    assessment = CapabilityDiscoveryAssessment(
        objective="learn how an external capability catalog can expose unknown gaps",
        source_model=_source(),
        probes=(
            DiscoveryProbe(
                lens=DiscoveryLens.ROLE_OR_OCCUPATION,
                finding="business-manager responsibilities imply requirement and coordination work",
                evidence_refs=("evidence://occupation",),
            ),
        ),
        latent_gap_candidates=("requirements-discovery",),
    )
    with pytest.raises(CapabilityDiscoveryAdmissionError, match="two distinct"):
        require_outside_in_capability_discovery(assessment)


def test_source_first_multi_lens_discovery_can_name_a_previously_unknown_gap():
    receipt = require_outside_in_capability_discovery(
        CapabilityDiscoveryAssessment(
            objective="discover latent capability gaps before choosing skills",
            source_model=_source(),
            probes=(
                DiscoveryProbe(
                    lens=DiscoveryLens.ROLE_OR_OCCUPATION,
                    finding="role families expose responsibility clusters that are absent from the current capability map",
                    evidence_refs=("evidence://occupation-map",),
                ),
                DiscoveryProbe(
                    lens=DiscoveryLens.WORKFLOW_OR_HANDOFF,
                    finding="business-to-engineering handoff exposes requirement translation and acceptance gaps",
                    evidence_refs=("evidence://handoff-map",),
                ),
                DiscoveryProbe(
                    lens=DiscoveryLens.CREATOR_OR_PORTFOLIO,
                    finding="creator portfolios expose capability bundles rather than isolated atomic skills",
                    evidence_refs=("evidence://portfolio",),
                ),
            ),
            latent_gap_candidates=(
                "latent-requirement-discovery",
                "cross-role-handoff-governance",
            ),
        )
    )
    assert set(receipt.lenses) == {
        DiscoveryLens.ROLE_OR_OCCUPATION,
        DiscoveryLens.WORKFLOW_OR_HANDOFF,
        DiscoveryLens.CREATOR_OR_PORTFOLIO,
    }
    assert "latent-requirement-discovery" in receipt.latent_gap_candidates


def test_skill_candidate_may_come_from_discovered_gap_without_pretending_need_was_known_first():
    receipt = require_outside_in_capability_discovery(
        CapabilityDiscoveryAssessment(
            objective="discover missing requirement capabilities",
            source_model=_source(),
            probes=(
                DiscoveryProbe(
                    lens=DiscoveryLens.TASK_OR_ACTIVITY,
                    finding="external task taxonomy contains requirement elicitation work absent from current map",
                    evidence_refs=("evidence://tasks",),
                ),
                DiscoveryProbe(
                    lens=DiscoveryLens.WORKFLOW_OR_HANDOFF,
                    finding="handoff analysis finds an unowned requirement translation step",
                    evidence_refs=("evidence://handoff",),
                ),
            ),
            latent_gap_candidates=("requirement-elicitation",),
        )
    )
    admission = assess_external_skill_candidate(
        ExternalSkillCandidate(
            skill_id="requirements-interviewing",
            source_ref="skillsmp/source",
            mapped_need_or_failure_class="",
            discovered_capability_gap="requirement-elicitation",
            discovery_receipt=receipt,
            source_inspected=True,
            companion_files_inspected=True,
            security_and_permissions_reviewed=True,
            existing_overlap_assessed=True,
            evaluation_refs=("eval:requirements-scenario",),
        )
    )
    assert admission.promotable_candidate


def test_discovered_skill_candidate_must_reference_gap_proven_by_receipt():
    receipt = require_outside_in_capability_discovery(
        CapabilityDiscoveryAssessment(
            objective="discover missing capability",
            source_model=_source(),
            probes=(
                DiscoveryProbe(
                    lens=DiscoveryLens.CATEGORY_OR_TAXONOMY,
                    finding="taxonomy suggests one gap",
                    evidence_refs=("evidence://taxonomy",),
                ),
                DiscoveryProbe(
                    lens=DiscoveryLens.ADJACENT_DOMAIN,
                    finding="adjacent domain confirms the same gap",
                    evidence_refs=("evidence://adjacent",),
                ),
            ),
            latent_gap_candidates=("gap-a",),
        )
    )
    with pytest.raises(ValueError, match="present in the discovery receipt"):
        assess_external_skill_candidate(
            ExternalSkillCandidate(
                skill_id="unrelated-skill",
                source_ref="skillsmp/source",
                mapped_need_or_failure_class="",
                discovered_capability_gap="gap-b",
                discovery_receipt=receipt,
                source_inspected=True,
                companion_files_inspected=True,
                security_and_permissions_reviewed=True,
                existing_overlap_assessed=True,
                evaluation_refs=("eval:scenario",),
            )
        )
