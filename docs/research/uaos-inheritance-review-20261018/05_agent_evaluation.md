# Agent evaluation and behavioral conformance study

Primary references:
- https://platform.openai.com/docs/guides/evals
- https://platform.openai.com/docs/guides/trace-grading
- https://opentelemetry.io/docs/concepts/observability-primer/
- UAOS: src/uaos/runtime/finalization.py ; src/uaos/observability/session_adherence.py ; tests/architecture/test_native_cognition_progress_live_replay.py.

Independent method:
1. Separate native session triggering from repository gate correctness.
2. Test exact observed failures with replay + a synthetic positive control for test sensitivity.
3. Run near-miss negative controls, changed task, abandoned action, and alternate causal/repair proposals.
4. Preserve expected behavior, observed behavior, exact authority/version, trace provenance, and confidence.
5. Require credible business outcomes and post-promotion observations in addition to green code tests.

Cross-examination: #92 recorded one genuine missing-progress example. Its test passed because it detected the failure; that does not mean the actual assistant was compliant. A CI gate is only trustworthy inside a controlled host that invokes it. Native ChatGPT tool traces/Skill activation are not directly observable with the current GitHub connector; classify this as UNKNOWN, not SUCCESS.

Candidates: claim native 100% from CI (reject); rely on user reminders (reject); version-pinned independent replay and accessible observational evidence with explicit host gap (select).

Method outputs should be linked into a knowledge acquisition assessment and, when an actual reusable change exists, passed through one canonical EvolutionTransaction. No second governance lifecycle.
