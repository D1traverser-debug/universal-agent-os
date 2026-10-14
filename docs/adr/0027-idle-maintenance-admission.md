# ADR-027 — Idle Maintenance Requires Authority-Derived Admission

Status: ACCEPTED
Date: 2026-10-14

## Decision

A timer firing is not proof that the system is idle. IDLE maintenance may run only after the scheduler evaluates the current authoritative runnable set and active resource claims. Any foreground runnable work or resource conflict denies admission. The resulting boolean is then consumed by the maintenance policy; a language model cannot self-declare the system idle.

UAOS does not encode "background" by choosing a magic low numeric priority. Its local scheduler and DBOS queues use different priority conventions, and maintenance safety should not depend on accidental numeric mapping. DBOS provides persistence, schedule triggering and a queue with concurrency one; the UAOS kernel provides admission semantics.

The live schedule probe creates a real DBOS schedule after launch, binds it to a durable queue, manually triggers it, verifies a workflow event, deletes the schedule and verifies cleanup. This is intermediate evidence. R7 closes only when the production maintenance workflow obtains and enforces real idle-admission evidence while foreground work is present/absent in live tests.
