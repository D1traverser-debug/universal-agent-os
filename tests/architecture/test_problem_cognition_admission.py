import pytest

from uaos.kernel import (
    ActionCandidate,
    CognitiveSearchMode,
    DeliberationEvidence,
    DeliberationSignals,
    HypothesisDisposition,
    ProblemHypothesis,
    ProblemLayer,
    RootScopeAdmissionError,
    RootScopeAssessment,
    architecture_reassessment_required,
    durable_problem_record_required,
    require_root_scope_admission,
)


def _evidence(*, external: bool = True, independent: bool = False) -> DeliberationEvidence:
    values = {
        "MICRO_DIAGNOSIS": ("evidence://micro",),
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT": ("evidence://macro",),
        "GOVERNING_ASSUMPTION_CHALLENGE": ("evidence://assumption",),
        "COUNTEREXAMPLE_SEARCH": ("evidence://counterexample",),
    }
    if external:
        values["EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH"] = ("evidence://research",)
    if independent:
        values["INDEPENDENT_VERIFICATION"] = ("evidence://independent",)
    return DeliberationEvidence(values)


def _hypothesis(hypothesis_id: str, layer: ProblemLayer, disposition: HypothesisDisposition) -> ProblemHypothesis:
    return ProblemHypothesis(
        hypothesis_id=hypothesis_id,
        layer=layer,
        statement=f"candidate cause at {layer.value}",
        disposition=disposition,
        supporting_evidence_refs=(f"evidence://support/{hypothesis_id}",),
        falsification_or_rejection_refs=(f"evidence://probe/{hypothesis_id}",),
    )


def _actions(*, structured: bool = False):
    items = [
        ActionCandidate("local-fix", ProblemLayer.LOCAL_IMPLEMENTATION, "repair narrow owner", ("evidence://action/local",), ("tradeoff://local",)),
        ActionCandidate("workflow-fix", ProblemLayer.DOMAIN_WORKFLOW, "repair workflow contract", ("evidence://action/workflow",), ("tradeoff://workflow",)),
    ]
    if structured:
        items.append(ActionCandidate("no-change", ProblemLayer.CONTROL_PLANE, "preserve current architecture", ("evidence://action/no-change",), ("tradeoff://no-change",), True))
    return tuple(items)


def test_local_problem_can_be_admitted_after_evidence_tested_root_scope():
    signals = DeliberationSignals(repeated_failure_count=1)
    receipt = require_root_scope_admission(
        signals,
        _evidence(external=False),
        RootScopeAssessment(
            hypotheses=(_hypothesis("local", ProblemLayer.LOCAL_IMPLEMENTATION, HypothesisDisposition.SELECTED),),
            selected_hypothesis_id="local",
        ),
    )
    assert receipt.selected_layer is ProblemLayer.LOCAL_IMPLEMENTATION
    assert receipt.hypothesis_count == 1
    assert receipt.search_mode is CognitiveSearchMode.LIGHTWEIGHT
    assert receipt.durable_problem_record_required is False


def test_user_correction_requires_contrastive_hypotheses_and_actions():
    signals = DeliberationSignals(user_correction=True)
    with pytest.raises(RootScopeAdmissionError, match="at least 2 hypotheses"):
        require_root_scope_admission(
            signals,
            _evidence(external=False),
            RootScopeAssessment(
                hypotheses=(_hypothesis("local", ProblemLayer.LOCAL_IMPLEMENTATION, HypothesisDisposition.SELECTED),),
                selected_hypothesis_id="local",
            ),
        )
    receipt = require_root_scope_admission(
        signals,
        _evidence(external=False),
        RootScopeAssessment(
            hypotheses=(
                _hypothesis("local", ProblemLayer.LOCAL_IMPLEMENTATION, HypothesisDisposition.SELECTED),
                _hypothesis("workflow", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.REJECTED),
            ),
            selected_hypothesis_id="local",
            action_candidates=_actions(),
        ),
    )
    assert receipt.search_mode is CognitiveSearchMode.CONTRASTIVE
    assert receipt.action_candidate_count == 2


def test_repeated_or_cross_subsystem_problem_requires_architecture_reassessment():
    signals = DeliberationSignals(repeated_failure_count=2, cross_subsystem=True)
    assert architecture_reassessment_required(signals) is True
    assert durable_problem_record_required(signals) is True
    with pytest.raises(RootScopeAdmissionError, match="at least two layers"):
        require_root_scope_admission(
            signals,
            _evidence(independent=True),
            RootScopeAssessment(
                hypotheses=(
                    _hypothesis("local", ProblemLayer.LOCAL_IMPLEMENTATION, HypothesisDisposition.SELECTED),
                    _hypothesis("local2", ProblemLayer.LOCAL_IMPLEMENTATION, HypothesisDisposition.REJECTED),
                ),
                selected_hypothesis_id="local",
                architecture_reassessment_refs=("evidence://architecture",),
                action_candidates=_actions(structured=True),
            ),
        )


def test_systemic_problem_can_select_local_cause_only_after_upstream_alternative_is_tested():
    signals = DeliberationSignals(repeated_failure_count=2, cross_subsystem=True)
    receipt = require_root_scope_admission(
        signals,
        _evidence(independent=True),
        RootScopeAssessment(
            hypotheses=(
                _hypothesis("local", ProblemLayer.LOCAL_IMPLEMENTATION, HypothesisDisposition.SELECTED),
                _hypothesis("control", ProblemLayer.CONTROL_PLANE, HypothesisDisposition.REJECTED),
            ),
            selected_hypothesis_id="local",
            architecture_reassessment_refs=("evidence://architecture/control-plane-excluded",),
            action_candidates=_actions(structured=True),
        ),
    )
    assert receipt.selected_layer is ProblemLayer.LOCAL_IMPLEMENTATION
    assert receipt.architecture_reassessment_performed is True
    assert receipt.durable_problem_record_required is True
    assert ProblemLayer.CONTROL_PLANE in receipt.compared_layers
    assert receipt.action_candidate_count == 3


def test_material_problem_is_not_allowed_to_skip_upstream_review_or_durable_record():
    signals = DeliberationSignals(material_problem=True)
    assert architecture_reassessment_required(signals) is True
    assert durable_problem_record_required(signals) is True
    with pytest.raises(RootScopeAdmissionError):
        require_root_scope_admission(
            signals,
            _evidence(independent=True),
            RootScopeAssessment(
                hypotheses=(_hypothesis("local", ProblemLayer.LOCAL_IMPLEMENTATION, HypothesisDisposition.SELECTED),),
                selected_hypothesis_id="local",
                action_candidates=_actions(structured=True),
            ),
        )


def test_user_or_external_claim_cannot_be_promoted_directly_to_root_cause():
    signals = DeliberationSignals(user_correction=True, repeated_failure_count=1)
    with pytest.raises(RootScopeAdmissionError, match="promoted without falsification"):
        require_root_scope_admission(
            signals,
            _evidence(external=False),
            RootScopeAssessment(
                hypotheses=(_hypothesis("architecture", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.SELECTED),),
                selected_hypothesis_id="architecture",
                direct_user_or_external_claim_promoted_without_test=True,
            ),
        )


def test_systemic_problem_requires_rejected_alternative_and_architecture_evidence():
    signals = DeliberationSignals(architecture_gap=True, repeated_failure_count=2)
    with pytest.raises(RootScopeAdmissionError, match="evidence-rejected alternative"):
        require_root_scope_admission(
            signals,
            _evidence(),
            RootScopeAssessment(
                hypotheses=(
                    _hypothesis("architecture", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.SELECTED),
                    _hypothesis("local", ProblemLayer.LOCAL_IMPLEMENTATION, HypothesisDisposition.PLAUSIBLE),
                ),
                selected_hypothesis_id="architecture",
                architecture_reassessment_refs=("evidence://architecture",),
                action_candidates=_actions(structured=True),
            ),
        )
