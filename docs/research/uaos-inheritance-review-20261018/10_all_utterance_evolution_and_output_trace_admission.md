# 10. Controller all-utterance evolution triage and output trace (2026-10-18)

Owner: UAOS current `src/uaos/runtime/epistemic_entry.py` / `CognitionCase` / existing `EvolutionTransaction`. This is NOT a second memory/evolution OS or a new durable task store.
Status: **CANDIDATE** — controlled-runtime source/negative tests pending CI; native ChatGPT invocation **UNVERIFIED**.

## User directive and *observed failure*, before selecting a fix

The user explicitly requires that not only user complaints but **every user utterance and every assistant utterance** (and discovered tool/status evidence) enters the same evolution consideration process; an ordinary message may yield no durable change, but it cannot be unseen. The user's recurring criticism was that the controller's own final replies omitted the stipulated Progress while it worked on Progress rules, yet it neither detected nor corrected the omission until prompted again. The latest source-level defect is the absence of a mandatory **actual-output** assessment for each controlled controller turn, not merely a missing paragraph in a Skill.

Prior `src/uaos/runtime/epistemic_entry.py` classified host-supplied observations before response generation, and `src/uaos/observability/session_adherence.py` checked a set of ten fields (now optionally bound to actual task state under PR #117). Neither ensured that a controller's **outgoing words** were themselves analyzed for new claims/contradictions and routed to cognition/evolution. This is separate from the still-unverified native host invocation ceiling.

## Tested alternative hypotheses, not a single pre-decided root

- **Only a missing Progress field**: rejected as complete explanation. The repeated failure includes unaudited outgoing responses, unobserved user corrections and inaccurate transition from text green to real success; strict field formatting alone does not catch new output claims.
- **A new autonomous evolution agent and per-sentence evolution database**: rejected. It introduces competing authority and storage, and treating an ordinary request as a durable mutation would drown real changes.
- **Always append an additional 'I checked my answer' sentence**: rejected. Self-report is not an attested source/coverage trace.
- **Prior entry already covers everything**: falsified by code. Previous entry observations are sampled input evidence supplied by a caller; they do not bind the actual assistant draft or prove full observed utterance coverage.
- **Host-complete trace + typed coverage at existing controlled finalization seam**: selected bounded candidate. The host enumerates actual utterance references; the existing epistemic entry's EntrySignal vocabulary classifies each as no-material-gap, claim/challenge, contradiction, knowledge gap or unfinished work; current CognitionCase/Deep Task/EvolutionTransaction remains the *only* substantive deliberation/promotion owner.

## Independent method comparison and boundaries

| External method | Transferable concept | Concrete use here | Counterexample / limits |
|---|---|---|---|
| OpenAI Agents SDK tracing / guardrails: https://openai.github.io/openai-agents-python/tracing/ and https://openai.github.io/openai-agents-python/guardrails/ | Span-level input/output/tool and handoff observability; blocking guardrails on controlled paths | Host supplies enumerated user/assistant/tool/status refs and verifies submitted message content identity. Final response bytes are hashed against the very text admitted. | Native ChatGPT product messages are NOT automatically intercepted by Python repo. A declared source ref is not a complete host transcript. |
| LangGraph durable state/continuation: https://docs.langchain.com/oss/python/langgraph/persistence | Short-lived checkpoint vs shared long-term store are different; recovery must use exact owner | User/assistant wording remains trace evidence; durable knowledge/evolution promotion belongs only to existing owner, not one new file per utterance. | Persistence does not make classifications true, and a state snapshot is not actual host execution proof. |
| Google SRE postmortem culture: https://sre.google/resources/book-update/postmortem-culture/ | Repeated incidents demand cause/contribution, prevention and post-change observation | Every recurrence is an opportunity to challenge earlier claims and method adequacy, including output omissions while repairing output. | A one-off benign message need not trigger a full investigation or mutation. |
| NIST AI RMF Govern/Map/Measure/Manage: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ | Continuous risk assessment is cross-cutting and not a fixed ordered checklist | Assess each message's potential problem/capability gap, route only significant ones into canonical cognition/Deep Task/evolution. | It is not an implementation of ChatGPT internal native hooks. |

## Executable admission (bounded host-controlled path)

1. The *host*, not the assistant's summary, enumerates all observed message refs in the current turn: user, earlier assistant commentary if host exposed, tool/status reports and final assistant output. The assistant/runner attaches an `EntrySignal` assessment and evidence for each. A clean verdict needs a review source and no-gap/alternative reason; material verdicts need appropriate admission/routing evidence.
2. `admit_turn_evolution_coverage` compares the reviewed source set with the separately supplied host enumeration and requires an assessed **user** input and the exact **assistant** final output.
3. Outgoing final text SHA-256 must match the version actually reviewed; host must validate digests of non-final inputs and evidence links for each judgment and next evolutionary disposition. Missing/forged refs or mismatched draft -> fail closed.
4. When the reviewed output or observed tool/user trace discloses a source-supported contradiction or knowledge gap, current finalization cannot quietly report no issue or skip Deep Task; it routes to existing cognition/deep-task owners. No second evolution transaction created merely because a greeting was processed.
5. Every real material change still follows existing branch -> CI/independent review -> controlled promotion -> main reread -> outcome observation. Native complete mediation remains **NOT PROVEN** until product-host trace is actually available.

## Key assurance limits and next holdouts

- The controlled host must independently enumerate all utterance sources. If host or native UI never supplies messages, code cannot learn they were omitted. **Input completeness is conditional on genuine host mediation, not guaranteed by the dataclass.**
- Reference verification is an API from the host; tests with fixture lambda returning true demonstrate deterministic gate behavior only. They do NOT demonstrate independent qualitative cognitive judgment, internet knowledge saturation or user satisfaction.
- The system must not store full private conversation text in public GitHub artifacts; store minimised reference identifiers/digests or non-sensitive failure-class summaries with provenance. Hashes of short/private inputs also warrant careful access controls.
- Test replays: (a) omitted user/tool/assistant message; (b) contradictory false no-change; (c) assistant output changed after review; (d) fabricated source/digest/judgment ref; (e) benign utterance checked without demanding full evolution; (f) selected controller final response fails when no turn review exists; (g) native host without trace stays UNVERIFIED.
- After controlled repo gate passes, assess *actual* native-session tool and output events separately; review history after new recurrence rather than treating a once-green CI as a final result. Keep controller deep-review task RUNNING; preserve exact Financial Writing return task unchanged.
