"""All utterances evaluated by existing cognition/evolution routing, NOT automatically promoted.

Controlled host tests; repository code does not physically intercept native ChatGPT.
"""
from dataclasses import replace
from hashlib import sha256

import pytest

from uaos.runtime.epistemic_entry import (
    EntryAdmissionError,
    EntrySignal,
    TurnEvolutionCoverage,
    TurnUtteranceAssessment,
    UtteranceOrigin,
    admit_turn_evolution_coverage,
)


USER = "Every utterance should be reviewed, including assistant progress claims."
ASSISTANT = "Current controller task RUNNING; controlled progress review remains open."
TOOL = "GitHub source inspection reports a task/progress status mismatch."
REFS = ("session:user-1", "session:tool-1", "session:assistant-final")


def digest(text):
    return sha256(text.encode()).hexdigest()


def item(source, origin, text, signal=EntrySignal.NO_MATERIAL_GAP):
    return TurnUtteranceAssessment(
        source_ref=source, origin=origin,
        source_sha256=digest(text),
        signal=signal,
        judgment_evidence_ref="test:judgment:" + source,
        alternative_or_no_gap_reason_ref="test:challenge:" + source,
    )


def review():
    return TurnEvolutionCoverage(
        observed_source_refs=REFS,
        assessments=(
            item(REFS[0], UtteranceOrigin.USER, USER, EntrySignal.CLAIM_OR_CAUSAL_SUGGESTION),
            item(REFS[1], UtteranceOrigin.TOOL, TOOL, EntrySignal.SYSTEM_OR_RULE_CONTRADICTION),
            item(REFS[2], UtteranceOrigin.ASSISTANT, ASSISTANT, EntrySignal.NO_MATERIAL_GAP),
        ),
        assistant_final_ref=REFS[2],
        evolution_routing_ref="test:evolution-triaged",
    )


def _verify_source(ref, sha):
    return {REFS[0]: digest(USER), REFS[1]: digest(TOOL)}.get(ref) == sha


def _call(input_review, **kwargs):
    return admit_turn_evolution_coverage(
        input_review,
        actual_assistant_response=kwargs.get("response", ASSISTANT),
        host_observed_source_refs=kwargs.get("observed", REFS),
        verify_source_digest=kwargs.get("source_verifier", _verify_source),
        verify_judgment_ref=kwargs.get("judgment_verifier", lambda ref: ref.startswith("test:")),
    )


def test_user_tool_and_real_assistant_output_are_all_covered():
    receipt = _call(review())
    assert receipt.assessed_count == 3
    assert receipt.problem_signal_observed
    assert receipt.hypothesis_challenge_required
    assert receipt.evolution_routing_ref == "test:evolution-triaged"


def test_no_message_may_be_skipped_even_if_prior_review_says_clean():
    missing = replace(review(), assessments=(review().assessments[0], review().assessments[2]))
    with pytest.raises(EntryAdmissionError, match="not every"):
        _call(missing)
    with pytest.raises(EntryAdmissionError, match="differs from host-observed"):
        _call(review(), observed=REFS + ("session:assistant-progress",))


def test_actual_assistant_final_must_match_reviewed_text():
    with pytest.raises(EntryAdmissionError, match="actual draft differs"):
        _call(review(), response=ASSISTANT + "\n状态：COMPLETE")


def test_self_certifying_unverified_user_input_or_reflection_fails():
    with pytest.raises(EntryAdmissionError, match="unverified utterance"):
        _call(review(), source_verifier=lambda _ref, _digest: False)
    with pytest.raises(EntryAdmissionError, match="unverified evolution"):
        _call(review(), judgment_verifier=lambda _ref: False)


def test_no_fake_coverage_when_user_or_assistant_missing():
    no_user = replace(
        review(),
        observed_source_refs=REFS[1:],
        assessments=review().assessments[1:],
    )
    with pytest.raises(EntryAdmissionError, match="user input must be included"):
        _call(no_user, observed=REFS[1:])
    no_assistant = replace(
        review(),
        observed_source_refs=REFS[:2],
        assessments=review().assessments[:2],
    )
    with pytest.raises(EntryAdmissionError, match="outgoing assistant message"):
        _call(no_assistant, observed=REFS[:2])


def test_ordinary_low_signal_input_is_reviewed_without_forced_evolution_transaction():
    low = replace(review(), assessments=tuple(
        replace(item_, signal=EntrySignal.NO_MATERIAL_GAP) for item_ in review().assessments
    ))
    receipt = _call(low)
    assert receipt.assessed_count == 3
    assert not receipt.problem_signal_observed
    assert not receipt.material_knowledge_gap_observed
    assert not receipt.hypothesis_challenge_required


def test_unverified_host_enumeration_never_counts_as_native_assurance():
    with pytest.raises(EntryAdmissionError, match="independently enumerated"):
        _call(review(), observed=None)
    with pytest.raises(EntryAdmissionError, match="independently enumerated"):
        _call(review(), judgment_verifier=None)


def test_message_origin_and_digest_shapes_are_required():
    with pytest.raises(EntryAdmissionError, match="lowercase sha256"):
        item("bad", UtteranceOrigin.USER, USER, EntrySignal.NO_MATERIAL_GAP).__class__(
            "bad", UtteranceOrigin.USER, "fake", EntrySignal.NO_MATERIAL_GAP,
            "test:claim", "test:disproof"
        )


def test_unfinished_authorized_work_is_not_collapsed_into_generic_challenge():
    baseline = review()
    tool_work = replace(
        baseline.assessments[1],
        signal=EntrySignal.UNFINISHED_AUTHORIZED_WORK,
    )
    receipt = _call(replace(baseline, assessments=(baseline.assessments[0], tool_work, baseline.assessments[2])))
    assert receipt.unfinished_authorized_work_observed
    assert not receipt.problem_signal_observed
