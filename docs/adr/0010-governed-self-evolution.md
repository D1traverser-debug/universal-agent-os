# ADR-023 — Governed Self-Evolution and Maintenance

Status: ACCEPTED
Date: 2026-10-14

## Decision

UAOS self-evolution is not an Agent with permission to rewrite production. The governed lifecycle is:

`Incident → Failure Class → Change Proposal → Reproducible Evaluation → Promotion Authorization → Action Authority → Post-Promotion Observation → Keep / Rollback / Retire`.

Repeated failures are attached to a common failure class so recurrence is repaired at the correct abstraction layer rather than accumulating case-specific prompts. A proposal must identify why existing mechanisms cannot be reused, what it adds/replaces/retires, new failure modes, rollback, expected benefit, explicit evaluation scenarios and a complexity delta.

Promotion is fail-closed. The proposal must be in EVALUATED state; declared scenarios must be covered; all supplied evaluations must pass; regressions must be empty; and component/state/maintenance-cost budgets must remain within policy. Approval only authorizes the existing `execution.action_authority` path. It does not apply a production mutation by itself.

Proposal lifecycle transitions are mechanical: DRAFT cannot jump to PROMOTED, and a promoted mechanism can only proceed to observed operation, rollback or retirement through explicit transitions.

Idle maintenance requires a real scheduler/background capability and always yields to higher-priority foreground work. Diagnosis and proposal generation may run without production mutation. High-risk production maintenance requires explicit approval and still executes through the normal action/side-effect controls.

This implements I01–I10 and reinforces H03/H08/H09, X02/X03/X05/X08/X11/X13.
