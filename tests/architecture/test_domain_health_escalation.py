from uaos.kernel.domain_health import (
    DomainObservation,
    ExternalSkillCandidate,
    HealthFindingType,
    ParentUpcall,
    Severity,
    assess_domain_health,
    assess_external_skill_candidate,
    cluster_cross_domain_failures,
    triage_parent_upcalls,
)


def _upcall(
    escalation_id: str,
    domain_id: str,
    *,
    severity: Severity = Severity.HIGH,
    conflict_keys: tuple[str, ...] = (),
    failure_class: str | None = None,
    capability_id: str | None = None,
):
    return ParentUpcall(
        escalation_id=escalation_id,
        domain_id=domain_id,
        domain_revision="rev-current",
        problem_ref=f"problem:{escalation_id}",
        severity=severity,
        impact="material quality/reliability impact",
        blocking_scope="affected capability only",
        suspected_layer="COMMON_CAPABILITY",
        evidence_refs=(f"evidence:{escalation_id}",),
        local_recovery_attempts=("owner-native recovery attempted",),
        requested_parent_help="diagnose common control-plane contribution",
        can_continue_unaffected_work=True,
        conflict_keys=conflict_keys,
        failure_class=failure_class,
        capability_id=capability_id,
    )


def test_parent_child_revision_drift_is_detected_instead_of_treating_parent_cache_as_authority():
    receipt = assess_domain_health(
        DomainObservation(
            domain_id="video",
            current_revision="0.8.0/profile9@02d39d8e",
            parent_observed_revision="0.7.0/profile8@55f605e6",
        )
    )
    assert not receipt.healthy
    assert receipt.findings[0].finding_type == HealthFindingType.PARENT_CHILD_REVISION_DRIFT
    assert "current child" in receipt.findings[0].summary


def test_declared_inherited_behavior_without_owner_native_evidence_is_visible():
    receipt = assess_domain_health(
        DomainObservation(
            domain_id="ashare",
            current_revision="0.3.0/profile5",
            common_behavior_required=True,
            common_behavior_binding_present=False,
            inherited_behavior_claims=("problem_to_action_closure", "recover_before_user_escalation"),
            operational_evidence_capabilities=(),
        )
    )
    types = {finding.finding_type for finding in receipt.findings}
    assert HealthFindingType.COMMON_BEHAVIOR_BINDING_MISSING in types
    assert HealthFindingType.DECLARED_WITHOUT_OPERATIONAL_EVIDENCE in types


def test_pending_material_change_is_flagged_before_execution_when_failure_recovery_scenario_is_missing():
    receipt = assess_domain_health(
        DomainObservation(
            domain_id="video",
            current_revision="0.8.0/profile10",
            material_change_pending=True,
        )
    )
    assert not receipt.healthy
    finding = next(item for item in receipt.findings if item.finding_type is HealthFindingType.SCENARIO_OR_RECOVERY_GAP)
    assert finding.severity is Severity.HIGH
    assert "pre-change" in finding.summary


def test_pending_material_change_with_owner_native_failure_scenario_does_not_create_scenario_gap():
    receipt = assess_domain_health(
        DomainObservation(
            domain_id="video",
            current_revision="0.8.0/profile10",
            material_change_pending=True,
            failure_recovery_scenario_evidence_refs=("scenario://premortem/stale-authority",),
        )
    )
    assert HealthFindingType.SCENARIO_OR_RECOVERY_GAP not in {item.finding_type for item in receipt.findings}


def test_multiple_nonconflicting_child_upcalls_do_not_form_one_global_fifo_blocker():
    selection = triage_parent_upcalls(
        (
            _upcall("esc-fin", "financial_writing"),
            _upcall("esc-video", "video"),
            _upcall("esc-novel", "novel"),
        ),
        max_slots=3,
    )
    assert {item.work_unit_id for item in selection.selected} == {"esc-fin", "esc-video", "esc-novel"}
    assert not selection.deferred


def test_only_shared_resource_conflicts_serialize():
    selection = triage_parent_upcalls(
        (
            _upcall("esc-fin", "financial_writing", conflict_keys=("COMMON:behavior-assurance",)),
            _upcall("esc-ashare", "ashare", conflict_keys=("COMMON:behavior-assurance",)),
            _upcall("esc-video", "video", conflict_keys=("DOMAIN:video",)),
        ),
        max_slots=3,
    )
    selected = {item.work_unit_id for item in selection.selected}
    deferred = {item.work_unit_id for item in selection.deferred}
    assert "esc-video" in selected
    assert len(selected.intersection({"esc-fin", "esc-ashare"})) == 1
    assert len(deferred.intersection({"esc-fin", "esc-ashare"})) == 1


def test_same_failure_class_across_domains_is_clustered_for_common_diagnosis():
    clusters = cluster_cross_domain_failures(
        (
            _upcall("esc-fin", "financial_writing", failure_class="FC-INHERITANCE-OPERATION-GAP"),
            _upcall("esc-ashare", "ashare", failure_class="FC-INHERITANCE-OPERATION-GAP"),
            _upcall("esc-video", "video", failure_class="FC-OTHER"),
        )
    )
    assert len(clusters) == 1
    assert clusters[0].cluster_key == "failure_class:FC-INHERITANCE-OPERATION-GAP"
    assert clusters[0].domain_ids == ("ashare", "financial_writing")


def test_external_skill_stays_candidate_until_source_security_overlap_and_evaluation_are_evidenced():
    blocked = assess_external_skill_candidate(
        ExternalSkillCandidate(
            skill_id="agent-introspection-debugging",
            source_ref="skillsmp/source",
            mapped_need_or_failure_class="FC-ACTIVE-DETECTION-GAP",
            source_inspected=True,
            companion_files_inspected=False,
            security_and_permissions_reviewed=False,
            existing_overlap_assessed=True,
            evaluation_refs=(),
        )
    )
    assert not blocked.promotable_candidate
    assert "bounded_evaluation" in blocked.missing_evidence

    admitted = assess_external_skill_candidate(
        ExternalSkillCandidate(
            skill_id="agent-introspection-debugging",
            source_ref="skillsmp/source",
            mapped_need_or_failure_class="FC-ACTIVE-DETECTION-GAP",
            source_inspected=True,
            companion_files_inspected=True,
            security_and_permissions_reviewed=True,
            existing_overlap_assessed=True,
            evaluation_refs=("eval:scenario-1",),
        )
    )
    assert admitted.promotable_candidate
    assert not admitted.missing_evidence
