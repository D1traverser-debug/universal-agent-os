# Domains

`src/uaos/domain_sdk/` is the reusable domain-package SDK. In-repository domain packages are migration artifacts only while a workflow is being brought under UAOS; they must not remain a second current business authority after that domain has cut over to its registered repository.

Current domain repositories and business-authority locations are defined by `config/SYSTEM_MAP.json` and `config/AGENT_REGISTRY.json`.

Financial Writing has completed external cutover to `D1traverser-debug/financial-writing-agent`. Its current workflow, policy, article state and delivery semantics live only in that registered domain repository; UAOS therefore carries no current `domains/financial_writing` business package.

Other domain-package retirement is handled only in the owning domain's maintenance scope; this Financial cleanup does not make claims about their current migration status.
