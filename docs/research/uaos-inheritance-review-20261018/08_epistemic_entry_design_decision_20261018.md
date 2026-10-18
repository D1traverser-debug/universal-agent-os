# UAOS single-entry epistemic architecture — evidence and decision, 2026-10-18

Scope: **UAOS controller only**. This is a comparison and change rationale for existing owners, not an extra governance lifecycle.

## Governing outcome vs. implementation proposals

Outcome: selected UAOS must independently question user claims, its own output, governing rules, learned methods and its initial causal diagnosis; seek other plausible factors; conduct sufficiently deep, multi-source learning when necessary; act, verify, inspect new issues and keep working without reminder. Only evidence can admit knowledge/mutation/evolution.

Candidates compared:
1. Add more MUST/NEVER exception rules: easier known-incident suppression, higher inconsistency and stale policy risk. REJECT as principal strategy. KEEP hard authorization/side-effect/version verification at technical boundaries.
2. All-source, all-repository and deep learning on every turn: can increase coverage but imposes context/cost/latency, repeats known material, may induce infinite regress and cannot measure inaccessible host behavior. REJECT as default; KEEP full audits when objective warrants.
3. One lightweight, evidence-sensitive entry feeding existing CognitionCase, Deep Task, KnowledgeAcquisitionAssessment, ActionCoordinator and EvolutionTransaction: ADOPT in bounded controlled UAOS path. It must treat the meta-rules and method choices themselves as candidates subject to challenge.
4. Complete host mediation in a controlled application/harness: materially stronger assurance but requires host ownership/traces. DEFER physical mediation of native ChatGPT.

## Distinct primary-source methods, challenged and adapted

- NIST reference monitor https://csrc.nist.gov/glossary/term/reference_monitor : complete mediation, tamper resistance, and compact verifiable boundary are three separate properties. Consequence: compiled prompt text alone is not evidence of physical mediation; test invocation when controlled.
- Chris Argyris double-loop learning https://hbr.org/1977/09/double-loop-learning-in-organizations : improvement must challenge governing variables, not merely error correction. Consequence: rule/assumption/method challenge is an *entry input*, not a new stage controller.
- CMU SEI ATAM https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method-2/ : compare modifiability, reliability, performance, complexity and security tradeoffs; "more instructions" may worsen modification cost while "always comprehensive" worsens latency.
- IBM MAPE-K autonomic computing https://research.ibm.com/publications/an-architectural-approach-to-autonomic-computing : sensors/analyzer/planner/effectors share knowledge. Consequence: without authentic observation and tool effect, a declarative feedback loop cannot claim autonomous learning.
- Google SRE postmortem culture https://sre.google/workbook/postmortem-culture/ : diagnose contributing factors, test recurrence and deliver measurable corrective actions rather than only explaining a discovered defect.
- OpenAI agent workflow evaluation https://developers.openai.com/api/docs/guides/agent-evals : traces and datasets test actual handoffs and tool use; deterministic unit tests are a different, narrower proof.

## Current source diagnosis (main at candidate branch)

- `config/SESSION_INTERACTION_POLICY.json` already has mandatory selected-context entry but previously listed six partly overlapping procedure lines. A user correction is not supposed to be the only trigger; a host failure may still bypass the policy.
- `config/DELIBERATION_POLICY.json` is the existing five-stage cognition authority.
- `src/uaos/kernel/problem_space.py` is the existing comprehensive knowledge-acquisition admission, with source roles, expansion, competing method families, contradiction and terminal saturation requirements.
- `src/uaos/runtime/finalization.py` already blocks remaining work in controlled mode, but did not require a source-backed *entry* from the selected UAOS controller to expose unmet research or rule contradictions before deciding a turn was clean.
- `src/uaos/runtime/native_session_profile.py` and the generated `skills/uaos-controller-runtime/SKILL.md` project behavior, not enforcement of native ChatGPT.
- Parent controller task remains RUNNING. This change does not execute any domain business task and should not be counted as full five-repo review.

## Implemented bounded intervention

- Condense entry's duplicate prose from six to four principled operations: recover provenance, challenge assumptions INCLUDING governing rules and learning methods, adaptively dispatch, act/verify/re-question.
- Existing cognition and evolution owners are untouched; no new ordered learning or cognition lifecycle.
- Add a small typed `ControllerEpistemicEntry` and a pure `assess_controller_epistemic_entry` adapter. Source-backed fact observations are distinct from user/assistant causal suggestions. A benign selected turn remains lightweight.
- In the existing `admit_final_response` controlled path **only when UAOS controller selection is asserted by the trusted host**, require entry evidence, verify its references through host-supplied source verifier and route fact-backed contradiction to CognitionCase, knowledge gap to Deep Task, and unfinished authorized action to existing continuation guard.
- Regression against actual failure classes: root-cause mirroring, no-user-correction contradiction, shallow knowledge, unperformed remaining work, fabricated evidence, and benign simple turn.
- If host cannot provide current evidence or call the finalization API, do not claim native complete mediation or source-verification independence. Reuse exact controller task for the remaining native study.

## Unresolved factors and saturation boundary

Competing causes remain: controller host invocation, incorrect semantic classification by model, stale source observations, over-broad or overly shallow research, repeated prompt-local patches, repair side effects, and post-promotion behavioral feedback. The new entry API addresses **controlled routing**, not all those factors.
Search rounds revisited NIST, Argyris, SEI, IBM, Google SRE and OpenAI workflow evaluation. They yielded a bounded, cross-family method comparison, not an exhaustive web traversal or two terminal zero-novelty saturation rounds. Consequently comprehensive study remains OPEN and no genuine native trace reliability percentage is asserted.

Acceptance for this patch: exact generated projections, candidate+production CI green, controlled negative and positive route tests, task/evolution continuity, no child repo edits, and truthful host assurance boundary. Subsequent direct native observations remain a separate task.
