# ADR-020 — Domain SDK and Financial Writing Pilot

Status: ACCEPTED
Date: 2026-10-14

## Decision

Business domains plug into UAOS through a small Domain SDK. A domain may declare business capabilities, workflow templates, knowledge namespaces, required tools and eval suites, but it may not redefine shared infrastructure such as continuity, action authority, knowledge lifecycle, maintenance or completion assurance.

Only `NEW_TASK` creates a domain workflow. `CONTINUE`, requirement changes and system maintenance remain control-plane operations so a domain cannot accidentally fork task identity or continuity semantics.

The first pilot is financial writing. We migrate confirmed business invariants from the legacy owner — current-source research, research audit, editorial planning, headline work, dual broad/deep drafting, finance-compliance review, Word delivery and visible-deliverable verification — while discarding legacy continuity, lease, owner-guard and GitHub-state machinery.

The pilot deliberately changes one legacy ordering: actual Word documents are rendered before mechanical/final audit, so the completion gate can verify the exact deliverables that will be given to the user. This satisfies G08/J03 rather than preserving an old runtime sequence for compatibility.

The pilot remains a workflow/contract pilot, not a production cutover. Legacy style rules that have not yet been mapped to explicit requirements/evals remain evidence in the old repository and are not silently imported.
