# Universal Agent OS

UAOS is the sole active cross-domain control plane for durable autonomous work.

Start with:
- `ENTRYPOINT.md` — runtime/bootstrap semantics;
- `CURRENT_SYSTEM.json` — machine-readable current authority;
- `config/SYSTEM_MAP.json` — exact locations/ownership map;
- `AGENTS.md` — repository operating rules.

## One controller, domain-owned business truth

UAOS owns task identity, requirements, cross-chat continuation, planning/action lineage, capability orchestration, retrieval admission and governed system evolution. Registered business repositories own domain rules and fine-grained business state/artifacts.

Current domains: Financial Writing, A-share, Novel, Video.

Every domain uses one current binding layout:
- `UAOS_SKILL.md`
- `.uaos/MANIFEST.json`
- `.uaos/ADAPTER.json`
- `.uaos/CAPABILITIES.json`

No current domain control binding lives under a `continuity/` namespace.

## Anti-pollution / anti-drift

- `config/RETRIEVAL_POLICY.json` rejects retired/superseded controller surfaces from normal retrieval.
- `config/BINDING_POLICY.json` fails closed if a domain Skill/manifest/adapter/capability binding drifts.
- `config/SYSTEM_MAP.json` is the current location map; search ranking is never authority.
- controller state lives under `state/tasks/`; domain business truth stays in each domain's declared business-state location.
- retired migration executables/importers are not part of the current tree.

The retired `D1traverser-debug/universal-continuity-agent` default branch is a tombstone redirect only. Historical Git commits may be inspected explicitly for forensics but are never runtime/recovery authority.

## ChatGPT Custom Instructions

Account-level Custom Instructions are optional and non-authoritative. UAOS does not require them. If used, keep only the stable pointer in `docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md`; do not duplicate system policy into account text.

## Hosts

The same controller semantics run through `CHATGPT_GITHUB` or `LOCAL` persistence adapters in `config/HOST_PROFILES.json`.

## Authority

- Requirements: `docs/requirements/FROZEN_REQUIREMENTS_v1.0.md`, `docs/requirements/FROZEN_REQUIREMENTS_v1.1.md`
- Architecture: `docs/architecture/ARCHITECTURE_BLUEPRINT_v1.1.md`
- Readiness: `docs/assurance/PRODUCTION_READINESS.json`
