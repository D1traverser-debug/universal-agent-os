# ChatGPT Fresh-Chat Bootstrap Pointer

UAOS core does not store its policy in account-level ChatGPT Custom Instructions. The repository remains authoritative.

For an ordinary brand-new ChatGPT conversation, however, the model needs one stable bootstrap signal unless the host already injects `ENTRYPOINT.md`. To make fresh-chat continuation deterministic, keep only this pointer in ChatGPT Custom Instructions:

> When I ask to continue, inherit, resume, or work with my persistent Agent projects, bootstrap from `D1traverser-debug/universal-agent-os@main:ENTRYPOINT.md`. Interpret my wording semantically; do not require exact aliases and do not create new aliases from casual wording. Use the current selector/registry only to resolve the controller or registered domain I selected. If I select a child Agent, activate that child directly as the current Agent in this chat and reread its current business authority before acting; do not require me to first enter a UAOS controller conversation and do not proxy normal child business turns through UAOS. Never use retired controller repositories or old continuity files as current authority.

This pointer is bootstrap-only and non-authoritative. UAOS owns parent/control-plane policy and shared governance; each registered domain repository remains authoritative for its own business identity, workflow, rules, state and artifacts.

Do not paste the full UAOS policy into ChatGPT Custom Instructions. A duplicated policy copy would drift independently from repository authority.
