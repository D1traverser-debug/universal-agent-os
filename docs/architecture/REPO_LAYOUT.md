# Proposed New Repository Layout

```text
universal-agent-os/
├─ pyproject.toml
├─ README.md
├─ docker-compose.yml
├─ src/
│  └─ uaos/
│     ├─ contracts/              # typed cross-layer contracts only
│     ├─ kernel/
│     │  ├─ intent.py
│     │  ├─ requirements.py
│     │  ├─ planner.py
│     │  ├─ policy.py
│     │  └─ topology.py
│     ├─ runtime/
│     │  ├─ ports.py             # DurableRuntime interface
│     │  ├─ dbos_runtime.py
│     │  ├─ task_workflow.py
│     │  ├─ scheduler.py
│     │  ├─ supervisor.py
│     │  └─ replanner.py
│     ├─ execution/
│     │  ├─ registry.py
│     │  ├─ router.py
│     │  ├─ actions.py
│     │  ├─ approvals.py
│     │  └─ adapters/
│     │     ├─ openai_agents.py
│     │     ├─ mcp.py
│     │     ├─ http.py
│     │     ├─ script.py
│     │     └─ sandbox.py
│     ├─ state/
│     │  ├─ models.py
│     │  ├─ repositories.py
│     │  ├─ ledger.py
│     │  ├─ artifacts.py
│     │  └─ knowledge.py
│     ├─ assurance/
│     │  ├─ plans.py
│     │  ├─ validators.py
│     │  ├─ evaluators.py
│     │  ├─ coverage.py
│     │  └─ delivery.py
│     ├─ evolution/
│     │  ├─ incidents.py
│     │  ├─ failure_classes.py
│     │  ├─ proposals.py
│     │  ├─ promotion.py
│     │  └─ maintenance.py
│     ├─ domain_sdk/
│     │  ├─ manifest.py
│     │  └─ registration.py
│     └─ observability/
│        └─ telemetry.py
├─ domains/
│  ├─ financial_writing/
│  ├─ a_share/
│  ├─ video/
│  └─ novel/
├─ migrations/
├─ tests/
│  ├─ contracts/
│  ├─ scenarios/
│  ├─ fault_injection/
│  └─ domains/
├─ docs/
│  ├─ requirements/              # frozen v1.0 copied verbatim
│  ├─ architecture/
│  └─ adr/
└─ scripts/
```

## Layout rules

1. `contracts/` contains schemas, not business workflows.
2. `kernel/` cannot import domain packages.
3. `domains/` may import the domain SDK and public contracts, not internal state repository implementations.
4. all authoritative writes use state service/repository APIs.
5. no domain creates its own continuity, action journal, knowledge lifecycle or maintenance framework.
6. domain-specific rules live in that domain, not in global prompts.
7. new top-level folders require an ADR and a frozen requirement/risk mapping.
