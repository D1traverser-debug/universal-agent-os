# Multi-causal autonomy and cumulative learning: comparative study, 2026-10-18

Status: **IN_PROGRESS — NOT SATURATED — NOT COMPLETE SYSTEM REVIEW**.
Authority: evidence input to existing UAOS CognitionCase / Deep Task / EvolutionTransaction; NOT a new SOP/control plane.

## Research question, competing premises

Goal: make selected controller work independently search for latent failures and methods, compare competing systemic causes, perform authorized corrective action, verify effects and derived requirements, and resume without user intervention.
Premise P1 "the last requirement-impact gap is the root cause" is unproven; P2 "browse/read every file and web page once, then all future evolutions are matched" is falsified as a general guarantee by unknown runtime side effects, uninstrumented host behavior and novel requirements.
P3 "CI proves an executable controller guard exists" holds only **when invoked**. Green Python tests do not establish native ChatGPT interception.

## Independent module: systems-engineering and requirements trace

Primary NASA requirements management https://www.nasa.gov/reference/6-2-requirements-management/ .
Core: bidirectional source/derived-requirement/design/verification traces; configuration changes assess cost, schedules, design, interfaces, upper/lower requirements; design-derived needs require source justification and independent checking.
UAOS: RequirementRecord lifecycle, Plan.transitive_dependents, TopologyRegistry.impact_closure and Financial owner requirement transactions exist, but no tested requirement semantic root-selection bridge is proved. Preserve owner boundary and recover UNKNOWN unmapped edges. An impact graph must not automatically treat every downstream change as a durable evolution.
Test: a requirement change with two plausible work roots must require independently supported selection, not a supplied root string.

## Independent module: systems-theoretic causal analysis

MIT CAST/STPA primary https://psas.scripts.mit.edu/home/books-and-handbooks/ and CAST handbook https://psas.scripts.mit.edu/home/get_file4.php?name=CAST_Handbook.pdf .
Core: resist root-cause seduction and hindsight bias; analyze interacting control conditions and process contexts, not only the nearest repairable defect. CAST is a system safety incident method, not evidence that a single Agent can infer all software causes.
UAOS: treat factors as potentially co-present: native host invocation boundary; task continuity/next-action loss; inadequate knowledge-acquisition admission; mistaken requirement root mapping; evidence self-attestation; missing post-promotion real outcome; authority/mutation gating; time/context/tool failures.
Test: "repair requirement map" may leave missing host trace, false completion, stale state. Validate factors separately; one success never disproves all others.

## Independent module: architecture tradeoffs and continuous review

CMU SEI ATAM https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/ .
SEI 2023 holistic architectural analysis https://sei.cmu.edu/library/a-holistic-view-of-architecture-definition-evolution-and-analysis/ .
Core: stakeholder scenarios, quality-attribute tradeoffs, sensitivity/risk themes; ongoing architecture analysis is a post-release concern and requires practical automation.
UAOS: judge reliability, autonomy, cost, latency, recoverability, owner preservation, adaptability against scenarios, not line count or green repo CI. Deep full-repo review at each *explicit controller selection* trades user work latency for wider discovery; use progressive cumulative evidence, not blind rereading of untouched files as a proxy. Do not turn an architectural preference into "verified root."
Test: a local fix passing CI while it increases host false-completion, owner collisions or unmeasured performance fails broader acceptance.

## Independent module: management, risk and learning cycle

NIST AI RMF Core https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ and Playbook https://airc.nist.gov/airmf-resources/playbook/ .
Core: GOVERN/MAP/MEASURE/MANAGE is continuous, contextual, multi-disciplinary; Playbook is NOT a fixed exhaustive recipe. Not measuring a risk should be documented, not scored zero.
ASQ PDCA https://asq.org/quality-resources/pdca-cycle : plan, run, check, act/standardize, then repeat; experiments distinguish policy candidates from accepted operations.
UAOS: explicit owner, risk, measured result, unknowns, selected action/no-change, rollback, post-observation. The current Task Index and EvolutionTransaction supply ownership and lifecycle; adapt them instead of a competing manager.
Test: require handoff/status after a green PR, and keep unmet business outcomes OPEN instead of closing maintenance.

## Independent module: operations, monitoring, incident response

Google SRE postmortem analysis https://sre.google/workbook/postmortem-analysis/ documents both triggers and multiple *contributing* root-cause categories; systemic patterns become durable improvements, not isolated blame.
Google SRE monitoring https://sre.google/sre-book/monitoring-distributed-systems/ separates user-impact signals from diagnostic measures.
UAOS: native session entry, tool selections, evolution stage, duration, root hypotheses, changed files, user-visible result and post-action effects need distinct evidence; lack of host telemetry is not success. PR CI is one narrow service signal.
Test: a green repository gate with no native trigger or user-facing outcome must remain UNKNOWN / OPEN.

## Independent module: autonomic computing and feedback control

IBM Research original architecture https://research.ibm.com/publications/an-architectural-approach-to-autonomic-computing and IBM Redbooks Autonomic Management Engine https://www.redbooks.ibm.com/redbooks/pdfs/sg246665.pdf (section 6.1.1).
Core: a self-managing resource must have real sensors and effectors; Monitor, Analyze, Plan, Execute share Knowledge (MAPE-K). A declarative loop without measurable sensor events or executable effector actions is not self-management.
UAOS: map control-surface sensors (repo revision, native turn trace if accessible, child runtime/outcome, task completion, failure recurrence), analyze with existing cognition, plan via current task/authority, execute via current mutation admission, update knowledge/evolution after an observed effect. The missing actual native ChatGPT sensor/effector mediation remains UNKNOWN/UNSUPPORTED even when repository-side tools work.
Test: a healthy `main` CI while controller review was not invoked in a native turn means MAPE-K Monitor coverage failed; repository tests cannot silently repair the missing host wiring.
Adoption: ADAPT as an external *architecture diagnostic lens*, not a second persistent MAPE controller, nor proof of real autonomy.

## Independent module: agent workflow evaluation

OpenAI agent workflow evaluation https://developers.openai.com/api/docs/guides/agent-evals .
Core: use traces (model/tool/guardrail/handoff sequence), graders, datasets, repeated eval runs; assess workflow rather than final-text promise. SDK traces apply to instrumented agent runtimes; cannot be inferred for native ChatGPT without product telemetry.
UAOS: real transcript failures are negative examples, deterministic replay is parser/checker evidence, independent fresh session executions and action-state effects are separate outcome assurance.
Test: injected "user says root cause X" and "assistant previously claimed done" must not be accepted as causal proof; recurring no-reminder action sequence needs actual trace/outcome holdouts.

## Method family comparison and explicit selection

| Method family | Solves | Does not solve | UAOS disposition |
|---|---|---|---|
| NASA trace | Known requirement/derived needs and affected work evidence | Unknown host event, semantic correctness solely by graph | REUSE existing requirement/plan/topology owner; add typed evidence-bound impact **if** evaluation justifies |
| MIT CAST/STPA | Multi-factor discovery and anti-single-root bias | Full live run telemetry, implementation enforcement | ADAPT CognitionCase causal factor and independent falsification |
| SEI ATAM/holistic | Quality-attribute risk/tradeoff and architecture redesign scope | Continuous tool-driven execution by itself | ADAPT existing ArchitectureExperienceCase |
| NIST AI RMF + PDCA | Governance, risk, adaptive improvement and follow-up | Mandatory "entire web" scan or native hook | ADAPT current task/evolution owner |
| Google SRE | User-impact observability, contributory causes, corrective action follow-up | Invisible native tool traces | REUSE domain-health/observation and explicit unknowns |
| OpenAI workflow eval | Trace-based independent behavioral comparison and regression | Prove uninstrumented ChatGPT always ran Skill | REUSE finalization/holdouts, require actual native observations for native claim |
| IBM MAPE-K | Sensor/analyzer/planner/effector/shared-knowledge feedback | Supply missing native sensor/effector permissions | ADAPT as missing-instrumentation lens, not a second loop owner |
| More instructions alone | Immediate textual salience | Physical mediation, root cause and real outcome | REJECT as sole remedy |
| Full scrape every turn | Potentially broader inventory | Completeness, pertinence, hidden unknowns, latency | REJECT as sole mechanism; retain indexed scope + evidence-driven deepening |
| New Research OS / Evolution OS | Can centralize brand-new operations | Duplicates existing canonical owners, new shadow authority | REJECT by default |

## Actual acquisition trace and saturation

Rounds: (1) primary source seed (NASA, SEI, NIST, SRE, MIT, OpenAI); (2) cross-family expansion to systems-theoretic CAST, holistic architecture, incident contributing causes, agent workflow traces and NIST limits; (3) source-specific challenge against current UAOS controller/finalization code and *new* IBM MAPE-K autonomic control family.
**The second and third rounds added material method families/failure modes. Saturation has NOT been demonstrated**, and no automated claim of "searched the entire web" or comprehensive-knowledge admission is made.
Missing next independent passes: double-loop learning/organizational incentive constraints, fault-tree and fault-injection counterfactual designs, diverse review of semantic root selection, and at least two real negative/positive native controller-inheritance traces; distinguish inaccessible host signals from search failure.

## Synthesis — one evidence-driven chain, not one universal fix

TRIGGER (explicit UAOS selection or continuing current unresolved controller task) -> RECOVER exact main/task/version -> INVENTORY registered owners and unmet goals -> MULTI-FACTOR discovery and falsification -> ACQUIRE independent relevant methods with source-role coverage -> MAP known and derived requirements/impacts -> SELECT no-change/local/systemic architecture actions -> EXECUTE owner-admitted actions -> VERIFY both technical and observed outcome -> REDISCOVER potential new failure after action -> UPDATE existing Task Index and canonical EvolutionTransaction as appropriate -> REPEAT until verified end or real external blocker.

Use an *existing* admission path: `src/uaos/kernel/problem_space.py#require_knowledge_acquisition_admission` for comprehensive research, `src/uaos/assurance/controller_review.py` for controller review, CognitionCase for causal judgment, EvolutionTransaction for durable promotion. Keep native ChatGPT host enforcement limitations explicitly open.

Current operational result: material gaps identified, not all learned knowledge is admissible yet; explicit stop reason for this document is checkpoint/continuation, **not knowledge saturation**.
