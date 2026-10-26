# 19 | 2026-10-26 — Retrieval-path identity at the authority boundary

**Owner:** existing UAOS controller task `uaos:maintenance:inheritance-review-20261018` and `EVO-20261018-INHERITANCE-REVIEW`. **Knowledge status:** CANDIDATE; the source-level mechanism is verified, but native host reachability, exploitability and method transfer remain UNVERIFIED.

## Governing outcome and proactive selection

A source retrieval decision must apply current owner policy to the **same repository-relative resource identity** later handed to a connector. A plausible source reference is not permission to retrieve it. This protects fresh continuation, domain binding and historical/retired-source isolation without building another controller or knowledge store.

The active task is still RUNNING. Recent PRs #163–#166 added a structurally strong but semantically incomplete full-dimension source-study gate; #165 intentionally preserves an xfailed semantic irrelevance case. Those changes do not establish native ChatGPT interception. In a separate, proactive source-code inspection, `RetrievalPolicy.authorize` used `path.lstrip("/")` and matched `deny_patterns` against the raw remaining string. `build_source_read_plan.add` independently blocked literal dot segments, but other callers of the public policy API had no equivalent validation.

**Source-level reproduction:** video domain policy denies `continuity/**`, yet `fnmatch("projects/../continuity/tasks/retired.json", "continuity/**")` is false; `authorize` returned allowed for that ambiguous string. Novel `migration/**` and A-share `config/cutover_status.json` are sibling negative paths. This is a policy admission bypass, **not** evidence that GitHub/ChatGPT actually fetched a denied file: the known read-plan caller already blocked literal traversal, and connector URL normalization is unverified.

## Competing explanations and falsification

- **H1: caller-level guard is sufficient.** Supported for `build_source_read_plan.add` with literal `.`/`..`; falsified as a *policy-wide* guarantee by direct `RetrievalPolicy.authorize` call. If all production fetches were conclusively mediated by that guarded caller, real exposure would be narrower; no such native complete-mediation evidence exists.
- **H2: transport canonicalization is the primary cause.** Unverified: a GitHub connector might normalize, reject or encode a path differently. Even a transport rejection would not make `authorize` semantically correct. This requires a real authorized connector trace to assess impact; do not probe inaccessible files or claim exfiltration.
- **H3: authorization is incorrectly applied before path identity is fixed.** Supported directly by `lstrip("/")`, raw `fnmatch`, and a standalone counterexample. The caller's duplicate validation is evidence of fragmented ownership. Other downstream file, URL and symlink boundaries are separate and must not be inferred secure from this fix.

## Alternatives and decision

| Candidate | Fit | Counterexample / cost |
|---|---|---|
| NO_CHANGE | Preserves current read-plan behavior | Public policy API can still allow a noncanonical denied path; a new caller can bypass the one existing guard. |
| LOCAL_PATCH_IN_READ_PLAN | Cheap and already partially present | Cannot cover direct policy users; repeated logic drifts. |
| **CANONICAL_VALIDATE_AT_RETRIEVAL_POLICY** | One existing owner rejects ambiguous relative identities before deny/allow matching; read-plan uses the same helper | Strict path spelling can reject legitimate percent-escaped or platform-specific names; explicit historical intent still needs its separate policy gate. |
| NEW_PROXY_OR_REWRITE | Could mediate every host fetch in a controlled deployment | Unjustified second routing/control layer; cannot physically intercept native ChatGPT merely by adding repository code. |

**Selected smallest complete intervention:** add a pure `_validated_repo_relative_path` helper in existing `src/uaos/integrations/retrieval.py`, use it from both `authorize` and `build_source_read_plan.add`. Reject absolute, drive-like, dot, empty-interior, backslash, control-character and percent-escape ambiguous spellings. Do not silently normalize or decode: canonicalization after an allow/deny decision changes the resource identity. Preserve valid child business paths and explicitly authorized historical reads. No extra controller, evaluator, state machine, API purchase or child mutation.

## Professional source-method learning

- **MITRE CWE-22** (https://cwe.mitre.org/data/definitions/22.html): path equivalence and canonicalization can invalidate prefix/allowlist assumptions; validate a consistent representation before policy comparison. Applicability: source-path admission. Counterexample: a valid normalized string does not prove absence of symlink, connector or authorization-layer problems.
- **NIST AI RMF 1.0 Core** (https://airc.nist.gov/airmf-resources/airmf/5-sec-core/): govern/map/measure/manage are context-dependent outcomes, explicitly not a checkbox sequence. Applicability: evaluate the retrieval failure class across owner boundaries and deployment conditions; not a reason to add six ritual stages.
- **Anthropic, Demystifying evals for AI agents (2026-01-09)** (https://www.anthropic.com/research/demystifying-evals-for-ai-agents): distinguish trajectory from environment outcome; grade task success and read real state, not only green checks or a final claim. Applicability: tests can prove this policy function rejects bad inputs; only observed host fetch behavior could prove end-to-end protection.
- **OpenAI Agents SDK tracing** (https://openai.github.io/openai-agents-js/guides/tracing/): controlled SDK tool spans expose actual calls, but tracing is runtime-specific; it is not evidence that a native ChatGPT Skill ran.

**Transfer rule (candidate):** whenever a policy decides authority over a named resource, bind admission and execution to the same normalized identity, and test direct API + every sibling caller + negative/positive outcome. **Nonfit:** semantic method relevance, model reasoning quality and native host invocation cannot be solved by string validation. Do not promote this to universal knowledge until an independent different resource-policy task reproduces the benefit.

## Frozen acceptance and observations

1. Direct policy denies all noncanonical paths across four child owners, including attempts to route through an allowed prefix to a denied retired path.
2. Existing read-plan safety and valid current paths remain functional; explicit historical read of a canonical denied path still works when authorized.
3. Full existing `promotion-gate` passes on candidate, merge uses the protected PR route, and `main` source is reread.
4. Claim is bounded to controlled repository policy. **OPEN:** native ChatGPT/Skill invocation, connector normalization, real-world denied fetch prevention, independent transfer, semantic six-axis study validity, and the Financial business outcome.

**Rollback:** revert the isolated helper/read-plan call-site change via PR if a legitimate GitHub path is rejected or an owner workflow regresses. Preserve this case as a candidate until real-host and holdout evidence exists.

## 2026-10-26 production observation (bounded)

- Candidate PR: https://github.com/D1traverser-debug/universal-agent-os/pull/167 ; head `a84ed0cdc507f2674f85e4be2fcb5858355a18d5`.
- Actual GitHub Actions promotion-gate: https://github.com/D1traverser-debug/universal-agent-os/actions/runs/40253842057 ; job `121351324605`, **693 passed, 2 skipped, 1 xfailed**, success. The xfailed case is the previously known six-axis semantic-irrelevance holdout, **not** a successful semantic judge.
- Merged production commit: `fed3a9f4fe82963b509977915b8dcda59fad7a27`. Reread on `main` confirmed the policy helper, direct-policy regression tests, current task, existing Evolution record and this research document.
- Verified improvement: direct controlled retrieval policy no longer admits ambiguous repository-relative path identities through the tested variants, and existing regression suite remains green. This does not certify native ChatGPT tool interception, downstream URL handling, security against untested encodings, or cross-task method generalization. The current controller task remains RUNNING.
