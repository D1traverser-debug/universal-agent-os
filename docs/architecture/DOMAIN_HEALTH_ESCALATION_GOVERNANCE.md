# Domain Health & Parent-Guidance Escalation Governance

Status: candidate architecture evidence
Date: 2026-10-15
Requirement authority: `docs/requirements/FROZEN_REQUIREMENTS_v2.1.md`
Policy: `config/DOMAIN_HEALTH_ESCALATION_POLICY.json`

## Governing outcome

Registered child Agents should inherit UAOS common cognition/evolution behavior in an operationally observable way, discover relevant control-plane problems before repeated user correction where feasible, and obtain parent guidance without turning UAOS into a single global blocking queue or a child-business proxy.

This extends existing Control / Assurance / Evolution / Scheduling surfaces. It does **not** create a second controller, domain business-state mirror or independent parent scheduler.

## Observed failure classes

1. `FC-PARENT-CHILD-FRESHNESS-SNAPSHOT-MASQUERADING-AS-CURRENT-001`
   - Financial parent verification still named 0.9.2/profile17 while current child authority was 1.0.1/profile18.
   - Video parent verification still named 0.7.0/profile8 while current child authority was 0.8.0/profile9.
   - Existing tests asserted those old snapshots as “current”, so a green parent CI could coexist with stale child observation.

2. `FC-INHERITED-BEHAVIOR-DECLARATION-WITHOUT-UNIFORM-OPERATIONAL-PROOF-002`
   - Parent policy already says declaration is not operational proof.
   - Financial, Novel and Video expose owner-native behavior admission/evidence.
   - Current A-share binding/capabilities reference common cognition but do not expose the same current `COMMON_BEHAVIOR_ASSURANCE` binding and owner-native repair/escalation admission.

3. `FC-PARENT-GUIDANCE-SINGLE-QUEUE-BLOCKING-RISK-003`
   - Parent upcalls had semantics but no explicit multi-upcall bulkhead contract. A naïve implementation could serialize all child help requests behind one difficult case.

4. `FC-PROACTIVE-UNKNOWN-FAILURE-DISCOVERY-GAP-004`
   - Turn-level problem detection is strong once a signal is visible, but there was no first-class control-plane contract requiring child freshness scans, inherited-behavior probes, cross-domain failure clustering and failure/recovery experiments.

## External method evidence

- AWS Well-Architected, REL10 bulkheads: isolate faults so unrelated cells/components keep operating. Applied here as domain/upcall fault boundaries rather than infrastructure cells.
- AWS Well-Architected, REL08 resiliency testing: deliberately exercise disruptive scenarios to expose unanticipated weaknesses; it explicitly warns against focusing only on known issues and identifying failures without resolution.
- Google SRE postmortem analysis: structured incident/root-cause data can be aggregated to discover systemic failure classes and target larger investments.
- SkillsMP: useful as a public pattern-discovery corpus but explicitly does not certify quality or safety. Candidate Skills such as `agent-introspection-debugging`, `agent-native-architecture` and `verification-loop` reinforce capture/diagnose/contained-recovery, explicit contracts, and verification loops; they are treated as external candidates, not imported authority.

References:
- https://docs.aws.amazon.com/wellarchitected/latest/framework/rel-10.html
- https://docs.aws.amazon.com/wellarchitected/2025-02-25/framework/rel_tracking_change_management_resiliency_testing.html
- https://sre.google/workbook/postmortem-analysis/
- https://skillsmp.com/

## Architecture concerns and selected views

### C1 — Inheritance observability
Structural concern: a child can point at common policy while behavior is not actually realized.

Selected view: authority/evidence chain.

`UAOS common capability -> child binding -> owner-native invocation/admission -> receipt/replay/evidence -> bounded assurance claim`

A missing link downgrades only the affected behavior to `DECLARED_ONLY/UNVERIFIED`.

### C2 — Parent/child freshness
Temporal concern: child production may advance after a parent verification snapshot.

Selected view: observation lifecycle.

`read registered child current authority -> compare parent cache -> record drift finding -> reconcile/refresh observation -> keep child as authority`

The parent cache is never allowed to overwrite child truth.

### C3 — Multiple simultaneous upcalls
Structural + temporal concern: one difficult escalation must not stall unrelated domains.

Selected view: conflict-key scheduling/bulkhead.

`upcalls -> impact/severity triage -> conflict-key selection -> parallel non-conflicting diagnosis -> serialize only shared-resource conflicts -> return child guidance/repair`

Implementation reuses `select_non_conflicting` from `src/uaos/kernel/scheduling.py`.

### C4 — Unknown failure discovery
Causal/operability concern: a system can pass known tests yet still contain interaction failures.

Selected view: layered discovery loop.

`static authority/contract scan -> scenario/recovery walkthrough -> bounded failure injection/replay -> live observation -> causal history -> cross-domain clustering -> scoped evolution`

No layer claims complete coverage of unknown unknowns.

## CURRENT_AGENT dogfood walkthroughs

### S1 — Parent asks “are all children current?”

1. CURRENT_AGENT reads `SYSTEM_MAP` and `DOMAIN_HEALTH_INDEX`.
   - Progress evidence: registered domain and latest observed revision are explicit.
   - Failure risk: treating cache as authority.
   - Recovery: policy says reread child current authority; mismatch becomes a finding.
2. CURRENT_AGENT compares current child evidence to parent observations.
   - Progress evidence: Financial 1.0.1/profile18 and Video 0.8.0/profile9 differ from historical `CURRENT_SYSTEM` snapshots.
   - Failure risk: green stale tests create false confidence.
   - Recovery: health finding remains open until observation semantics/tests are reconciled.

### S2 — Three children request parent help at once

1. Financial, A-share and Video each provide a structured upcall.
   - Progress evidence: each has domain revision, problem ref, impact, layer, evidence and local recovery attempts.
   - Failure risk: a global FIFO queue serializes all three.
   - Recovery: convert upcalls to existing `RunnableWork` with explicit conflict keys.
2. Parent selects non-conflicting work.
   - Progress evidence: unrelated domain/resource keys are selected concurrently up to capacity.
   - Failure risk: two common-capability repairs race on the same parent authority.
   - Recovery: shared conflict key serializes only those two; unrelated work continues.

### S3 — Child says it inherited “进化+认知” but user still has to remind it

1. CURRENT_AGENT checks child declaration and owner-native evidence separately.
   - Progress evidence: declaration and evidence are distinct fields/findings.
   - Failure risk: `UAOS_HOSTED` marker is mistaken for proof.
   - Recovery: absent invocation/receipt/replay evidence yields `DECLARED_WITHOUT_OPERATIONAL_EVIDENCE` and a scoped child remediation/upcall.
2. If the same failure class appears in two domains, cluster it.
   - Progress evidence: common failure cluster identifies affected domains and refs.
   - Failure risk: suspected common cause globally blocks every child.
   - Recovery: common diagnosis is promoted in scope only after evidence establishes the shared cause/invariant.

### S4 — UAOS looks for problems before the user reports one

1. Run freshness, inheritance-evidence and contradiction scans.
   - Progress evidence: concrete findings, not a generic “looks good”.
   - Failure risk: only known checks are exercised.
   - Recovery: material changes add scenario/recovery experiments; live evidence remains an explicit observation boundary.
2. Aggregate repeated causal histories.
   - Progress evidence: cross-domain failure classes become visible as candidates for common investment.
   - Failure risk: every one-off becomes a global rule.
   - Recovery: cluster is diagnosis evidence only; governed evolution still requires generalization/evaluation.

## Tradeoff and rejected designs

Rejected: a new central “supervisor queue” subsystem. It duplicates current scheduling/control authority and creates a new bottleneck.

Rejected: make every child copy the parent cognition implementation. This increases drift and confuses method ownership with business ownership.

Rejected: assume better architecture means no runtime problems. This is not supportable for probabilistic Agents and changing external environments; the target is lower defect incidence plus smaller blast radius, earlier detection, faster bounded recovery and stronger learning.

Selected: extend current binding/behavior assurance + health observation + existing non-conflicting scheduler + governed evolution. Complexity delta is one parent health policy/index and one small executable health module, with no new controller identity.

## Assurance boundary

Structurally verified by policy/contract tests and executable kernel tests.
Behavioral verification requires candidate CI and scenario tests.
Current child freshness observations are evidence as of the recorded commits only.
Live quality outcomes and unknown future failure modes remain observation scope and must not be reported as universally solved.
