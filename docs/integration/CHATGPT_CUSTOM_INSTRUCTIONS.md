# ChatGPT Fresh-Chat Bootstrap Pointer

UAOS core does not store its policy in account-level ChatGPT Custom Instructions. The repository remains authoritative.

For an ordinary brand-new ChatGPT conversation, however, the model needs one stable bootstrap signal unless the host already injects `ENTRYPOINT.md`. To make fresh-chat continuation deterministic, keep only this pointer in ChatGPT Custom Instructions:

> When I ask to continue, inherit, resume, or work with my persistent Agent projects, first bootstrap from `D1traverser-debug/universal-agent-os@main:ENTRYPOINT.md`. Interpret my wording semantically; do not require exact aliases and do not create new aliases from casual wording. Resolve the current task through UAOS, then reread the selected domain's current business authority before acting. Never use retired controller repositories or old continuity files as current authority.

This pointer is bootstrap-only and non-authoritative. All task, routing, retrieval, approval, recovery and domain policy remains in UAOS.

Do not paste the full UAOS policy into ChatGPT Custom Instructions. A duplicated policy copy would drift independently from repository authority.
