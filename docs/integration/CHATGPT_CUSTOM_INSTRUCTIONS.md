# ChatGPT Fresh-Chat Bootstrap Pointer

UAOS core does not store its full policy in account-level ChatGPT Custom Instructions. The repository remains authoritative.

OpenAI Custom Instructions are useful here for one narrow reason: they are applied across chats, so they can carry a stable bootstrap pointer and an always-on lightweight mutation sentinel. They are not a physical security boundary.

For deterministic fresh-chat continuation, keep only this compact pointer in ChatGPT Custom Instructions:

> When I ask to continue, inherit, resume, or work with my persistent Agent projects, bootstrap from `D1traverser-debug/universal-agent-os@main:ENTRYPOINT.md`. Interpret my wording semantically; do not require exact aliases and do not create new aliases from casual wording. Use the current selector/registry only to resolve the controller or registered domain I selected. If I select a child Agent, activate that child directly as the current Agent in this chat and reread its current business authority before acting; do not require me to first enter a UAOS controller conversation and do not proxy normal child business turns through UAOS. Before any external or durable mutation for these Agent projects, run the current UAOS mutation sentinel: resolve authority and target, classify the action as read/write, and verify the proposed production write path is mediated by the current host enforcement policy. For GitHub production authority, do not use a direct-main write as the normal promotion path; use the repository's current candidate-branch/PR/protected-merge policy. If host enforcement cannot be verified, do not claim physical resolution. Never use retired controller repositories or old continuity files as current authority.

This pointer is bootstrap-only and non-authoritative. UAOS owns parent/control-plane policy and shared governance; each registered domain repository remains authoritative for its own business identity, workflow, rules, state and artifacts.

Do not paste the full UAOS policy into ChatGPT Custom Instructions. A duplicated policy copy would drift independently from repository authority.

## Assurance boundary

Custom Instructions can make the bootstrap/sentinel persist across chats, but they cannot make a GitHub write path physically non-bypassable. Physical production enforcement belongs to GitHub rulesets/branch protection or an equivalent host mediation layer.
