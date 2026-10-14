# Clean-Slate v4 — 冻结需求规格 v1.2

Status: `FROZEN_BASELINE_V1_2 / REQUIREMENTS_AUTHORITY`
Date: 2026-10-14
Updated-at: 2026-10-14T08:21:28Z

v1.2 does not rewrite v1.0 or v1.1. It incorporates every requirement in those versions unchanged and adds the following explicit user requirements. Where these interaction/observability/common-capability requirements refine earlier continuation or subsystem rules, this v1.2 delta takes precedence.

## V12-01 — Bare inheritance selector
When the user sends a generic inheritance/continue request such as “继承” and no exact task or domain is semantically resolved, UAOS must not silently choose a business task. It must present a current selectable inheritance surface containing:
1. the UAOS controller (“总控系统”); and
2. current `resume_eligible` tasks/projects from `state/TASK_INDEX.json`, with status/stage and explicit-only/HOLD distinctions visible.

The selector must be derived from current authority at invocation time. Selecting an item must not create or mutate task aliases.

## V12-02 — Progress report in inherited conversations
After a controller or durable task/project has been selected for the current conversation, every final assistant response in that inherited conversation must end with a compact current-Agent progress report.

The report must include, when applicable:
- current Agent/controller;
- current task/project or maintenance scope;
- lifecycle status;
- current stage;
- next action or blocker;
- governing version identity;
- progress/freshness timestamp.

Unknown or unverified fields must be labelled as such; they must not be guessed.

## V12-03 — Version and timestamp provenance
Material controller, task and domain authority used for continuation or system maintenance must expose a stable version identity (release/version/schema/hash as appropriate) and an ISO-8601 update timestamp or equivalent authoritative commit timestamp.

User-visible progress reporting must distinguish:
- **authority/progress timestamp** — when the governing state actually changed; and
- **response time** — when the chat response was produced.

Schema version alone must not be presented as the system release version.

## V12-04 — Common capability inheritance
Every Agent registered by UAOS must inherit UAOS common capabilities without copying a second control plane into the domain repository. Common capabilities include:
- intent and requirement governance;
- cross-chat continuity/recovery;
- capability handshake and graceful degradation;
- assurance/evidence/completion governance;
- governed self-evolution;
- inherited-session progress reporting;
- version/timestamp provenance.

Business rules, business data, project state, domain-specific evaluation and domain artifacts remain owned by the domain repository.

## V12-05 — Governed self-evolution inheritance
UAOS governed self-evolution is a shared governance capability, not an unrestricted self-rewriter.

Domain systems may and should generate incidents, failure classes, learning candidates, alternative comparisons, evaluations/replays and owner-scoped change proposals. Durable production promotion must still pass the unique owning authority:
- common/cross-domain mechanism changes are promoted through UAOS;
- domain-specific business-rule changes are promoted by the domain owner under UAOS requirement/action lineage;
- candidates never become production authority merely because a domain learning stage produced them.

The shared lifecycle remains:

`Incident → Failure Class → Change Proposal → Reproducible Evaluation → Promotion Authorization → Action Authority → Post-Promotion Observation → Keep / Rollback / Retire`

## Authority composition
Current requirements authority = `FROZEN_REQUIREMENTS_v1.0.md` + `FROZEN_REQUIREMENTS_v1.1.md` + this v1.2 delta.
