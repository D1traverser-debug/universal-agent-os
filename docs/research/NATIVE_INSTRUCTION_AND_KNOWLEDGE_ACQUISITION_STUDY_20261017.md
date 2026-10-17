# Native Instruction + Knowledge Acquisition Study — 2026-10-17

Status: `EVIDENCE_ONLY__NON_AUTHORITATIVE`

Purpose: evaluate how UAOS should learn unfamiliar methods/frameworks, write native ChatGPT/Skill instructions, route reasoning depth, and convert evaluated knowledge into durable capability without creating a second cognition/evolution system.

## Governing questions

1. Should native UAOS entry be symptom-triggered, or should every selected-context turn enter a cheap router before any depth decision?
2. What belongs in Custom Instructions, Skill metadata, Skill body, references/scripts, canonical policy, executable gates, regressions and holdouts?
3. When should instructions be positive/invariant-oriented versus negative/prohibitive?
4. How should broad learning/search avoid both known-keyword tunnel vision and impossible literal “search the whole web” claims?
5. How should broad learning stop, validate, and enter governed evolution?

## Source-role map

### A — current/primary platform and implementation authority
- OpenAI Developers: Skills concepts / building skills / prompt engineering / model guidance / Goals in Codex.
- OpenAI `openai/skills` repository, including current skill-creator and curated Skill examples.
- Agent Skills open specification, especially description optimization and progressive disclosure.
- Current UAOS production authority and executable code.

### B — independent research / benchmark / systematic evidence
- SkillsBench (2026): curated Skills improve some agent tasks materially, but benefit is heterogeneous; self-generated Skills are not automatically beneficial; focused Skills can outperform comprehensive documents.
- SWE-Skills-Bench (2026 preprint): many public SWE Skills do not improve pass rate and can add token overhead; specialized fit matters.
- “Lost in the Middle” and multi-constraint instruction-following work: placement/context load and constraint count/order can affect following performance.
- LLM self-correction surveys: same-model self-critique is not a reliable independent judge; external/tool feedback is materially stronger.
- Adaptive-reasoning/routing work: no single reasoning style dominates all task classes; allocate depth by task/evidence rather than running heavy reasoning uniformly.

### C — professional search/review methods
- PRISMA-S: document information sources, search strategies, citation searching and supplementary methods for reproducibility.
- Cochrane searching guidance: searching is iterative; citation search can assess completeness; stopping should be reasoned and documented.
- TARCiS: backward/forward citation searching is useful for hard-to-search topics.
- Information-retrieval query-expansion literature: initial vocabulary is often incomplete; discovered terms should reformulate subsequent searches.
- Evidence triangulation: seek complementary sources with different failure modes rather than counting repeated claims from one evidence family.

### D — implementation/discovery samples
- OpenAI/Anthropic real Skill repositories and examples.
- GitHub repositories/issues/PRs as implementation and failure evidence.
- Skill catalogs/indexes (for discovery only, not quality authority).

### E — community/emerging-signal sources
- X, Reddit, Hacker News, blogs and creator discussions: useful for finding emerging methods, failure modes and vocabulary, but not sufficient by themselves for durable causal or policy claims.

## Knowledge modules learned independently

### M1 — Entry versus escalation

Finding: a host/model cannot reliably use “unknown knowledge”, “complexity”, “architecture”, or “systemic failure” as *pre-entry* conditions because detecting those conditions is itself part of the cognition task. This creates a circular dependency.

Better abstraction: after a UAOS/domain context is selected, every substantive turn enters a cheap mandatory routing/sentinel step. The sentinel then decides whether ordinary execution, contrastive cognition, structured cognition, Deep Task, broad knowledge acquisition, evolution or mutation admission is required.

Boundary: mandatory entry does **not** mean mandatory heavy deliberation. The cheap router must preserve fast simple-task execution.

### M2 — Skill discovery metadata

Finding: Skill name/description are discovery/routing metadata. They should describe the user goal/scope and when the Skill should load. Detailed workflow belongs in the body or referenced resources.

Failure mode: symptom-list descriptions (“correction, failure, repeated failure, contradiction, uncertainty, knowledge gap...”) try to encode the problem ontology in metadata, increase context/false-trigger risk, and duplicate canonical policy.

Implication: because UAOS Custom Instructions can explicitly hand off to the runtime Skill after mandatory entry, the Skill description can be concise and scope-based rather than an exhaustive trigger dictionary.

### M3 — Instruction language and degrees of freedom

Finding: one language style is not optimal everywhere.
- High-freedom principle/heuristic instructions suit contextual judgment where multiple valid approaches exist.
- Medium-freedom templates/pseudocode suit preferred patterns with bounded variation.
- Low-freedom scripts/gates suit fragile, error-prone or consistency-critical operations.

Positive invariant should usually define the desired state/action loop. Hard negative `MUST NOT/NEVER` language is appropriate at genuine cliffs or non-bypassable boundaries, not as the default representation of every past incident.

Example abstraction repair:
- symptom-level: “never use `next` as workflow clock”
- governing invariant: while the admitted objective remains unfinished and no genuine user-input/authorization/safety/budget blocker exists, select the next evidence-supported action, execute it, verify it, and reassess completion/stop conditions.
- regression case: a no-information `next/continue` message must not be required merely to advance already-authorized work.

### M4 — Epistemics and anti-anchoring

Finding: “question everything” is too broad. It can cause pointless skepticism of explicit requirements and verified facts.

Better invariant: causal explanations, solution proposals, framework choices and action recommendations do not gain authority from who said them — user, current model, prior assistant, expert, popular repository or existing code. They remain claims/candidates until evidence appropriate to risk supports them. User-defined outcomes, preferences and constraints remain requirement authority within their valid scope.

External research should supply independent facts/methods/counterexamples; same-model self-dialogue is candidate generation, not independent verification.

### M5 — Research / learning acquisition loop

Literal “search the whole web” is not a verifiable completion condition. The useful interpretation is coverage-oriented acquisition:

1. define governing question/outcome and knowledge modules;
2. model the source landscape and required evidence roles;
3. seed multiple independent queries/lenses, not one known keyword;
4. use source-native browsing/repository traversal where relevant;
5. expand/reformulate queries from newly discovered vocabulary;
6. follow backward/forward citations or equivalent reference/implementation links when they can expose missing families;
7. extract claims, mechanisms, assumptions, limitations and failure modes;
8. cluster findings into method/mechanism families instead of counting duplicate pages;
9. seek contradictions/counterexamples and triangulate across source families with different failure modes;
10. stop on documented saturation, not fatigue;
11. validate the integrated method on holdout/replay/realistic use;
12. if system behavior should change, enter the existing `EvolutionTransaction` as `EVALUATED_KNOWLEDGE` or `CAPABILITY_GAP`.

### M6 — Search stopping / saturation

A broad acquisition should not stop merely after N searches. A reasonable bounded stop contract is:
- required source roles for the task are covered;
- material contradictions are resolved or explicitly bounded;
- the candidate method/solution space contains competing families and known failure modes;
- successive expansion/snowball passes produce no material new method family, failure mode, constraint or evidence that would change the current decision;
- further search has low expected value relative to risk/cost;
- the stop reason is recorded.

This is a saturation criterion, not a claim of literal exhaustive-web coverage.

### M7 — Evaluation and holdout

Skill/prompt changes should be versioned and evaluated as application behavior, not accepted because prose “looks better”. Trigger metadata needs positive, indirect and near-miss negative examples. Behavioral changes need realistic holdouts, including examples not used to tune the wording.

For the user’s included/free-first constraint, repo-native deterministic tests + GitHub CI/live tests + real fresh ChatGPT holdouts are preferred. Do not introduce paid API/model-eval dependency merely to score instruction variants.

### M8 — Control surface versus prose

Prose should not simulate enforcement that belongs at a physical chokepoint. GitHub rulesets/status checks can mechanically guard production writes; native ChatGPT currently lacks a repository-controlled pre-send/pre-tool hook. The Skill/Custom Instructions improve behavioral routing but must not claim complete mediation.

## Candidate architecture comparison

### A — Keep v2 and add more examples/rules
Rejected as insufficient. It preserves symptom-driven language and risks turning incident history into a growing prompt.

### B — Add a separate “Research OS / Research Skill”
Rejected as default. Current UAOS already owns cognition, Deep Task, outside-in discovery and Evolution. A new parallel lifecycle would duplicate authority unless an evidence-backed boundary proves existing owners cannot carry the behavior.

### C — Extend existing cognition/Deep Task/problem-space owners + redesign native entry language
Selected for candidate implementation.
- Mandatory lightweight entry after context selection.
- Internal adaptive routing; complexity/unknown/systemic signals are escalation inputs, not entry gates.
- Coverage-oriented knowledge-acquisition receipt extends `problem_space.py`; it does not create a second cognition state machine.
- Deep Task can require the receipt when broad method/framework/unknown-knowledge acquisition is material.
- Native Custom Instructions become a compact mandatory-entry pointer + autonomous goal loop.
- Runtime Skill becomes a concise dispatcher to canonical owners; incident-specific phrases move to eval/regression fixtures.

### D — Move all native interaction into a controlled wrapper/API runtime
Deferred. It can offer stronger mechanical interception, but conflicts with the included/free-first baseline and is not required to test the admitted language/research capability gap.

## Candidate source-of-truth allocation

- Custom Instructions: mandatory native entry pointer + minimal authority/bootstrap/autonomous-loop semantics.
- Skill description: scope/discovery only.
- Skill body: dispatcher/decision workflow and pointers, not duplicate policy encyclopedia.
- `DELIBERATION_POLICY`: canonical cognition/search semantics.
- `DEEP_TASK_EXECUTION_PROFILE`: evidence-depth requirements.
- `problem_space.py`: executable broad-discovery / knowledge-acquisition receipt.
- Evolution: durable proposal/evaluation/promotion/observation.
- Tests/evals: incident phrases, near-miss triggers, no-op continuation, user-remedy anchoring, under/over-trigger cases.
- GitHub ruleset/CI: production mutation enforcement.

## Holdout families required before promotion

1. selected-context trivial factual/read-only turn — mandatory entry, no heavy escalation;
2. routine authorized execution — continue autonomously without ceremonial research;
3. user proposes a root cause + repair and says “just do it” — keep repair candidate until admitted;
4. user independently requires a mechanism regardless of diagnosis — preserve requirement authority;
5. unknown method/framework choice — broad acquisition/search escalation;
6. explicit “learn this comprehensively” — module decomposition + source map + saturation/holdout;
7. narrow known lookup — do not force comprehensive research;
8. systemic/repeated failure — structured cognition + failure-class coverage;
9. no-information continuation prompt — should not be required to advance already-authorized work;
10. near-miss non-UAOS chat — no accidental controller takeover.

## Boundaries

- This document is evidence, not policy authority.
- Search coverage is not literal web exhaustiveness.
- A source’s prestige/popularity is not current-system causal proof.
- Community/catalog sources are discovery inputs unless independently verified.
- No claim is made that native ChatGPT always executes repository cognition physically; fresh-chat holdout remains necessary.
