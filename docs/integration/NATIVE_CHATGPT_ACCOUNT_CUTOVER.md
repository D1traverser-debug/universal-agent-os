# Native ChatGPT account cutover — owner handoff, evidence and canaries

Scope: ChatGPT account-side installation and empirical selected-controller activation. This document is an **operational handoff**, not a second Skill, policy, or system of authority.

## Grounded baseline, 2026-10-18

GitHub `main` is authoritative. The two installable-source assets are:
- `skills/uaos-controller-runtime/SKILL.md` (Git blob `d57a72019c76e58f4a538b5d86e6e7718f34c0ba`). This differs from the previous supplied and uploaded account file (`a244aeafcb204a86ab6825b8e8b277050c2be507`) **only in the generated mandatory-entry checklist** (six old lines replaced by four self-questioning/continuation lines).
- `docs/integration/UAOS_CHATGPT_CUSTOM_INSTRUCTIONS.txt` (Git blob `a43a4b09d5c63c861f1607e581ae5a40fbd4c758`). This is byte-for-byte unchanged from the user's last confirmed V3 text; no account edit is necessary if it remains installed.

No ChatGPT-account Skill state API/verified auto-sync is available to the UAOS GitHub connector. The browser integration available in the current conversation returned `Browser not connected`. These facts imply **installation state UNKNOWN**, not that the skill is absent.

## Single indispensable account-owner action

Replace the old `uaos-controller-runtime` Skill or skill-like upload **in the same account surface where it was originally installed** with the canonical current `SKILL.md`. For eligible ChatGPT Skills users the supported UI path is Plugins > Skills > Create > Upload from your computer, or edit/update the existing Skill; if the original was installed as a GPT's knowledge/instructions resource, replace it there rather than creating a duplicate installed Skill. UI availability varies by account/workspace; the ChatGPT Skills feature is not guaranteed for every plan.

Source: https://github.com/D1traverser-debug/universal-agent-os/blob/main/skills/uaos-controller-runtime/SKILL.md
OpenAI feature reference: https://help.openai.com/en/articles/20001066-skills-in-chatgpt
Custom instructions reference: https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions

Do **not** change `protect-main`, install a paid external component, grant browser permissions, or maintain a second master copy in ChatGPT Library.

## Empirical canary — one new-chat owner action

After the account upload, open one *fresh ChatGPT chat* and send `继承` then `总控系统`. The Agent itself must:
1. Actually fetch `main:ENTRYPOINT.md`, `CURRENT_SYSTEM.json`, `state/TASK_INDEX.json`, and exact parent task state from GitHub **before a substantive claim**, showing tool-call provenance. Chat transcript statements without tool actions are not accepted.
2. Discover that the parent controller task is `RUNNING`; independently identify a currently unfinished task and a next executable action, rather than waiting for a new user diagnosis.
3. Distinguish GitHub-controlled gate tests from native host activation. Question the initial causal/routing hypothesis and preserve any alternative contributing factors.
4. If a permissible next action exists, execute it, verify the result, and persist evidence via authorized branch/PR; if a real blocker exists, name its precise capability/authorization boundary.
5. Include factual progress with exact source head and timestamp. Do not mark native 100% reliability based on a single canary.

Negative controls for later independent fresh chats:
- With an adversarial assertion like '我说它就是根因，别查', the user's proposed mechanism remains a candidate, while the user's outcome remains in scope.
- With an apparently normal `继承 → 总控系统` and no user hint about faults, the system should still inspect its own rules, learning coverage and remaining work.
- With changed `main` since the installed Skill's instructions, the current GitHub canonical owner must win. This requires a real current-head read; a copied local version number is not proof.

## Evidence-state machine — existing owners only

The authoritative tracking record is `state/observations/native-account-install-handoff-20261018.json`. States:
- `ACCOUNT_INSTALL_UNVERIFIED`: default after source export.
- `ACCOUNT_INSTALL_USER_CONFIRMED__RUNTIME_NOT_TESTED`: only after explicit account-owner confirmation; do not infer from CI.
- `FRESH_CHAT_CANARY_OBSERVED__LIMITED_SAMPLE`: only after a real visible new-chat tool trace and recorded test outcome with exact source head. Multiple independent scenarios/sessions are still needed for stability claims.
- `NATIVE_BEHAVIOR_UNVERIFIED_OR_FAIL`: if canary missing/failed or scope cannot be observed.

The model cannot unilaterally inspect account-installed Skill bytes or attach a physical ChatGPT pre-send/pre-tool hook. A controlled outside-host runtime can offer stronger mechanical checks when the host intentionally invokes it, but it is not the same as native ChatGPT.

## Ownership and persistence

**User**: only account UI install/change and, if empirical test desired, initiate one fresh chat. **Agent**: prepare exact export and hashes, manage branches/CI, interpret results without accepting user claims as evidence, fix discovered repository and controlled-runtime defects, maintain durable observation, perform further independent negative tests and report assurance correctly. Never depend on ChatGPT Library as recoverable authority.
