"""Red/expected-fail holdout: structurally complete study != semantic validity.

This case is intentionally *not* a new finalization gate or an invented native
host trace. It freezes one reproduced limitation of the controlled source-only
contract while a proper host-bound independent semantic judge is designed.
"""
import pytest

from uaos.runtime.epistemic_entry import (
    DimensionResearch,
    EntryAdmissionError,
    FullDimensionStudy,
    FULL_RESEARCH_AXES,
    FULL_RESEARCH_CONCERNS,
    admit_full_dimension_study,
)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "KNOWN GAP: current controlled study admission verifies structural "
        "coverage and host-provided reference booleans, not whether source "
        "mechanisms causally fit the user's goal or observed outcome"
    ),
)
def test_all_sources_and_axes_present_but_semantically_irrelevant_is_not_valid():
    """Must reject a citation-rich study that entirely misses its task goal."""
    studies = tuple(
        DimensionResearch(
            axis=axis,
            local_evidence_refs=(
                f"test:verified-original-task:{axis}",
                f"test:verified-owner-state:{axis}",
            ),
            independent_method_refs=(
                "https://www.nasa.gov/reference/4-0-system-design-processes/",
                "https://asq.org/quality-resources/a3-report",
            ),
            counterexample_refs=(f"test:unrelated-counterexample:{axis}",),
            outcome_verification_refs=(f"test:unrelated-output:{axis}",),
            finding="Cake frosting technique determines the user's GitHub agent authority.",
            alternative="Use garden pruning cadence instead of repairing the host invocation boundary.",
            task_implication="Change a user's business source authority based on unrelated horticulture.",
            covered_concerns=(
                FULL_RESEARCH_CONCERNS if idx == 0 else (FULL_RESEARCH_CONCERNS[idx],)
            ),
            cross_axes=tuple(other for other in FULL_RESEARCH_AXES if other != axis)[:2],
        )
        for idx, axis in enumerate(FULL_RESEARCH_AXES)
    )
    study = FullDimensionStudy(
        studies=studies,
        emerging_unknowns=("How cake temperature controls GitHub authentication.",),
    )

    # A source-existence verifier (or indiscriminate True stub) cannot judge
    # relevance, causal fit or business outcome. Current admission passes this.
    with pytest.raises(EntryAdmissionError):
        admit_full_dimension_study(study, verify_evidence=lambda _ref: True)
