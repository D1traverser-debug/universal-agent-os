# Clean-Slate v10 — Frozen Requirements Delta v2.0

Status: `FROZEN_BASELINE_V2_0 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-15

v2.0 extends v1.0-v1.9 with explicit domain-internal work orchestration and child business-identity ownership.

## V20-01 — One Domain Agent may own multiple business workstreams and subtasks
A registered domain Agent may decompose one user/business objective into multiple workstreams, projects and subtasks without creating multiple UAOS child Agents merely because the work differs internally.

The domain repository owns those internal business identities, states, dependency graphs, artifacts and decision receipts. UAOS remains the cross-domain controller and must not mirror child project/program/workstream/subtask identities as parent task identities.

## V20-02 — Internal work relations are explicit
Domain-internal orchestration must be able to represent at least:
- serial dependency;
- independent parallel work;
- fan-out/fan-in synthesis;
- consultative advice;
- competitive candidates;
- structured critique and revision;
- authorized adjudication;
- panel/quorum review.

Unrelated unfinished work must not block a subtask whose declared dependencies and required inputs are satisfied.

## V20-03 — Competition and consultation do not erase ownership
Consultation creates advisory evidence only. Competition creates independently inspectable candidates against declared criteria. Neither transfers decision authority implicitly.

Selection, merge or rejection of competing candidates requires an authorized adjudicator/owner and a durable decision result before dependent work proceeds.

Same-model candidate diversity is useful exploration but is not independent semantic verification by itself.

## V20-04 — Negotiation is structured, not unbounded peer chat
When subtasks need to challenge, negotiate or reconcile, represent the interaction through bounded artifact rounds such as:

`proposal -> critique -> revision -> adjudication`

or

`candidate set -> independent reviews -> synthesis/selection`.

Do not create open-ended peer-chat loops with unclear termination, hidden authority transfer or non-reproducible state.

## V20-05 — Specialists exist for real contract differences
Create a distinct specialist only when the work materially differs in tools, policy, context, expertise, output contract or assurance boundary. Cosmetic role proliferation is forbidden.

A single domain owner remains responsible for user-facing synthesis unless an explicit domain handoff contract states otherwise.

## V20-06 — Business orchestration must preserve domain reliability contracts
Internal concurrency/competition must preserve:
- least-context execution;
- explicit artifact handoffs;
- dependency and provenance binding;
- producer/reviewer separation where required;
- fail-closed hard gates;
- stale-output invalidation when upstream inputs change;
- domain recovery and governed-evolution semantics.

## V20-07 — Parent routing identity and child business identities are distinct
UAOS may keep a domain router identity and, when useful, an opaque child business-state reference. It must not require equality between parent router/task IDs and child project/program/workstream IDs.

Exact historical child references remain child-domain business identities. Resuming one must not require parent adoption of that identity.

## Authority composition
Current requirements authority = v1.0 + v1.1 + v1.2 + v1.3 + v1.4 + v1.5 + v1.6 + v1.7 + v1.8 + v1.9 + this v2.0 delta.
