# Universal Agent OS

UAOS is the active cross-domain control plane for durable autonomous work.

Start with:
- `ENTRYPOINT.md` — runtime/bootstrap semantics;
- `CURRENT_SYSTEM.json` — machine-readable current authority;
- `AGENTS.md` — repository operating rules.

## One controller, domain-owned business truth

UAOS owns task identity, requirements, cross-chat continuation, planning/action lineage, capability orchestration, retrieval admission and system evolution. Registered business repositories own their domain rules and fine-grained business state/artifacts.

Current domains: Financial Writing, A-share, Novel, Video.

## Anti-pollution / anti-drift

- `config/RETRIEVAL_POLICY.json` blocks retired/superseded continuity surfaces from normal retrieval.
- `config/BINDING_POLICY.json` fails closed when a domain Skill/manifest/adapter no longer binds to UAOS.
- historical cutover material lives only under `docs/migration/` and is excluded from bootstrap.
- controller state lives under `state/tasks/`; domain business state remains domain-local.

## Hosts

The same controller semantics run through `CHATGPT_GITHUB` or `LOCAL` persistence adapters in `config/HOST_PROFILES.json`.

## Authority

- Requirements: `docs/requirements/FROZEN_REQUIREMENTS_v1.0.md`, `docs/requirements/FROZEN_REQUIREMENTS_v1.1.md`
- Architecture: `docs/architecture/ARCHITECTURE_BLUEPRINT_v1.1.md`
- Readiness: `docs/assurance/PRODUCTION_READINESS.json`
