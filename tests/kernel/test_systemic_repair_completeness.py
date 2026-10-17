import pytest

from uaos.kernel.cognition_case import CognitionCaseReceipt
from uaos.kernel.deliberation import CognitiveSearchMode, ProblemLayer
from uaos.kernel.problem_closure import (
    EvolutionDisposition,
    ProblemClosureDecision,
    ProblemClosureError,
    ProblemClosureSignals,
    assess_problem_closure,
)


def _receipt(*, layer: ProblemLayer) -> CognitionCaseReceipt:
    return CognitionCaseReceipt(
        case_id="systemic-repair-case",
        search_mode=CognitiveSearchMode.STRUCTURED,
        supported_factor_ids=("f-owner",),
        rejected_factor_ids=("f-leaf-only",),
        compared_layers=(ProblemLayer.LOCAL_IMPLEMENTATION, ProblemLayer.CONTROL_PLANE),
        intervention_candidate_id="repair",
        intervention_layer=layer,
        intervention_no_change_baseline=False,
        architecture_reassessment_performed=True,
        architecture_experience_admitted=False,
        durable_problem_record_required=True,
        evidence_ids=("failure", "owner", "sibling", "dup", "bounded", "generalize", "recurrence"),
        verification_methods=("scope-scan",),
        validation_methods=("generalization-replay",),
        systemic=True,
    )


def _signals(*, layer: ProblemLayer, bounded_local: bool = False) -> ProblemClosureSignals:
    scope = ("failure", "owner", "sibling", "dup")
    return ProblemClosureSignals(
        problem_detected=True,
        repair_attempted=True,
        repair_verified=True,
        cognition_case_receipt=_receipt(layer=layer),
        evolution_disposition=EvolutionDisposition.DURABLE_EVOLUTION_UPDATED,
        problem_record_required=True,
        problem_record_ref="issue://77",
        terminal_action_candidate_id="repair",
        verification_evidence_refs=scope + (("bounded",) if bounded_local else ()),
        validation_evidence_refs=("generalize", "recurrence"),
        systemic_scope_evidence_refs=scope + (("bounded",) if bounded_local else ()),
        failure_class_evidence_ref="failure",
        owning_abstraction_evidence_ref="owner",
        sibling_path_evidence_refs=("sibling",),
        duplication_or_supersession_evidence_refs=("dup",),
        local_scope_bounded_evidence_refs=("bounded",) if bounded_local else (),
        generalization_evidence_refs=("generalize",),
        recurrence_detection_evidence_refs=("recurrence",),
    )


def test_systemic_repair_cannot_close_with_verification_and_validation_only():
    signals = ProblemClosureSignals(
        problem_detected=True,
        repair_attempted=True,
        repair_verified=True,
        cognition_case_receipt=_receipt(layer=ProblemLayer.CONTROL_PLANE),
        evolution_disposition=EvolutionDisposition.DURABLE_EVOLUTION_UPDATED,
        problem_record_ref="issue://77",
        terminal_action_candidate_id="repair",
        verification_evidence_refs=("failure",),
        validation_evidence_refs=("generalize",),
    )
    with pytest.raises(ProblemClosureError, match="failure-class scope evidence"):
        assess_problem_closure(signals)


def test_owner_level_systemic_repair_closes_when_failure_class_is_generalized_and_detectable():
    decision = assess_problem_closure(
        _signals(layer=ProblemLayer.CONTROL_PLANE)
    )
    assert decision is ProblemClosureDecision.REPAIR_EXECUTED


def test_local_intervention_cannot_close_systemic_case_without_evidence_that_scope_is_leaf_bounded():
    with pytest.raises(ProblemClosureError, match="genuinely bounded"):
        assess_problem_closure(
            _signals(layer=ProblemLayer.LOCAL_IMPLEMENTATION)
        )


def test_local_intervention_may_close_systemic_case_when_scope_evidence_proves_leaf_boundary():
    decision = assess_problem_closure(
        _signals(layer=ProblemLayer.LOCAL_IMPLEMENTATION, bounded_local=True)
    )
    assert decision is ProblemClosureDecision.REPAIR_EXECUTED


def test_generalization_and_recurrence_must_be_validation_evidence_not_self_attested_labels():
    signals = _signals(layer=ProblemLayer.CONTROL_PLANE)
    invalid = ProblemClosureSignals(
        **{
            field: getattr(signals, field)
            for field in signals.__dataclass_fields__
            if field != "validation_evidence_refs"
        },
        validation_evidence_refs=("generalize",),
    )
    with pytest.raises(ProblemClosureError, match="recurrence-detection evidence"):
        assess_problem_closure(invalid)
