# Management and continuous improvement study

Sources: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ ; https://asq.org/quality-resources/pdca-cycle ; https://dora.dev/capabilities/learning-culture/ .

NIST AI RMF separates GOVERN, MAP, MEASURE, MANAGE; these are context-sensitive and not a universal checklist. ASQ PDCA plans a change, tests it, checks evidence, and standardizes or revises. DORA associates a learning culture with software delivery improvements, not with guaranteed LLM compliance.

Independent synthesis: a controller review must record objective, owner, active risk, accepted evidence, unmeasured gaps, action disposition, and post-change observation. A green repository CI is a technical outcome, not proof of user-facing business quality. Competing designs: accumulate more prompt rules (rejected); rely exclusively on CI (rejected); require evidence-bound management closure using existing UAOS task and evolution owners (selected).

Current-system counterexample: PR #91 was merged and CI green while its observation still claimed candidate pending. This was repaired by PR #92, but shows why independent management closure is required.
