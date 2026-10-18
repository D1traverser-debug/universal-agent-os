# 15 — Paperclip 多 Agent 控制面、治理与执行闭环：源码级研究、独立反证和 UAOS 迁移

**研究对象**：`paperclipai/paperclip`（用户指定外部来源第 **4/4** 项）。权威上游默认分支 **master**，冻结 SHA **27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1**，提交时间 2026-10-18T19:16:13Z。权威所属：UAOS controller，状态真相 `state/tasks/uaos-inheritance-review-20261018.json`，不以本文替代任务索引或任何 child domain 的真实进度。
**地位**：**SOURCE-STUDY / KNOWLEDGE-CANDIDATE / NO PAPERCLIP DEPLOYMENT / NO NATIVE UAOS QUALIFICATION / HOLDOUTS UNEXECUTED**。外部源的“公司”“CEO”“董事会”“权限”“预算”“心跳”是 Paperclip 自有模型，并非经自动授权可重构 UAOS 的 parent/child authority。

## 1. 研究覆盖、事实边界和评估路线

Paperclip 是具有 Node.js/TypeScript 服务端、React UI、PostgreSQL/Drizzle、适配器/Runner、技能库、CLI、审批/预算/审计、测试与文档的**实际开源多 Agent 产品**，而不是一个只包含 `SKILL.md` 的单技能。它称自己是 Agent 团队的 control plane：公司目标、代理层级、issue/task、运行 heartbeat、状态/成本和授权都存储在它的持久服务。和纯对话型代理不同，若未实际运行其 server/DB/runner，浏览 Skill 文件不会获得其事务级仲裁能力。

该上游冻结树 **11,672 个条目、未截断**，主要存量位于 `packages/`（3329 条）、`ui/`（2709）、`server/`（2511）、`tests/`（590）、`doc/`（510）、`scripts/`（284）、`cli/`（179）、`docs/`（135）、`.agents/`（92）、`skills/`（32）和 GitHub CI/集成。来源级深审采取**按功能/权威/攻击与故障面分层取样**：官方架构与 Skill 全文入口，工作流/审计策略，服务器关键门禁和预算事务，适配器运行资源生命周期，代表性负向测试，源内明确的待验资格快照及独立外部工程文献。**不是逐行审阅 11,672 个文件，也未运行 Paperclip 测试、安装服务、真实 Agent 执行或外部网络探测。**不能把源仓自身的成百上千测试文件存在误写成“我们跑了测试”。

### 1.1 多角色冻结来源矩阵

| 角色 | 源码/资料 | 此次证据要点 |
| --- | --- | --- |
| 产品立场、依赖、概念和许可证 | [README](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/README.md)；[Architecture](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/start/architecture.md)；[Core Concepts](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/start/core-concepts.md)；[LICENSE](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/LICENSE) | 公司/目标/任务/Agent、服务/数据库/客户端/适配器职责；产品自述不等于宿主验证 |
| 管理授权与分派 | [Delegation](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/guides/board-operator/delegation.md)；[Approvals](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/guides/board-operator/approvals.md)；[Agent management](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/guides/board-operator/managing-agents.md) | CEO 规划→董事会批准→分解→下属执行→跟进，以及 board 的暂停/终止权限 |
| Agent 运行/恢复合同 | [Heartbeat protocol](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/guides/agent-developer/heartbeat-protocol.md)；[Agent runtime](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/agents-runtime.md)；[Core Paperclip Skill](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/skills/paperclip/SKILL.md) | Agent 身份/领取任务、运行 ID/审计、过程结果和持久恢复；警惕文档与正在快速迭代实现的版本差异 |
| 心跳编排与状态 | [queue.ts](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/heartbeat/queue.ts)；[recovery.ts](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/heartbeat/recovery.ts)；[run-lifecycle.ts](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/heartbeat/run-lifecycle.ts)；[run-completion.ts](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/heartbeat/run-completion.ts) | wake coalescing、DB admission/recovery、unknown/liveness、终结与重复防护；非单个 in-memory lock |
| 真审批 stage/请求人 | [Execution policy guide](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/guides/execution-policy.md)；[issue-execution-policy.ts](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/issue-execution-policy.ts)；[approval-records.ts](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/lib/approval-records.ts) | 真实状态转换干预、revision/review/approval、原子决策注释、审批重复幂等 |
| 执行隔离边界 | [execution allowlist](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/execution-allowlist.ts)；[bootstrap](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/execution-policy-bootstrap.ts)；[run permissions](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/packages/adapter-utils/src/paperclip-runner-permissions.ts) | Kubernetes only/managed-sandbox-only 与默认允许选本地的差别；UX permission 非物理隔离 |
| 公司/代理身份和跨租户 | [agent-identity.ts](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/agent-identity.ts)；[agent-run authentication](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/middleware/agent-run-authentication.ts)；[authorization-context tests](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/__tests__/authorization-run-context.test.ts) | 公司键、run 归属和持久 scope、密钥校验，不允许低信任运行跨域提升 |
| 预算与成本 | [Budget guide](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/guides/board-operator/costs-and-budgets.md)；[budget reservations](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/budget-reservations.ts)；[accounting tx](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/accounting-transaction.ts)；[budgets.ts](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/budgets.ts) | 预算预留、会计公司锁、未结算实例的占用、阈值停机与不可控外部费用 |
| 适配器单次尝试生命周期 | [ACPX coordinator](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/packages/adapter-utils/src/acpx-engine/run-coordinator.ts)；[resource ledger](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/packages/adapter-utils/src/acpx-engine/run-resource-ledger.ts)；[fault matrix tests](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/packages/adapter-utils/src/acpx-engine/run-fault-matrix.test.ts) | startup / turn / settlement / reproduction，资源一次结算、错误清理和 transfer/finalize |
| 技能供应链与知识 | [Skills store](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/docs/guides/agent-developer/skills-store.md)；[core skill](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/skills/paperclip/SKILL.md) | catalog→company library、来源冻结、`trustLevel` 由文件推断、更新/漂移/脚本风险 |
| Conformance 和反例 | [106-case contract](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/packages/paperclip-runner/docs/capability-eval-conformance.md)；[semantic vectors](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/packages/paperclip-runner/src/conformance/capability-semantic-conformance.ts)；[lifecycle authority tests](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/tests/lifecycle-baseline/authority.test.ts) | 106 条/16 组**源文档称**离线 mock 契约；拒绝表面叙述假进度与错误权限升级 |
| 代表性持久库负测 | [approval idempotency](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/__tests__/approval-routes-idempotency.test.ts)；[queued claim isolation](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/__tests__/heartbeat-queued-run-claim-isolation.test.ts)；[lease terminalization](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/__tests__/heartbeat-run-lease-release-terminalization.test.ts)；[budgets service](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/__tests__/budgets-service.test.ts)；[execution allowlist tests](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/server/src/services/execution-allowlist.test.ts) | 真实代码中含 cross-company、recovery、budget、拒绝重复、run 终结等正反用例；不是运行回执 |
| 自身资格与边界反例 | [rich ACP qualification checkpoint](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/doc/architecture/runner-rich-acp-qualification-2026-09-29.json)；[SECURITY policy](https://github.com/paperclipai/paperclip/blob/27709a99b1a2d3f1e58ab77d5a0e6b48d4626bc1/SECURITY.md) | 上游留存资格状态 `pending` 与费用未知不可视为 0；生产资格不因 README 徽章成立 |
| 独立行业方法对照 | [Temporal Activity 官方文档](https://docs.temporal.io/activities)；[Temporal retry/idempotency](https://github.com/temporalio/documentation/blob/main/docs/encyclopedia/activities/activity-definition.mdx)；[OPA authorization](https://www.openpolicyagent.org/docs)；[NIST AI RMF](https://airc.nist.gov/) | 外部系统 retry 的至多/至少一次副作用语义、PDP/PEP 分离、治理与可测风险，避免以同一产品自证合理性 |

### 1.2 学习充分性与仍开放的事实

已覆盖源码角色：产品层、公司归属、权限身份、分派/心跳、并发 claim、预算交易、生命周期资源结算、独立 stage 审查、执行 sandbox 配置、Skill 供应链、负向测试和未过资格；跨方法参照 Temporal 的 durable Activity（重试可重复副作用）、OPA 的授权判定/执行分离、NIST AI RMF 对效果/风险可测要求。**广度为主要职责面覆盖，深度为关键机制源与测试代码审查；非全仓饱和。**
开放：Paperclip 当前部署的真实配置、安全沙箱 OS enforcement、所有 adapter 的真实权限、数据库隔离下的竞争结果、106-case 测试是否在此 master 的真实 CI 上无条件通过、实际用户的组织结果、成本与退出动作是否符合预期、UAOS 原生 GPT host 是否有同等入口。项目内 `runner-rich-acp-qualification-2026-09-29.json` 把那一专项明确标 `pending`，且 `modelReceiptPolicy` 不将未知成本算作 0；**不能把任何单次报告“源码存在”推断为当下已通过全部生产资格**。

## 2. 六层真实系统与两个不能混淆的“Agent OS”

1. **组织/目标层**：Company 是顶层租户，Goals/Projects/Issues 关联业务方向，CEO/Manager/Report 属组织树；人类 operator 审批部分战略/用人决策。目标连续性来自 database 和 board 规则，不来自 Agent 记住使命。
2. **任务与人层**：Issue status/assignee/parent/goal/互动文档/附件为可恢复协同事实。Checkout 是原子任务所有权转移；`409` 是竞争冲突，不能强行重试抢占当前 owner。一个 Agent“收到了通知”不意味着 checkout 成功。
3. **调度运行层**：定时、分派、评论、手动等 wake 进入 heartbeat queue，标记 Run/Agent/Issue 和会话；同 agent 或同 issue 的资源争用还有数据库 lease/queued-run claim/recovery 机制。心跳只是一次有限尝试，不是“24 小时持续模型思想”。
4. **执行与交付层**：adapter 由 server 调度，但实际 Agent CLI/runner/process/HTTP 端点和 sandbox 在对应执行环境行动。Runner 具 startup→turn→settlement 资源生命周期、传输、会话、sync-back、日志和费用收集；UI 仅投影，不是执行所在。
5. **治理与成本层**：公司访问、Agent/run-bound actor identity、审批/执行策略、预算 reservation 与 accounting lock、权限/秘密连接、Skill trust/provenance；层层有效条件不等于“人设里有 CTO”就可改全局权限。
6. **验收/评测层**：`issueExecutionPolicy` 在完成路上强制 review/approval，`run` 结果/issue comments、审查决定和证据历史落库，mock conformance/DB integration/E2E 分不同证据级别。不应把“Agent status succeeded”和“业务成果 verified”混为一个字段。

Paperclip 的“Agentic OS”是它的**产品类比**，不覆盖 UAOS 已注册 parent-child controller。对 UAOS 最有用的是**机制可验证的切分**：持久工作索引、受信事务仲裁、带 attempt 身份的运行、用户批准、外部副作用回执、真实验收。它不是一个必须替换 UAOS 的主仓。

## 3. 十四项可复用机制及代码级事实与限制

### P1. Company/agent/issue/run 四轴身份证明

运行不是普通用户会话：`agent-run-authentication.ts` 按 `runId + companyId + agentId` 查询活动 identity context、responsibleUser、状态/取消信息；`agent-identity.ts` 以 company+agent 获取 Ed25519 公钥，创建时 DB 锁住 owner，在加密私钥解开后比较导出的公钥/指纹，密钥腐败 fail-closed 而非重建。这能消除“用字符串传了 agentId 就拥有身份”的误解。
**限制**：源码可见并非所有外部 harness 绝对一致；必须检验信任身份来源与每个真实 provider adapter 的 run token/host 权限，不能仅看 prompt env 变量。UAOS fit：已有 authority context/RegisteredCapability/ActionCoordinator；仅可在受信 adapter 的 inbound 绑定强检，不新建平行组织身份。

### P2. Issue 归属与 Run 活性两张状态表

Issue `in_progress / blocked / in_review / done` 是任务业务事实；Heartbeat run `queued / running / succeeded / interrupted...` 是尝试事实；liveness/continuation 是又一层元数据。`heartbeat-run-lease-release-terminalization.test.ts` 有“issue done+run 仍 running”、“issue active+run 仍 running”、“queued run lease released”等分歧单测。模型输出“做完了”、进程退出与 issue 完成不能互推。
UAOS fit：TASK_INDEX/exact task 与 Action UNKNOWN 和资产交付 proof 分开，防止一次对话回答取代已验证业务成果。

### P3. 原子 checkout + 竞争状态 fail-closed

Heartbeat 要对具体 Issue `POST /api/issues/<id>/checkout`，绑定运行 ID 与 allowed expected status；当前其它 owner 返回 `409`，Agent 契约明确不得重试同一冲突。队列模块还通过持久 Postgres wake queue/admission lock 与 native lease 区分“已占有 Issue”和“尚未领到 Run”。`agent-start-lock.ts` 另有**进程内**每 agent Promise 排队和 stale timeout，但不能把它当跨主机原子锁；实际跨主机正确性仍需 DB CAS/租约/最终 writer fencing。
UAOS fit：在真实多写者出现时直接检查底层对象 owner/lease generation；不能用 model 端“我在处理”充当锁。

### P4. Heartbeat 是工作循环，不是待命回声

文档规范顺序：认识身份→处理待审批→取任务→选在做工作→atomic checkout→读取上下文和上层目标→同轮做实际动作→写状态/评论→按父子 issue 委派。子任务完成通过系统触发上级，不用空转轮询。最新 Core Skill 增加 `inbox-lite`/inline wake comments，并区分聊天回复无需重复 API 操作的情况。**文档有历史差异，应以 master 的当前 Skill + 服务端 API 合约与真实适配器版本优先，而非混合过期帮助页。**
UAOS fit：用明确 outcome/action receipt 区分研究/计划/执行，而不是每轮无条件创建复杂调度；不假装 ChatGPT 会后台自主心跳。

### P5. Review/approval 是事务状态门禁

`issue-execution-policy.ts` 将 review、approval、原执行者、当前 participant 和 completed stage 绑定到 issue transition。只有 current participant 能推进，结果要求同一次 PATCH 提交的实质评论；不能先在 thread 发“同意”再无说明更新状态。可 `changes_requested` 返回原执行者、再进入同一 stage；默认三轮 agent review 之后有人类 escalation（见 `DEFAULT_MAX_REVIEW_ROUNDS=3`），而非循环永不停。审批通道还有 `approval-records.ts` 在 DB `where status in pending/revision_requested` 上做 CAS，二次 approve 返回 applied=false，不再次发 side effect。
**限制**：文档中某些 `executionPolicy` 是 per-issue optional，board 直接 create agent 和其他 override 权力另有明示；不能称为**所有**写操作都会审查。UAOS fit：只有实际 approved exact action/child owner 才能提高权限，新增“审查模板”不是拦截。

### P6. Budget reservation 不是供应商硬退款/硬限额

`budget-reservations.ts` 首行注释即：**估算用于 admission，但无法封顶 provider bill**。在 `withAccountingTransaction` 的 company-level `FOR NO KEY UPDATE` 锁里，校验 run 状态、已有 reservation、hardStop policy 及未结算的已占额度，然后创建 reservation；因突然断网或重启，hold 要继续存在直到可证实结算/释放，防止超售和错误重发。即便 reservation 为 0 也作为防重复发包的 marker。`budgets.ts` 和 operator 文档有 soft threshold（80%）与 hard-stop（100%）并可在提高预算后恢复。
**限制**：未知外部费用必须记为 unknown，不得算 0；provider 出账可超原估值/结算回执可能延迟；“系统自动暂停”不能逆转已调用外部服务的费用。UAOS fit：无单独付费 API 禁止仍是强约束，必须事前 provider action/cost admission，预算提醒不是预算硬门禁的替代品。

### P7. Pending/UNKNOWN 与真实资源释放必须严格区分

`heartbeat/recovery.ts` 在无法核实 native execution owner 时有明确 `automatic recovery is blocked` 文本；监测 remote termination receipt、本地 PID、native lease 与 workspace finalization。扫尾 retry 有上限，不能随意放弃活 lease。ACPX run coordinator 用单 Owner 先 startup，然后 turn（有类型结果），随后 settle，**最后**再对外返回结果；resource ledger `open → sealed → consumed` 一次 claim，清理函数即使某个失败也遍历余下项并 AggregateError 报告，`run-fault-matrix.test.ts` 含建链部分失败、handshake、resume、timeout、cancel、重复 settlement、sync-back failure 等正反例。
**限制**：调度资源结算不等于外部 SaaS API 已无副作用；任何 provider unknown 仍需单独幂等键/查询协调。UAOS fit：直接强化既有 ActionCoordinator.UNKNOWN/reconcile + PersistentAssetGate，不安装第二 runtime。

### P8. 执行模式与物理隔离不能因产品默认配置被误读

`execution-allowlist.ts` 是受信 host 代码的一个纯判定函数：`executionMode=kubernetes` 严格只允许指定 sandbox provider；`managedSandboxOnly` 禁本地驱动，但可允许其他平台沙箱；**默认 executionMode=any 仍允许 local/SSH 等候选环境**，适用于不同信任部署。启动 `execution-policy-bootstrap.ts` 把环境配置固化到实例，真正 gate 是每次 run 的 allowlist。Runner `paperclip-runner-permissions.ts` 中 Codex `never` 意味无 provider 审批暂停，但注释要求额外 root-denied/workspace-scoped/network-disabled 配置；OpenCode `allow` 则是其另一供应商层面的 permission，不能一概称为安全 sandbox。
UAOS fit：即使源代码有 gate，也不能推定 ChatGPT Cloud/本地宿主默认会运行。必须拿到可信的 execution-host policy+真实 kernel/process/network isolation receipt。

### P9. Skills Catalog → Company Library 是“安装对象”，不是“已会/已应用”

`skills-store.md` 区分只读 curated catalog 与 company database 的安装副本，支持 origin/source commit/hash、版本/升级/漂移。Skill 按实际文件内容推出 `markdown_only / assets / scripts_executables`，不是任由名字自封 `trusted`；GitHub 原始来源须 freeze 成完整 40 位 SHA 才能导入，导入不应自动执行 hooks。外部 live playbook 的薄包装要有来源白名单与不可逆动作审批。**脚本分类 + 来源冻结并不足以证明任何第三方 Skill 行为安全**：最终仍依 host tool policy/allowed external action。
UAOS fit：用户要求的“逐一深学+入库”，最好是**source-pinned CANDIDATE + fit/misfit/falsifier**，而非一见到 SKILL 就安装/启用/偷偷运行。

### P10. CLI 接收低信任内容时 shell 二次解析是实战风险

上游当前 `skills/paperclip/SKILL.md` 特别警告：`pnpm paperclipai` 作为 package script，可能把含 backtick、`$(...)`、环境变量展开的非可信参数交给 shell 二次解释；相应采用直接 argv 的 `npx paperclipai` 或指向本地 `node ... tsx ...`。这是一种**命令调度层与文本内容层**的信任边界错误，不只是 prompt injection。
UAOS fit：任何 provider/CLI adapter 的 untrusted source 应作为结构化 argv/API object，而非拼接给 shell。没有受信运行层时不能声称防注入成功。审查 issue 文本/网页与系统指令也适用。

### P11. 对象归属、可搜索性、可执行身份相互不同

Paperclip 各 company 实体有归属键，`agent-run-authentication` 查相同公司/代理/run，`authorization-run-context.test.ts` 包含低信任 session 仅能访问允许 project、保存 run restriction 不泄漏其他上下文。访问可见（UI/search）、对象所有、对某资源可 mutate/approve 以及实际运行 provider 所用 secrets 是不同维度。
UAOS fit：保持 parent controller、child financial/business 与跨域共享技能研究的最小必要权限；不能因为一个技能在 UAOS doc/research 被检索到，便把 child 配置/生产权限授予它。

### P12. 结果/恢复闭环需“真实变化”，而非文字变长

`tests/lifecycle-baseline/authority.test.ts` 有 `LCA-09 additional commentary cannot manufacture progress or reset an attempt`、审批解锁但同一自然语言仍改变 authority、显式 continuation 的不同执行权限等对照。这和 UAOS 上游目标“主动发现、全局处理、真实验证”高度相关：只说“我会继续”不能把节点从 blocked→complete，增加解释文本也不会清除 attempt budget。
UAOS fit：实际 source diff/CI/主分支回读是文档/代码证据；host 拦截/业务成果仍需另外证明，不能用 100 个日志字段取代结果。

### P13. Capability conformance 要覆盖禁止动作与多跳效果

`packages/paperclip-runner/docs/capability-eval-conformance.md` 声明从受检入仓 traceability derivative 构成离线 **106 cases / 16 groups**，包含 agent tool contract、authorization policy、control plane invariant、multi-hop 和 restraint/no-call，具体 `CAPABILITY_HIGH_RISK_SEMANTIC_VECTORS` 含审批决定、跨租户依赖、幂等冲突、终结重试等。`src/conformance/capability-semantic-conformance.ts` 使用 mock control plane + typed semantic receipts。
**界线**：mock 正确是必要的预先条件，**不是**每个真实适配器的 provider endpoint/身份/费用/权限同步正确，且此研究没有运行全部 106。UAOS fit：应采用对照 falsifiers/外部持久副作用签收，把 `NO_CALL` 正确克制作为正式指标。

### P14. 层级治理和组织工作管理仍需下游产品验收

Paperclip CEO 可制订策略、申请人员、拆分子任务，manager 升级 blocker；有完整 dashboard 运营观测。反面是“组织像公司”容易诱发角色假权限、代理自我评绩、行动过度协调、跨 agent 成本扩张。没有精确定义可验结果的 objective，团队活跃不是价值。任务 owner 只决定调度责任，不自动证明拥有外部业务 target 的 durable write 权。
UAOS fit：沿现有五仓责任线、KnowledgeCatalog/EvolutionTransaction/ActionCoordinator 保持真实 owner；复用 delegated work 和 review mechanics，而不是把 Paperclip 本体包装成 UAOS 第六仓总控。

## 4. Paperclip 与前三项来源的交叉抽象

| 可组合的专业机制 | Hindsight #1 | Orca #2 | Cloudflare #3 | Paperclip #4 | UAOS 接口约束 |
| --- | --- | --- | --- | --- | --- |
| 证据来源/记忆纠偏 | 双时态/引用撤回 | 真实 dispatch 回报 | source:line 反证 | persistent issue context / history | Knowledge evidence，不改当前 task owner |
| 并行 work isolation | bank/scope | worktree/dispatch | hunter scratch/单 parent 写账 | company/issue/run/agent + sandbox | GitHub PR 与受信工具/Host 分开 |
| 错误恢复 | 时态更正 | live/unverifiable/exit + fencing | blocked/deferred/incomplete | queued claim/recovery/resource settlement | ActionCoordinator UNKNOWN，不重复 CREATE |
| 独立审核 | 反射/撤回 | 决策门禁 | 两层新 reviewer + strengthened gate | issue execution stages + CAS approval | 同模型自审不能冒充独立外部 judge |
| 方法使用 | context recall | binary-matched Skill | attack class × trust boundary | Skill Store contentHash/trustLevel | Source-pinned candidate → holdout → proven use |
| 成本/安全 | 检索预算与隐私 | dispatch 重试预算 | runner sandbox 和审计预算 | company spending reserve，executor allowlist | provider actual effect/cost and permission receipt |

重要差异：Paperclip 和 Orca 都已经实现某类调度/资源模型，直接部署会引入持久后端、host、token/预算、权限、资产复制。UAOS 如果只是当前 ChatGPT 会话 + GitHub 受控修改，并不因此自带真实持续后台 agent；此外 Paperclip 的 standalone local/HTTP provider 可产生不可见外部写，必须先确认 connector 入/出站行为。外部模块的优点要带着它依赖的机制条件一起迁移。

## 5. 外部交叉评估：替代方案及局限

| 专业参照 | 对 Paperclip/UAOS 的独立校验角度 | 不能混为一谈 |
| --- | --- | --- |
| [Temporal Activity](https://github.com/temporalio/documentation/blob/main/docs/encyclopedia/activities/activity-definition.mdx) | Activity 被重试会有物理多次执行，provider API 侧必须支持稳定幂等键；workflow 观测 `completed` once 不等于外部 side effect exactly-once | Heartbeat queue 防重复启动 ≠ Gmail/支付/provider 一定只执行一次 |
| [OPA authorization](https://www.openpolicyagent.org/docs) | policy decision (PDP) 与真实入口 enforcement (PEP) 分离，必要时各路 API 同步执行相同许可规则 | “角色属于 CEO”或模型读了 SKILL ≠ 所有外部连接都受 RBAC |
| [NIST AI RMF](https://airc.nist.gov/) | 治理、地图、衡量、管理；评估在真实用户价值/安全风险和高频代理变化中有证据 | Product dashboard/监控次数 ≠ 闭环治理效果或真实鲁棒性 |
| UAOS 当前源法 | 固定原 task authority、source frozen、PR/CI/main-readback、child original owner 验收 | 不将“上线了别家完整 SaaS”误报成现有 UAOS 自动运行 |

备选：
- **A 整体部署 Paperclip 并作为 UAOS 总控**：可获得 DB/runtime/dashboard 实体，却增加第二 owner、迁移费用、长期主机、身份/密钥/联网和生产迁移风险，现阶段没有用户授权/独立证明，不选。
- **B 只模仿 Paperclip 术语/组织图/Prompt**：便宜但无事务仲裁，无法实现真实强制审查和可靠恢复，不选。
- **C 将关键机制证据化为方法候选并在现有 UAOS owner 层触发适配**：保留可证伪边界，不依赖新服务，选。
- **D 不学习**：无法满足指定 4/4 的长期知识积累目标，不选。

## 6. 十四张 UAOS 方法卡（候选知识，无实际 usage links）

每张卡必须按 `source_ref` / `source_sha` / `trigger` / `fit` / `misfit` / `owner` / `falsifier` / `validation_plan` / `usage_links=[]` 存入受控 Knowledge 流程。不能将文档里的卡片宣称为独立活跃数据库项或 CANONICAL。

1. **PAP-01：Company-Agent-Issue-Run 四维入站身份**。Trigger：多 Agent provider 回报；Owner：trusted RegisteredCapability / domain owner；Misfit：仅凭模型自报 id；Falsifier：旧 run 可修改其它 company；Validation：cross-company + wrong-run + replay identity holdout。
2. **PAP-02：Task Status / Run Attempt Status 正交**。Trigger：heartbeat 中断/状态错位；Owner：existing exact task/ActionCoordinator；Misfit：run succeeded 强推业务 done；Falsifier：lease 释放后仍出现悬挂 run；Validation：四象限状态矩阵。
3. **PAP-03：原子 Issue Checkout 与真实 writer fencing**。Trigger：重入/并发双工；Owner：actual DB/provider adapter；Misfit：把内存锁或 PR branch 视为全局锁；Falsifier：同 issue 两个进程都通过；Validation：两个实例同步竞争 + 迟到写。
4. **PAP-04：Wake-Coalescing/任务归属/轮次上下文**。Trigger：大量评论唤醒、批量委派；Owner：existing Deep Task/host；Misfit：无后台执行服务；Falsifier：重复相同 wake 导致二次外部写；Validation：comment burst + lost-receipt + task cursor。
5. **PAP-05：Stage 审批绑定参与者及决策正文**。Trigger：业务高风险/人类签收；Owner：UAOS approval/child original authority；Misfit：审批随模型文本自动放行；Falsifier：非当前 reviewer 一句话推进 done；Validation：wrong reviewer, missing same-PATCH comment, changes_requested loop。
6. **PAP-06：预算预留与真实结算区别**。Trigger：付费 provider 或多个并发 Agent；Owner：CapabilityRouter/actual provider billing；Misfit：估价当绝对硬封顶；Falsifier：两个 run 共用额度超发/未知账单算 0；Validation：并发 claim、timeout hold、跨月结算、provider 出账超估。
7. **PAP-07：资源生命周期所有权和一次 settlement**。Trigger：CLI/runner/浏览器/沙箱；Owner：host runtime adapter；Misfit：无持久 run 执行层；Falsifier：双结算、清理失败却覆盖原 error；Validation：ACPX 风险矩阵与资源 dispositions。
8. **PAP-08：Unverifiable recovery 不自动重试副作用**。Trigger：断线/不明 provider 结果；Owner：ActionCoordinator.reconcile；Misfit：网络超时断言 FAILED；Falsifier：实际成功写入后自动二次 CREATE；Validation：response loss + external provider reconciliation + idempotency key。
9. **PAP-09：执行模式 allowlist 与实际 OS 隔离**。Trigger：处理不可信 Agent 代码；Owner：host sandbox/Capability admission；Misfit：默认 any、UI permission 名称即隔离；Falsifier：untrusted 运行在 local/root、出站网络未限制；Validation：host-level deny-and-audit。
10. **PAP-10：Skill 内容指纹、签名来源和 scripts 风险等级**。Trigger：外部 Skill 导入/升级；Owner：KnowledgeCatalog + sandboxed adapter；Misfit：GitHub 来源视为可执行安全证据；Falsifier：换了源 commit 却仍执行旧/新未审内容；Validation：manifest hash drift, script-trust positive/negative。
11. **PAP-11：非可信文本被 shell 二次解释的阻断**。Trigger：CLI 参数含正文/Markdown；Owner：trusted tool adapter argv gateway；Misfit：拼接 bash/pnpm scripts；Falsifier：`$(...)` 引发意外命令；Validation：无害可验证 marker 命令模拟与 argv 单测（隔离环境）。
12. **PAP-12：No-call 与语义多跳 conformance**。Trigger：扩展 connector/真实 Agent 工具；Owner：UAOS capability contract/gateway；Misfit：只有 Mock 通过就称生产通过；Falsifier：mock restraint=no_call、真实 adapter 却执行外部工具；Validation：mock→real adapter parity, cross-company and approval negative。
13. **PAP-13：组织目标→父任务→结果的可追溯链**。Trigger：跨模块项目/长运行代理组织；Owner：UAOS parent coordination + domain-specific task truth；Misfit：凭 CEO persona 自动获得 write 权；Falsifier：无 owner/goal 的代办被自我视为已授权完成；Validation：parent lineage, terminal business output acceptance。
14. **PAP-14：计费/资格/结果未知不得默认成功**。Trigger：源项目标准不一、费用账单丢失、远程 runner qualification；Owner：Assurance + honest source evidence；Misfit：任何缺数据都按 0/已合格；Falsifier：qualification pending 时被当 native production pass；Validation：unknown-vs-zero、pending-vs-passed 两组冻结回归。

优先级：PAP-03/05/06/07/08/09/11/12 是 UAOS 真正的工具越权、重复写、成本与合规故障风险高地；PAP-01/02/04/10/13/14 更适用于跨仓大型任务的治理可观测与方法召回。**卡片是候选，不允许自封实测效果**。

## 7. 冻结 holdout 与负向实验（只做测试设计，尚未执行）

1. 两个独立 scheduler 并发 claim 同一 issue：至多一个活 owner，另一条路径 409/reconcile，不新建重复外部对象。
2. 一个 agent 已执行 run A，run B 夺回任务后 A 的晚到 “done”：不得越权提交 B 的 issue 状态。
3. 伪造 `PAPERCLIP_AGENT_ID/COMPANY_ID/RUN_ID` 的不匹配 JWT：provider admission 拒绝。
4. 用别家公司合法 actor 查看并改另一个公司 issue：拒绝，不能被语义相似检索泄漏。
5. 一个 issue 已 done 但 heartbeat run 还 running：资源必须按可证明 evidence/lease 终结，不覆写 issue 决定。
6. run interrupted 但 issue active：不能因评论“已完成”将 issue 改 done。
7. Issue review stage 绑定 QA-X：QA-Y 的 status-only PATCH 不能批准。
8. QA-X 先发普通 comment 后单独 PATCH done：不能绕过 same-PATCH decision comment。
9. 审批状态已 approved 再 retry approve：`applied=false` 且没有重复 side effect。
10. Agent review 循环超过默认 3 轮或 profile max：应有真正 human escalation，不无限自批。
11. Budget month $X 已被两个 pending provider run 预留：第三次 admission 必须受公司锁拒绝，避免 check-then-act race。
12. Provider 已实际消费费用但 cost event 缺失：保持 unknown/待结算，禁止 $0 展示为确定。
13. 跨月但上月 reservation unresolved：不可自动释放并新开额外预算窗口忽视旧 hold。
14. Admitted provider 一次花费超估：系统认作外部费用仍可能高于 reservation，不能把预算门禁当供应商账单撤回。
15. 外部 API 创建成功但返回丢失：重试前必须凭 provider receipt/idempotency reconcile。
16. 回收本地 AC P runtime 时部分 staging/sync-back failure：settlement 遍历所有资源，任何失败保留审计信息。
17. 对同一个 resource ledger 两次 `takeForSettlement`：第二次应拒绝并不再执行 cleanup。
18. 默认 `executionMode=any` 的 local adapter：不要虚构已隔离；强制 kubernetes 后非该 provider 的实际 run 应 fail-closed。
19. OpenCode 全自动 allow 模式：不得当成 container/ACL；拿 host 网络/文件访问负测收据。
20. Skill 导入脚本/静态资源混合：trustLevel 应随文件内容提升，GitHub branch drift 不得静默替换冻结 SHA。
21. 包含 backticks/`$(date)` 的任务标题被 CLI 作为单个数据参数：不得执行 shell 展开；需在隔离测试脚本中断言 argv。
22. Mock conformance `no_call` 成功，但真实 provider 行为相反：不得用 mock pass 升格原生 pass。
23. 长时 agent 的 `task done` 只有状态和自评，没有 artifact/test/signed external receipt：业务验收仍待完成。
24. Runner-rich ACP checkpoint 标记 pending：其相应环境/模型资格不能按 passed 排入生产配置。
25. 非指定 financial child 经 parent 仿 Paperclip 的 CEO persona 直接修改 child 发布内容：必须由 UAOS 当前 AuthorityWritePolicy 拒绝或按治理 basis 正常 admission。
26. 在无法提供独立运行宿主、DB 或外部授权时，Paperclip Skill 能读/解释，但不能产生“自主持续监控 Agent 组织”真实证明。
27. 对比现有 UAOS vs 借鉴候选机制：以 source-confirmed path、双写防范、真实成本、独立 judge 重现、用户业务后效为度量，不以 agent 数量、评论次数或代码行数定高低。
28. 主分支发布 4/4 知识研究后，四份文档均可 exact readback；但原生 selected-chat 技能入口/Agent heartbeat/外部真实 holdout 仍须标 UNVERIFIED。

评价指标：source-grounded 证据引用率，事件/成果错认率，cross-owner mutation reject，重复外部资产率，pending resource cleanup 收敛，budget reservation overcommit，未定价比例，provider mock vs real 差异，Skill 源漂移阻断率，no-call 正确率，人工批准漏闸率，端到端业务独立验收率和平均/尾部成本延迟。预定义 good/bad 目标后才能判断迁移价值。

## 8. 知识入库边界与下一阶段唯一真实动作

本资料放入 UAOS 已有 `docs/research`，不建立第二 Paperclip 控制面、第二任务状态索引、第二 Knowledge authority，不在当前用户没有授权的情况下运行 third-party agent、创建云实例、支付 API/外部密钥服务或跨 child 写产品状态。与 Hindsight、Orca、Cloudflare 三项一样，仅有源码学习、比较和候选卡片，**没有**实际受控 KnowledgeCatalog `CANDIDATE→EVALUATED→CANONICAL` 的提升或真实跨业务 usage links。

完成来源研究 4/4 后，UAOS controller 依然有主目标：**五仓深审、全球治理效应可验证、跨域方法召回/裁剪、native host interception/observability、child 真业务验收**。下一动作不是再“学第 5 个截图仓”，而是回到唯一父任务的明确未完成环节，优先审计现有 UAOS 是否已具备可信工具入口/原生独立复验路径；再按高风险/可执行性选择已收录的候选方法进行有外部证据的实际实验，并记录通过或失败。只有能力 host 真执行、证据反证通过、业务 owner 接受，才可以对特定方法晋级。财务写作受控专项保留 RUNNING/not default，仍须等 parent governance 决定何时续接。

**判定**：第 4/4 项 Paperclip 的研究与方法蒸馏完成（源码角色级，不是逐行或运行饱和），其 14 张卡片均为 CANDIDATE、28 项 holdout 均为 TEST_SPEC_ONLY、整个 UAOS 主任务仍为 RUNNING。绝不使用源码仓自身测试文件或 README 宣传替代 UAOS ChatGPT Native/Host 真实执行证据。
