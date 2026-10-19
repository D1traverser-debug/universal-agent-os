"""Product acceptance guard is wired into *existing* controlled finalization."""
import pytest
from hashlib import sha256

from uaos.kernel.cognition_case import EvidenceItem, EvidenceKind
from uaos.kernel.domain_health import DomainObservation, ProductOutcomeEvidence
from uaos.runtime.epistemic_entry import (
    FullDimensionStudy, DimensionResearch, FULL_RESEARCH_AXES, FULL_RESEARCH_CONCERNS,
    ControllerEpistemicEntry, EntryObservation, EntrySignal,
    TurnEvolutionCoverage, TurnUtteranceAssessment, UtteranceOrigin,
)
from uaos.runtime.finalization import FinalizationBlocked, FinalizationContext, admit_final_response

HEAD = "e580cd4dfda8db47674803451c9adfff9e3cf975"
DIMS = ("requirements_consumed", "current_research", "reader_value", "word_delivered")


def _entry():
    return ControllerEpistemicEntry(
        objective_ref="receipt:objective", state_ref="receipt:state",
        governing_assumption_review_ref="receipt:challenge", next_action_ref="receipt:next",
        observations=(EntryObservation(
            EntrySignal.NO_MATERIAL_GAP,
            EvidenceItem("e:current", EvidenceKind.REPOSITORY_FACT,
                         "Current controller authority was checked.", "receipt:source"),
        ),),
    )


def _reply():
    return """当前 Agent：UAOS
当前范围或任务：Financial product closure controlled test
Authority：UAOS
状态：RUNNING
当前阶段：independent quality admission
下一动作或阻塞：product outcome assessed
Evolution：NO_EVOLUTION_TRIGGER
Deliberation：NOT_TRIGGERED
版本：controlled
进度时间：2026-10-18
"""


def _turn_coverage():
    user_data = b"controlled financial owner request"
    return TurnEvolutionCoverage(
        observed_source_refs=("test:financial-user", "test:financial-agent"),
        assessments=(
            TurnUtteranceAssessment(
                source_ref="test:financial-user", origin=UtteranceOrigin.USER,
                source_sha256=sha256(user_data).hexdigest(),
                signal=EntrySignal.NO_MATERIAL_GAP,
                judgment_evidence_ref="test:user-verdict",
                alternative_or_no_gap_reason_ref="test:user-challenge",
            ),
            TurnUtteranceAssessment(
                source_ref="test:financial-agent", origin=UtteranceOrigin.ASSISTANT,
                source_sha256=sha256(_reply().encode()).hexdigest(),
                signal=EntrySignal.NO_MATERIAL_GAP,
                judgment_evidence_ref="test:assistant-verdict",
                alternative_or_no_gap_reason_ref="test:assistant-challenge",
            ),
        ),
        assistant_final_ref="test:financial-agent",
        evolution_routing_ref="test:clean-evolution-evaluated",
    )


def _turn_kwargs():
    return dict(
        turn_evolution_coverage=_turn_coverage(),
        observed_turn_source_refs=("test:financial-user", "test:financial-agent"),
        observed_turn_source_origins={"test:financial-user": UtteranceOrigin.USER, "test:financial-agent": UtteranceOrigin.ASSISTANT},
        turn_source_digest_verifier=lambda ref, digest: (
            ref == "test:financial-user" and digest == sha256(b"controlled financial owner request").hexdigest()
        ),
        turn_judgment_verifier=lambda ref: ref.startswith("test:"),
    )


def _case(**updates):
    data=dict(domain_id="financial_writing",child_revision=HEAD,
              objective_ref="receipt:objective",required_dimensions=DIMS,
              dimension_evidence=(("requirements_consumed","receipt:requirements"),),
              independently_adjudicated_outcome_ref=None,
              open_rejection_refs=("receipt:historic-rejection",))
    data.update(updates)
    return ProductOutcomeEvidence(**data)



def _full_dimension_study():
    return FullDimensionStudy(
        studies=tuple(
            DimensionResearch(
                axis=axis,
                local_evidence_refs=(f"test:{axis}:current", f"test:{axis}:historical"),
                independent_method_refs=(f"test:{axis}:method-a", f"test:{axis}:method-b"),
                counterexample_refs=(f"test:{axis}:falsifier",),
                outcome_verification_refs=(f"test:{axis}:outcome",),
                finding=f"Observed and researched {axis} as a separate system dimension.",
                alternative=f"Independent alternative to the first {axis} interpretation.",
                task_implication=f"Check {axis} interactions against actual task outcome.",
                covered_concerns=FULL_RESEARCH_CONCERNS if i == 0 else (FULL_RESEARCH_CONCERNS[i],),
                cross_axes=tuple(x for x in FULL_RESEARCH_AXES if x != axis)[:2],
            )
            for i, axis in enumerate(FULL_RESEARCH_AXES)
        ),
        emerging_unknowns=("Unexpected boundary between tools and governing objectives",),
    )


def _ctx(case=None, **updates):
    data=dict(context_selected=True,controller_selected=True,
              full_dimension_study=_full_dimension_study(),
              controller_epistemic_entry=_entry(),
              entry_evidence_verifier=lambda _: True,
              **_turn_kwargs(),
              governed_product_outcome_completion_requested=True,
              governed_product_outcome_observation=DomainObservation(
                  domain_id="financial_writing",current_revision=HEAD),
              governed_product_outcome_evidence=case or _case(),
              governed_product_outcome_verifier=lambda _: True)
    data.update(updates)
    return FinalizationContext(**data)


def test_ci_only_financial_claim_is_rejected_at_real_finalization_gate():
    with pytest.raises(FinalizationBlocked,match="PRODUCT_OUTCOME_NOT_VALIDATED"):
        admit_final_response(_reply(), _ctx())


def test_even_complete_self_filled_pass_does_not_work_without_verifier():
    evidence=tuple((name,"self:" + name) for name in DIMS)
    with pytest.raises(FinalizationBlocked,match="PRODUCT_OUTCOME_NOT_VALIDATED"):
        admit_final_response(
            _reply(), _ctx(_case(dimension_evidence=evidence,
                                independently_adjudicated_outcome_ref="self:pass",
                                open_rejection_refs=()),
                           governed_product_outcome_verifier=None)
        )


def test_old_release_cannot_validate_current_financial_article():
    with pytest.raises(FinalizationBlocked,match="current child revision"):
        admit_final_response(
            _reply(), _ctx(_case(child_revision="f261367eb480c884880890513752afc77d1ef916"))
        )


def test_product_closure_cannot_execute_as_ordinary_child_without_parent_authority():
    with pytest.raises(FinalizationBlocked,match="PRODUCT_OUTCOME_COMPLETION_REQUIRES_CONTROLLER_AUTHORITY"):
        admit_final_response(
            _reply(), FinalizationContext(
                context_selected=True,controller_selected=False,
                governed_product_outcome_completion_requested=True,
                governed_product_outcome_observation=DomainObservation(
                    domain_id="financial_writing",current_revision=HEAD),
                governed_product_outcome_evidence=_case(),
                governed_product_outcome_verifier=lambda _: True,
            )
        )


def test_product_data_not_required_on_normal_clean_controller_turn():
    no_close=FinalizationContext(
        context_selected=True,controller_selected=True,
        full_dimension_study=_full_dimension_study(),
        controller_epistemic_entry=_entry(),
        entry_evidence_verifier=lambda _: True,
        **_turn_kwargs(),
    )
    receipt=admit_final_response(_reply(),no_close)
    assert receipt.adherence.passed
    with pytest.raises(FinalizationBlocked,match="UNSOLICITED_PRODUCT_OUTCOME_CLOSURE_EVIDENCE"):
        admit_final_response(
            _reply(), _ctx(governed_product_outcome_completion_requested=False)
        )


def test_synthetic_full_evidence_can_pass_controlled_gate_without_claiming_live_success():
    full=_case(
        dimension_evidence=tuple((name,"receipt:" + name) for name in DIMS),
        independently_adjudicated_outcome_ref="receipt:distinct-reviewer",
        open_rejection_refs=(),
    )
    receipt=admit_final_response(_reply(),_ctx(full))
    assert receipt.adherence.passed  # synthetic contract test ONLY
