# 18 — UAOS 总控上层复核：从被动规则集到实际自主发现、双环学习与进化执行

**Authority:** UAOS controller existing task `state/tasks/uaos-inheritance-review-20261018.json`; original evolution `state/evolution/EVO-20261018-INHERITANCE-REVIEW.json`.  
**Scope/status:** `SOURCE_AND_HOST_ACTIVATION_STUDY__CANDIDATE_ARCHITECTURE_DECISION__NO_NATIVE_SEMANTIC_CONFORMANCE_PROOF`. Current parent baseline `main@6332bd6c6ffbaba7158b4a68bf0a6a734f51eba7`. The current user message is a goal/correction signal, *not* proof of the proposed cause or proposed architecture. This study is broader than the last incident's wording: examine general proactive discovery, real host execution, evidence-to-method transfer and outcome feedback. It is **not** an assertion of whole-repo or full-public-web saturation.

## 1. The observed systemic failure class, not one more prompt mistake

Over repeated selected-controller replies, the model chose easy local/procedural fixes: Progress formatting, recency-only knowledge inventory repair, later prohibiting child audits to address its *own* poor judgment, and source PR/CI pass claims without demonstrated native behavioral improvement. Earlier research [06], [08 taxonomy], [17] had already identified many of the same failure classes. Therefore a new single-line rule, longer Skill, extra postmortem or isolated negative prompt is **not an evidence-based sufficient remedy**.

**Governing outcome:** UAOS itself discovers unknown/latent problems (including failures in its own reasoning and assumptions), seeks independent professional methods, questions the architecture and method-selection rule, performs authorized improvements, verifies outcomes rather than proxies, retains/reuses/retracts knowledge, and resumes without the user serving as the diagnostic trigger. Normal child work is not cancelled to symbolically satisfy this goal.

### Current source-to-execution chain (read verified)

`Custom Instructions pointer` → account-installed `uaos-controller-runtime/SKILL.md` (version **unknown**) → ChatGPT model chooses to fetch `ENTRYPOINT.md/CURRENT_SYSTEM.json` and current state → conceptual `CognitionCase` / `DeepTask` / `KnowledgeAcquisitionAssessment` → Python `FinalizationContext/admit_final_response` **only if an independently controlled host actually invokes it** → `EvolutionTransaction` **only if entered** → PR/CI/main readback → post-release real behavior **not automatically observed**.

Source facts:
- `config/HOST_PROFILES.json#CHATGPT_GITHUB`: `native_runtime_skill_installation` is account UI manual; `semantic_signal_assurance` is behavioral and no verified pre-send hook; proactive triggers are configured schedule or opportunistic next invocation.
- `src/uaos/execution/openai_agents.py`: the controlled Agents SDK can attach `build_uaos_output_guardrail`, but that does **not** wrap this native ChatGPT conversation.
- `src/uaos/runtime/finalization.py` and `src/uaos/runtime/epistemic_entry.py`: when a controlled host supplies evidence they enforce real structural and source-origin invariants, but their docstrings explicitly exclude native physical mediation.
- `src/uaos/kernel/cognition_case.py#EngineeringTrace`: binds a non-empty goal string/evidence IDs to selected action ID and V&V text; this is not an independent semantic adjudication of action → actual complained-of capability.
- `config/EVOLUTION_POLICY.json#proactive_evolution`, `src/uaos/evolution/transaction.py`: first-class `CAPABILITY_GAP` and `EVALUATED_KNOWLEDGE` transaction exists; *availability of the transition code is not repeated invocation*.
- `src/uaos/evolution/opportunistic.py`: pure `assess_opportunistic_maintenance` decision, which cannot execute itself.
- `.github/workflows/domain-health-live-audit.yml`: a real six-hourly cron, but only audits child repository revision drift; **does not launch autonomous knowledge/reasoning improvement or corrective governance**.
- Connected ChatGPT automations private state *observed during this turn*: one pre-existing UAOS proactive audit task had `is_enabled=false`, `last_run_time=null`, meaning no scheduled executions were observable. The same existing task was updated **successfully to `is_enabled=true`** and its task instructions upgraded to research/counterexample/action/outcome lifecycle rather than warning-only monitoring; weekly cadence retained; **first successful run not yet observed**. This external user-owned state is NOT proven merely by a GitHub document; no personal task identifier is copied here.

### Independent problem-space factors

| Factor | Current disposition | Falsification or missing proof |
|---|---|---|
| Host execution activation discontinuity | **CONFIRMED** in inspected native/automation path: passive repo functions and disabled trigger; account Skill bytes unknown | Captured automatic host invocation of actual finalization and periodic work; first scheduled run+outcome |
| Local patch/test proxy mistaken for behavior | **OBSERVED** in repeated visible replies and lexical/progress tests | Version-pinned real multi-turn agent trajectories and independent success/outcome judgment |
| Historical learning not transferred on next novel problem | **OBSERVED EVIDENCE OF RECURRENCE**, exact causal split still open | Record retrieval of previous method + fit/misfit + successful application in unrelated held-out case |
| User framing / last assistant framing anchor | **OBSERVED** in repeated wrong conclusions, but not assumed universal | Hold-out with incorrect user theory where Agent independently disproves it |
| Oversized multi-policy/context load | **PLAUSIBLE**, not enough comparative evidence to declare sole cause | Version-controlled ablation of full/lean Skills at real host, measure semantic/latency/regression |
| No actual native output+tool identity trace | **CONFIRMED HOST EVIDENCE BOUNDARY** for current tools | Native pre-send hook/independent signed product trace becomes accessible |
| Underlying model inherently incapable of improvement | **NOT ESTABLISHED**; could not infer from these samples | Same-model host with correct bounded feedback/harness robustly outperforms base, or vice versa |

## 2. Independent method learning and fit/misfit

**A. Double-loop learning (Chris Argyris).** Primary `https://hbr.org/1977/09/double-loop-learning-in-organizations`; systematic review `https://onlinelibrary.wiley.com/doi/10.1111/emre.12615`. Single-loop alters an action under the same governing assumptions; double-loop questions the assumptions, goals and rules themselves. **Transfer:** when the Agent repeatedly patches a symptom, reopen the objective, judge, causal model, and whether current CI is an appropriate success criterion. **Limit:** asking more self-reflection questions without a mechanism that gets invoked and measures outcome reproduces ceremonial prose. Existing research [06] and [08] already discussed double-loop; novelty this turn is observing **real disabled trigger** rather than only recommending it.

**B. Reflexion (Shinn et al., `https://arxiv.org/abs/2303.11366`).** Feedback-driven linguistic reflection retained in episodic memory for later trials. **Transfer:** preserve specific failure *classes*, counterfactuals and when a method should NOT be reused; demand an actual later-use receipt. **Limit:** reflective text is not weight update, reliable truth or product-host execution; merely saving another research page is not learning success. Existing `KnowledgeItem` and Hindsight candidate [12] already own memory/provenance; do **not** deploy another competing memory store.

**C. Voyager (Wang et al., `https://arxiv.org/abs/2305.16291`).** Automatic curriculum + executable skill library + environment-error feedback + self-verification. **Transfer:** a proactive Agent must *select an uncovered next capability*, run a task in the environment, use outcome/error to refine, then store only verified reusable skill; evaluation should include transfer to a different problem. **Limit:** Minecraft's executable-world feedback and repeatable sandbox do not exist by default for opaque ChatGPT conversation semantics. Source documents remain candidates until transfer works in UAOS's real harness.

**D. Anthropic Agent Evals (`https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents`, 2026-01-09).** Distinguishes task, trial, grader, **entire trace**, observable **environment end state**, and harness; recommends balancing capability tests and regression tests, multiple trials and model/structural/human calibrated grading. **Transfer:** avoid a source-string benchmark that always says green; evaluate a new challenge not copied from the regression and record actual tool/action/results. **Limit:** adding a grader without a running host is still inert; self-model grading alone has bias and may need calibration.

**E. OpenAI Agent workflow evaluation (`https://developers.openai.com/api/docs/guides/agent-evals`).** Trace grading captures model/tool/guardrail/handoff path; datasets/eval runs compare prompt/orchestration variants. **Transfer:** when a fix changes routing, confirm the *new route* is used and improves outcome, not merely present in repo. **Limit:** native ChatGPT conversation is not automatically an Agents SDK trace.

**F. NIST AI RMF GOVERN/MAP/MEASURE/MANAGE (`https://airc.nist.gov/airmf-resources/airmf/5-sec-core/`).** Continuous, context-sensitive evaluation of risk and whether purpose was achieved, not a linear checklist. **Transfer:** quality assurance must question the goal/decision criteria, not just run another pass. **Limit:** process inventory is not measurable execution.

**G. Paperclip [15] and Hindsight [12] source studies already held by UAOS.** Paperclip's meaningful heartbeat binds actual issue checkout/run and result, not a scheduled message; Hindsight's recall/reflect with provenance/retraction matters only if fresh cases actually invoke and apply it. **Transfer:** distinguish heartbeat trigger, accountable work claim, action effect, recovery and knowledge promotion; avoid second task store, agent controller, or unproven usage links.

## 3. Architecture alternatives and tradeoffs

| Alternative | Strength | Failure / tradeoff | Decision now |
|---|---|---|---|
| Append more clauses to Custom Instructions and Skill | Low development cost | Existing source already lengthy; no proof of native invocation or better reasoning | REJECT as complete systemic repair |
| Add separate monitoring/supervisor/research database | Can add isolation and notifications | Duplicates ownership; no inherent action/effect or host authority | REJECT without executable independence proof |
| Keep only current reactive ChatGPT reply pattern | No overhead | Requires user to rediscover problems; repeatedly observed failures | REJECT as adequate proactive target |
| Rebuild all UAOS/children around new vendor framework | Potential new run environment | High migration/permissions/cost; no comparative proof all current kernels fail | NOT SELECTED without scope evidence |
| Reuse existing evolution/knowledge owners, **activate one real schedule**, pick novel coverage proactively, execute/falsify/observe; distinguish host-control ceiling | Actual enabled wakeup and opportunity to start work, no extra lifecycle; improves only scheduler activation now | Still does not intercept ordinary native replies and first run/outcome unknown | **SELECTED CURRENTLY EXECUTABLE BOUNDED STEP**, does not close systemic behavior assurance |
| Run same UAOS decision contract in a **controlled agent host** with trace, end-state and exact-response finalization binding | Stronger observable control and independent trials | Requires real host deployment, permissions/compute/provider cost and real handoff. May be outside current plan | **NEXT ARCHITECTURE OPTION TO EVALUATE**, not fake deployment |

**Architectural conclusion:** Failures arise primarily at the **control-loop actuation, observable outcomes, and learning-transfer boundary**, not from absence of a `CognitionCase` class or missing fifth instruction clause. A root-level redesign should concentrate on a genuine running host with trusted context/action/outcome feedback, if present or feasible; it need not discard proven authority, task, evolution, or knowledge components. Without actual host execution, changing more policy text is largely cosmetic.

## 4. Autonomous fault discovery is not just monitoring

The selected existing scheduler must perform a *work cycle*, not a scan: `choose next high-impact unknown → seek raw evidence/outside professional method → challenge governing rules and alternative causes → execute admitted safe next action → verify source AND environment/user outcome where accessible → reflect on second-order effects → retain/reuse/retire knowledge in original owners → choose next unknown`. Distinguish **immediate repair**, **latent capability discovery**, **independent unknown-unknown exploration**, and **no-change with falsification**. Only the first two/three sometimes mutate software.

Generalization targets intentionally NOT limited to the current user wording:
1. A fresh unprompted controller review discovers a historical risk missed by previous investigations; action and outcome are documented.
2. A newly encountered domain problem resembles a past failure but has a mismatched host/owner: retrieval must reject superficial analogy, test fit/misfit and independently choose.
3. A prior fix causes a different quality regression: the system discovers second-order effect and revises or rolls back earlier assumptions, without waiting for complaint.
4. A source project/version changes: trigger changed method/source re-evaluation and bound impact, not blanket adoption.
5. The user offers a false root theory: the model pursues evidence against its preferred/user theory and chooses a different action when justified.
6. A correct simple read-only turn must stay cheap; a proactive guard may not force verbose research/PRs everywhere.

Success metrics: % autonomous material findings *before* user prompts; independently reproduced false-positive/false-closure rate; observed end-state outcome score; % learned methods genuinely reused with effect; transfer pass rate on hidden cases; scenario pass^k across separate runs; cost/latency and unrelated-work regression. **All are NO BASELINE YET**, not invented scores.

## 5. Frozen ownership and what was actually done today

- **DONE / verified through host automation tool:** the existing UAOS proactive scheduled task (previously disabled/unrun) is now **enabled**, its prompt shifted from warning-only audit to actual research, challenge, bounded action, production reread and validated learning. The schedule remains weekly; it was not duplicated. A scheduling/activation acknowledgement is **not** evidence that a periodic run completed successfully.
- **DONE:** source/host audit distinguishing periodic six-hour child revision health cron from autonomous reasoning evolution; code owner roles and missing native interception recorded above.
- **DONE:** outside-in comparative learning across Reflexion/Voyager/Anthropic/OpenAI/NIST/Argyris and older UAOS Hindsight/Paperclip/architecture method notes; what transfers and what fails were documented with source links.
- **NOT DONE:** first autonomous scheduled run's raw transcript, verified actions, end-state result; native ChatGPT pre-send mediation; real held-out task performance improvement; comprehensive 405-file saturation; deployed independent model semantic grader or API runtime.
- **NEXT, without treating documentation as terminal:** observe the first actual scheduled run and whether it performs **authorized actions** rather than reporting; if it fails, diagnose run permission/context/tool activation and repair. Continue current-session review across evidence/host. Evaluate controlled-host adoption only if it improves actual reliability/cost/safety versus current native model; do not ask the user to repeat a diagnostic.

**Assurance boundary:** `LIVE_SCHEDULE_CONFIG_UPDATED__NEXT_RUN_NOT_VERIFIED__ARCHITECTURE_METHODS_STUDIED__NATIVE_SELF_EVOLUTION_NOT_CLOSED`.
