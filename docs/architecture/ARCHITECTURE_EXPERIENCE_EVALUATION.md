# Architecture Experience Evaluation

Status: CANDIDATE
Authority: UAOS

## Why this exists

UAOS already has a structural architecture: control kernel, durable runtime, execution fabric, state/artifact/knowledge, assurance/recovery, evolution/maintenance and observability. It also has task lifecycle and domain ownership rules.

That is necessary but insufficient. A system can be structurally coherent and still be hard for the acting Agent to understand or operate correctly in sequence. The architecture therefore must be evaluated as something an Agent actually inhabits and uses, not only as a diagram or inventory of components.

This method complements, rather than replaces, the structural blueprint.

## Governing rule

Architecture is evaluated from stakeholder/Agent concerns and concrete scenarios. Representations are selected because they expose the concern, not because one notation is universally preferred.

A user-provided mechanism or analogy is not automatically a requirement. First separate:

- governing goal/outcome;
- explicit constraint or locked requirement;
- example/analogy;
- observation of a failure;
- hypothesis about a cause or solution.

Only the first two are binding without further promotion. The others are evidence or candidate inputs.

## Four complementary questions

For every material architecture change, ask:

1. STRUCTURE — what owns what, what depends on what, and where does authority/state live?
2. TIME — what happens first/next, what can interleave, where can interruption occur, and how is recovery performed?
3. COGNITION/OPERABILITY — can the current Agent discover the correct goal, authority, next action and progress evidence at each step without reconstructing hidden context?
4. CAUSAL/TRADEOFF — why does this mechanism improve the governing outcome, what does it worsen, and what competing design could falsify the choice?

These are concerns, not mandatory diagram types. Use only the representations needed to answer them with evidence.

## Scenario portfolio

Select the smallest portfolio that covers material risks. Candidate classes include:

- primary success path;
- failure and recovery;
- resume after interruption;
- user correction or requirement change;
- cross-domain handoff when applicable;
- maintenance/evolution when applicable;
- current-Agent dogfood for control-plane or Agent-experience changes.

A scenario must name its governing outcome and starting authority/state.

Each step records:

- acting role;
- intended action;
- evidence that progress occurred;
- plausible confusion or failure;
- recovery or next evidence.

## Current-Agent dogfood

When UAOS itself is being changed, the evaluating Agent must walk through representative work as CURRENT_AGENT.

Examples of questions:

- If a user gives a goal plus an illustrative mechanism, do I preserve the goal and test the mechanism, or literalize the example?
- Can I locate current authority without relying on chat memory?
- Before a material mutation, is the valid order of operations discoverable?
- If a mutation fails, can I distinguish a harmless rejected request from a production defect?
- After a child system evolves, what tells me whether parent observation is stale?
- When CI is green, what architectural risks can still remain outside the test suite?
- After interruption, can I resume from evidence rather than reconstructing an assumed sequence?

## Representation selection

Use concern-driven views. Examples:

- authority/context/component/dependency views for structural ownership and coupling;
- sequence/state/event/lifecycle/timeline views for ordering, handoff and recovery;
- cognitive walkthrough/task journey for Agent operability and learnability;
- causal graph/decision table/tradeoff matrix/quality-attribute scenario for selection rationale.

Do not force all views on all changes. Do not claim a static view proves a temporal property or that a sequence proves ownership boundaries.

## Candidate comparison

A preferred architecture is not selected merely because it is familiar, already implemented, or was mentioned by the user. Compare viable candidates against the governing scenario outcomes and relevant quality attributes, such as:

- correctness;
- comprehensibility;
- operability;
- recoverability;
- evolvability;
- friction/cost;
- assurance strength;
- failure containment.

Tradeoffs must remain visible. A stronger control is not automatically a better product if it materially damages normal operation without a corresponding requirement.

## Promotion boundary

A material architecture candidate is promotable only when:

- governing goals and explicit requirements are separated from examples/hypotheses;
- material concerns have scenario coverage;
- concern-appropriate representations exist;
- current-Agent dogfood exists when the change affects Agent/control-plane use;
- walkthrough steps expose progress, failure/confusion and recovery evidence;
- structural contracts and scenario behavior do not contradict each other;
- candidate comparison and rejected alternatives are evidenced at a depth proportional to risk;
- reproducible tests/fitness checks cover mechanizable invariants.

The executable admission is `src/uaos/kernel/architecture_experience.py`.
