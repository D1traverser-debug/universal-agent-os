# 14 — Cloudflare Security Audit Skill：来源研究、覆盖驱动审计、独立反证与 UAOS 安全保证迁移

**源对象**：Cloudflare 官方仓库 `cloudflare/security-audit-skill`，而非字面上不存在的 `cloudflare/security-audit` 仓库。固定 **main = c1c8a8c1471069fb0e188eeaff69b8e8db6564a8**（源提交日期 2026-09-14），用户截图学习顺序第 **3/4** 项。**所属 authority**：UAOS controller；唯一任务进度参见 `state/tasks/uaos-inheritance-review-20261018.json`。研究记录性质：**SOURCE-STUDY / CANDIDATE KNOWLEDGE / NO INSTALL / NO RUNTIME AUDIT / NO CANONICAL PROMOTION**。

本次目标是研究外部方法并提炼可以检验的机制，**不是**给任何线上主机做渗透、安装外部 Skill、运行源代码、创建另一个安全总控或以文档冒充已部署的 UAOS 安全门禁。当前工具只能核对 GitHub 源码及其测试结构，不能宣称运行了 Cloudflare 的本地 CLI、它的并发 subagent harness、真实 OS sandbox 或生产 UAOS 的 native selected-chat 前置执行器。

## 1. 研究定位、来源角色与核验覆盖

官方 README 说明此 Skill 是其更大型漏洞发现 harness 的**单仓起点**：多阶段、多执行主体、机器可读结果、独立复查、对运行路径和安全边界有严格限制；其官方产品文章描述的 fleet-wide harness **不能等同**此公开 Skill 的可执行能力。官方 MIT 许可证允许研究与改作，但复制实质性原文须保留版权及许可声明；本研究只作原则/流程/方法卡蒸馏，不复制原工程或声称二次部署。见 [README.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/README.md)、[LICENSE](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/LICENSE)、[Cloudflare 技术文章](https://blog.cloudflare.com/build-your-own-vulnerability-harness/)。

冻结树共有 24 个条目，其中两个目录、22 个文件；含入口 README/许可证、**15 个 Markdown 方法文件**（SKILL、RECON、HUNT、ATTACK、VALIDATION 及 10 个领域 companion；根目录 README 另计）、1 个 report-schema、2 个 Node validator、2 个对应测试。采集路径：完整审阅中心五段工作流与 README/许可，逐一解析领域 companion 的启用条件、Core discipline、攻击族、Universal moves、Validation rules，检查 schema 三个 verdict 分支，定位校验器实际函数及负向单测名称，并独立交叉核对公开 Issue 与安全工程标准。**没有逐行人工重跑 22 个文件，也没有本地测试执行，不能称为完整动态或形式化证明。**

### 1.1 原始资料 / 角色矩阵

| 来源角色 | 固定来源 | 在本次证明什么，不证明什么 |
| --- | --- | --- |
| 产品、入口、运行方式 | [README.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/README.md)；[skills/security-audit/SKILL.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/SKILL.md) | 全审计与 guidance 模式的触发条件、资源和风险约束；不证明 ChatGPT 原生能自动加载 |
| 确定性覆盖计划 | [skills/security-audit/RECONNAISSANCE.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/RECONNAISSANCE.md) | 四个基线 recon agent、输入面/边界/子系统/攻击类别的稳定身份、状态机与前次 evidence 重用 |
| 攻击与子代理执行 | [skills/security-audit/HUNTING.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/HUNTING.md)；[skills/security-audit/ATTACK-CLASSES.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/ATTACK-CLASSES.md) | Hunter Prompt 契约、严格隔离、coverage critic waves 和 sibling paths；非真实并发执行证明 |
| 独立候选验证 | [skills/security-audit/VALIDATION-AND-REPORTING.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/VALIDATION-AND-REPORTING.md) | Phase 3 与 5 的 agent independence、纠错和重新审查界线 |
| 结构化结果 | [skills/security-audit/report-schema.json](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/report-schema.json) | confirmed / needs_validation / rejected 分支、字段要求和额外字段拒绝 |
| 机器校验 | [skills/security-audit/validate-coverage-ledger.cjs](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/validate-coverage-ledger.cjs)；[skills/security-audit/validate-findings.cjs](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/validate-findings.cjs) | 文本、状态、路径、字段、输入大小、编码等静态约束的执行代码；不等于证据真实性 |
| 校验负例 | [skills/security-audit/validate-coverage-ledger.test.cjs](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/validate-coverage-ledger.test.cjs)；[skills/security-audit/validate-findings.test.cjs](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/validate-findings.test.cjs) | 有针对 ID 冲突、路径、状态、非法 Unicode、大小/深度、FIFO/symlink 等测试；未在本轮重跑 |
| AI/Agent 专项 | [skills/security-audit/AI-AND-LLM.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/AI-AND-LLM.md) | RAG/记忆/工具/委派/MCP 的代码授权与 action binding 风险 |
| 持久化与交接 | [skills/security-audit/DATA-ISOLATION-AND-LIFECYCLE.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/DATA-ISOLATION-AND-LIFECYCLE.md)；[skills/security-audit/SUPPLY-CHAIN-AND-RELEASE.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/SUPPLY-CHAIN-AND-RELEASE.md) | 缓存/删除/恢复/派生副本与 CI/构建/签名/发布检查 |
| 其他攻击族 | [skills/security-audit/WEB-PROTOCOL-AND-AUTH.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/WEB-PROTOCOL-AND-AUTH.md)；[skills/security-audit/CLIENT-SIDE.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/CLIENT-SIDE.md)；[skills/security-audit/CLOUD-AND-DEPLOYMENT.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/CLOUD-AND-DEPLOYMENT.md)；[skills/security-audit/PROTOCOLS-RPC-AND-MESSAGING.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/PROTOCOLS-RPC-AND-MESSAGING.md)；[skills/security-audit/RESOURCE-EXHAUSTION-AND-AVAILABILITY.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/RESOURCE-EXHAUSTION-AND-AVAILABILITY.md)；[skills/security-audit/MEMORY-SAFETY-AND-BINARY.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/MEMORY-SAFETY-AND-BINARY.md)；[skills/security-audit/DESKTOP-MOBILE-AND-LOCAL-IPC.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/DESKTOP-MOBILE-AND-LOCAL-IPC.md) | 针对真实边界激活领域补充；不是所有仓库都必做全族 |
| 独立安全方法 | [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)；[OWASP ASVS 5.0](https://github.com/OWASP/ASVS)；[NIST SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final) | 信任边界、设计/验收安全要求和安全开发流程交叉验证，不能证明此 Skill 所有能力已通过 |
| 公开反例 | [上游 Issue #21](https://github.com/cloudflare/security-audit-skill/issues/21)；[Issue #53](https://github.com/cloudflare/security-audit-skill/issues/53) | ledger artifact 实在性与 Windows 安全文件打开兼容性公开问题；编号按当前 GitHub API 而非搜索结果页面别名 |

### 1.2 方法学习是否充分（来源角色/扩展/饱和度）

角色覆盖：一手权威 README、完整策略 Skill、执行步骤、数据 schema、实际 validator 与测试、领域 companion、上游缺陷报告、外部 OWASP/NIST，覆盖**设计、实现、测试、反例、比较**。扩展不局限初始词 `security-audit`：还从攻击族、威胁建模、数据生命周期、AI 工具授权、软件供应链与 CLI 平台兼容性多镜头取材。已经明确两个可证伪争议（证据文件是否被真的校验、Windows CLI 是否能工作），所以不宜宣布“方法无未知项”。真实宿主安装/触发、OS sandbox 建立、现场运行、误报漏报、独立复核实际质量、CI/用户业务效果全部 **UNVERIFIED**；知识饱和标注 `SOURCE_ROLE_COVERED__REAL_USAGE_HOLDOUT_UNSATURATED`。

## 2. 准确还原这项 Skill 的六阶段工作流

| 阶段 | 实际负责主体与持久产物 | 重要防误判机制 |
| --- | --- | --- |
| 0. 模式 / 审计准入 | guidance 默认为针对问询/定点分析；只有明确全面 codebase audit/pen-test/报告时全模式；parent 写 `run-metadata.json` | “加载 Skill”不授权写文件或运行目标。target 和 output path 分离；外部/线上 API 禁止测试 |
| 1. Recon | 4 个预留调用：业务/栈、身份权限、输入与 sink、离线/部署可见性；parent 写不超约 1000 词的 `architecture.md` 和 `coverage-ledger.json` | source:line、前次引用回核、外部部署不可见明确标记，非凭假设放行 |
| 2. Hunt | hunter 领取稳定 ID 的覆盖单元；parent 独写 ledger；每 wave 后独立 `coverage critic` 拾漏与重分配 | 必须细看 sibling/batch/legacy/retry/revoke/error；未分配单位记 deferred，不允许默默“扫完” |
| 3. Candidate validation | 每个唯一 fingerprint 交给**不是 hunter 的全新 verifier**，优先找反例 | 以具体 principal / resource / boundary / observed result 为确认门槛，缺关键事实留 needs_validation |
| 4. Structured output | parent 写 sorted `findings.json` 并分别运行 findings 与 ledger validators | verdict 三分支互斥，字段契约/顺序/路径/状态结构有效；不等于运行真实性 |
| 5. Independent record verification | 除 quick 合并验收外，全新 agent 对最终记录再检；重大替换交再独立 verifier | 不允许审查者自我批准 stronger verdict；无法重新验明则 incomplete |
| 6. Report | 从最终 JSON 与 ledger 派生 `REPORT.md`, `FINDINGS-DETAIL.md`, `NEEDS-VALIDATION.md` | human prose 不能改 JSON verdict、影响和缺证结论 |

终态只有 `run_status=complete` 且产物齐全、两个结构校验通过、记录验证完成，或 `run_status=incomplete` 并显式写原因和缺口；“运行结束/有报告/无 confirmed”都不自动等于全覆盖。三种 profile：quick 为一 wave+最终 critic、一独立验证；standard 保留多 wave 与 final clean critic；deep 加大按子系统/生命周期分解、将候选和最终验证分两批独立 agent。预算必须预留 recon/critic/verifier，预算不足要停止而不是缩掉安全审查。依据 SKILL、RECON、HUNT、VALIDATION。

## 3. 核心机制深读与真实可执行边界

### M1 按 `source × trust boundary × subsystem × attack class × lifecycle` 建立确定性覆盖账本

Coverage unit 的真实 identity 来自 `canonical_refs`，按 UTF-8、NFC、RFC3986 percent encode + `::` 拼接，避免随手把显示标签、agent 名、波次、判定写进 ID；同一语义引用不同 ID 或相同 ID 对不同语义均判冲突。相同 source object 在多轮审计必须沿用稳定引用。主 ledger 状态包括 planned / in_progress / covered / blocked / candidate / deferred / out_of_scope / not_applicable；非完成态不得冒充已覆盖。每次 critic 回开 covered/candidate/blocked 时把旧尝试 append-only 存入 `attempts[]`，新 owner/new wave 从空证据开始，不克隆先前结果。离线文件中的 `reviewed_paths` 要恰等于检查子项的集合，不是靠 parent 一句“所有路径已查”。来源：RECON 第 1 阶段、ledger validator `canonicalCoverageId`、`validateStateInvariants`、`validateAttempts`、对应测试。

**转移价值**：把“做过检查”转化为**稳定工作单元+引用路径+覆盖类型+失败/没做到理由**。但“正确造出 coverage_id”本身不证明已经找遍未建账本的未知入口；coverage critic 的深度和独立性不可省略。

### M2 先识别真正信任边界，再选攻击族，而非按标签包办

核心 ATTACK-CLASSES.md 有 injection、access control、resource/file、cryptography/secrets、business logic、feature abuse/data leakage、chained trust boundary、wildcard 和 obvious things。10 个专业 companion 的启用是按 **source-visible boundary** 而不是出现某个语言名、依赖名：
1. AI/LLM：间接注入、记忆污染、MCP/工具身份、schema-dispatch 不一致、未绑定动作批准、上下文跨租户。
2. Web identity：HTTP framing / cache key、Host/Forwarded、JWT/OAuth/SAML、MFA/WebAuthn、会话恢复。
3. Client/browser：DOM sink、postMessage、WebSocket/CORS、service worker/cache、browser lifecycle。
4. Data lifecycle：主库与 index/cache/log/export/backup/restore/queue 的 ACL、撤回和删除继承。
5. Supply chain：依赖锁定、CI 触发人、build→artifact→signature→promotion 的完整性、可更新插件。
6. Cloud：IAM/Workload identity、配置覆盖层、mesh/ingress、object-store 与生产不可见控制。
7. RPC/messaging：消息身份、重放/顺序、ack/commit、幂等、不同版本解析歧义。
8. Availability：非共享环境中小尺度可复核的资源放大、取消后工作、operator spend，绝不向共享服务压测。
9. Native/binary：FFI/ABI、integer、UAF、loader、race、内核特权界面；崩溃不得自动推导 RCE。
10. Desktop/mobile/IPC：deep link、native bridge、peer credentials、helper、设备/账户生命周期。

对 UAOS 特别有意义的是 AI companion 明确：**prompt 本身不是安全边界**；model output/memory/tool description/MCP response 均是 untrusted，须找到确定性工具鉴权与实际 sink；“意图批准 exact action”和“调用者拥有授权”是两项不同的判定。直接用户授权某动作，并不代表文档/网页里的指令可替其下令。见 [skills/security-audit/AI-AND-LLM.md](https://github.com/cloudflare/security-audit-skill/blob/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit/AI-AND-LLM.md)。

### M3 攻击候选必须能从 source 到 observable boundary effect 追踪

六要素：lower-trust principal → accepted input/action/state → control/invariant → source propagation → affected principal/resource → bounded observed result。视同一主体自操作/自损或单纯缺最佳实践为 hardening/nonfinding；未能观察部署的提供商/网关/浏览器行为时，不替实物做推断。它可与 OWASP STRIDE/DFD 威胁识别相配合，但 Cloudflare 的最终报告门槛更窄：**只确认经独立本地可控证据支持的可达失守**。由此减少噪声，也可能漏掉依赖真实部署的风险；那些应显示为 needs_validation 而非“不存在”。证据：SKILL Core principles、HUNT Core method、VALIDATION Candidate verifier。

### M4 工作分派是 evidence ownership，不是“多 Agent 数量越多越好”

Parent 是 run metadata / ledger / findings / reports 的唯一写者。每个 hunter/verifier 有专属 `agents/<id>/scratch`；被审计目标的可执行程序仅可写 scratch，retained `artifacts` 不允许被目标程序/agent 直接写。文件从 scratch 提升到 artifacts 由受信 parent 持有根 dirfd，逐层 nofollow，限定 regular file、唯一 link、大小/累积限额、首尾 fstat 和独占目标创建。不存在该 trusted promotion 机制时，**本地代码执行结果不可自动升级为持久证据**。注意这是**程序性规范**，公开 Skill 仅含 Markdown、schema 和两个 validator，仓库树中**没有完整执行 sandbox / dirfd promotion 的受信生产宿主实现**。即使 Node validator 校验通过，仍需核对宿主是否真的隔离和受信提升。

### M5 独立验证要能够反驳猎手，而不是复述

Phase 3 fresh general verifier 从初始输入重读源、最强防线、部署条件、已有反例，尝试最小可控复验并给 confirmed/needs_validation/rejected；Phase 5 fresh research verifier 再检查最终 JSON，每项都要校正指纹、影响程度与修复范围。若 Phase 5 要把等级变得更强或改变 root cause、trace、输入、观察结果/严重度，必须交给**第三个未参与者**重新验证，而不是 review 改一句“已确认”。quick 压缩轮数不压缩独立 candidate gate。没有独立 provider/host 能力时不得把同一模型自评写成外部 judge。

### M6 严重程度与确定性分离

`confirmed` 需要 exact trace、bounded execution、conditions、root cause、remediation 和 severity likelihood/impact/overall；`needs_validation` 只给 claimed root cause、证据、blockers、适用的 local/deployment 计划，**不得有 severity**；`rejected` 记录已被推翻的候选及理由，以免下次无证据地复现主张。`severity.overall` 不得超过已展示的 `impact`。这三者不是一个置信度阈值上的不同形容词，而是不同 evidence contract。来源 report-schema 与 validate-findings 的语义校验。

### M7 增量回看有“源是否真的变了”的判据

读取已有 ledger + findings 后不能仅凭 commit hash 相同就假设路径相同，更不能因 quick/scoped 的 prior covered 直接压制全审计。前次 unchanged-source confirmed 仅可暂时作为候选携带，且还需最新独立复核；changed-source confirmed 必须重新进入 hunt；needs_validation、deferred、blocked、out_of_scope 都不自动免检。被驳回的只是“同根因且证据不变的特定 claim”，不是整个入口单元。此机制可借给 UAOS 的源变更影响链、状态恢复与历史修复复核；仍须保留 owner 层级和 exact source。

## 4. 校验器与测试：真实源码支持什么，不能支持什么

- 代码确有 **两个零额外依赖的 CommonJS validator** 和对应 `node:test` suite，不是纯宣传。ledger validator 873 行，findings validator 774 行；各自单测有约 31/34 个以 `test(...)` 声明的场景。这里只核对代码及单测定义，**没有运行 npm/node**。
- findings validator 读取 `report-schema.json`，检验 `oneOf` verdict 与 additionalProperties false、完整 trace 类别、正行号、排序/唯一、UTF-8、输入大小/深度、安全路径/人类可见文字，并阻止 severity overall 超过已声明 impact。它**不能**独立证伪 source line 是否真存在、模型读没读、sandbox 中有没有真实发生结果、某个审查者是否真的独立。
- ledger validator `isOwnedArtifactPath`（源 394–398 行）只检查安全相对路径和 `agents/<id>/artifacts/` 字符串归属；`validateChecks`（421–450 行）据此拒绝错误格式、所有者不匹配。**并未在 ledger 校验的检查子项对磁盘上的 artifact 执行 `stat/lstat` 或检查其真实存在**。其 `readFileWithinLimit` 读的是 ledger JSON 文件**本身**。上游 [Issue #21](https://github.com/cloudflare/security-audit-skill/issues/21) 同样报道：合法格式却不存在的本地 artifact 可以得到 `PASS`。这不是证明 Cloudflare 线上服务遭漏洞攻击；属于证据完整性验证缺口，并且仓库文档另要求受信提升者在实际工作流中保证。
- 两个 CLI 的输入读取均要求 OS 暴露非零 `O_NOFOLLOW` 与 `O_NONBLOCK`：ledger 源 721–727 行、findings 源 604–609 行。Windows Node 下这些标志可能不可用，于是主动报 `OS no-follow and nonblocking input protection is unavailable` 并拒绝全部输入；上游 [Issue #53](https://github.com/cloudflare/security-audit-skill/issues/53) 对此提供复现。此保守安全选择换来了跨平台不可运行的可能性；**不应通过偷偷降级为普通 fs.open 来宣称修好了**。
- Unit-test 具有防原型链继承/alias、非法 Unicode/控制字符、重复 canonical ID、状态所有权、archived owner evidence 泄露、FIFO/symlink 安全读取和大量 malformed 输入限制等负例。确有相应测试文件，但未取得上游本提交的 CI 实际运行回执，也没有独立执行。
- 报告的机器校验是**格式完整性 + 状态语义约束**，与“证据实在性/审查真正发生/宿主安全隔离/实际漏洞真实存在”是四层不同问题。建议复用此方法时每一层建立各自 verifier 和 receipt，而非一个 `PASS` 封顶。

## 5. 外部安全工程方法对照与反例

| 方案/标准 | 可借鉴 | 不应混淆 |
| --- | --- | --- |
| OWASP 威胁建模（DFD/STRIDE/attack tree/abuse cases） | 先建模 principal、输入、数据流、信任边界，找未曾列入的 threat；更利于 **未知路径发现** | Threat brainstorm 未经 code path 证据不等于 vulnerability `confirmed` |
| OWASP ASVS 5.0 | 以预定义的可验安全要求做设计/验收 baseline，补 Cloudflare 只报告真已观察突破的保守性 | checklist 的 fail 可能只是 hardening，安全要求未达标 ≠ 已发生越权 |
| NIST SSDF 1.1 | 把验证/根因复发预防和安全开发流程相连，贯穿从源、构建、发布到维护 | CI 通过/文件存在 ≠ 实际部署及用户结果 |
| Cloudflare 六阶段 Skill | Coverage ledger、受信 parent、独立反证、分类结果、证据受限、增量 recheck | 未提供此公开仓库以外的完整 Agent hosting/sandbox/CI/commit enforcement |
| UAOS 当前 CognitionCase/Deep Task/Evolution | 目标→证据→多因子候选→干预→真实验证，跨域知识候选复用 | 不应再建一套通用审计“总控”；领域安全审计可能是一个受限方法子流程 |

**替代路线比较**：
A. 全量复制/安装 Cloudflare skill 及其所有流程到 UAOS：仅在有真实 subagent host、sandbox、trusted artifact promotion、独立 verifier、资源预算和业务授权时才可能支持；现在增加双重 owner、成本与虚假安全感。**不选**。
B. 只保留通用十项 checklist：省时间但不会强制来源、coverage、三态和反证，复发“文档即执行”问题。**不选作唯一方法**。
C. 将来源级知识归纳为带 owner/fit/misfit/falsifier 的候选方法卡，沿 UAOS 既有 CognitionCase/Deep Task/ActionCoordinator/Knowledge/EVOLUTION Gate 调用；未来具体安全要求再选用，并做真实 holdout。**本轮采用**。
D. 完全不学习：不满足用户指定的全面学习并持久化要求，仅作对照基线。

## 6. 十二张待评估候选方法卡（全部 CANDIDATE）

卡片字段最少为 `source_ref`、`owner`、`trigger`、`fit`、`misfit`、`falsifier`、`validation_plan`、`usage_evidence_refs`。此处 `usage_evidence_refs=[]`；不能宣称已经进入 UAOS canonical KnowledgeCatalog 或实测提高发现率。

1. **CSA-01 / 信任边界—源—sink 追踪**：trigger=安全缺陷、Agent 越权；owner=现有 CognitionCase + child domain source authority；misfit=只有架构图没有代码；falsifier=确认路径其实被中间 ACL 阻断；验证=带恶意/良性输入的最小 source-local 对照。
2. **CSA-02 / 确定性 coverage unit**：trigger=跨仓、多输入面、长时审查；owner=现有 Deep Task/KnowledgeAcquisition evidence；misfit=单点精确 lookup；falsifier=同源不同标签产生漏检/重复 ID；验证=稳定 refs、缺口 critic、跨 run replay。
3. **CSA-03 / 单写者与委派产物隔离**：trigger=多代理或不可信目标程序参与；owner=Trusted capability/asset adapter；misfit=认为 Markdown 能创建 sandbox；falsifier=delegated agent 直改 parent authority；验证=write-deny/污染分离负测。
4. **CSA-04 / 执行受限与证据安全提升**：trigger=需要运行目标代码或保留 fixture；owner=实际受信 host + persistent asset gate；misfit=没有 OS sandbox 或 dirfd promotion；falsifier=symlink/race 可从 scratch 获取秘密或写 artifact；验证=受信执行层隔离、符号链接与文件类型对抗测试。
5. **CSA-05 / 三态证据裁决**：trigger=source-grounded 漏洞/方法缺口；owner=CognitionCase evidence / Assurance，不另建 verdict authority；misfit=猜测无需具体主体和结果；falsifier=needs_validation 被给 severity 或假定 host 行为；验证=contradictory and missing-condition holdouts。
6. **CSA-06 / 先反证后确认**：trigger=高影响问题或模型单方分析；owner=现有 Independent Judge / Deep Task；misfit=同一模型改写自己的报告自称独立；falsifier=强防线被忽略或 severity 过高；验证=不同 verifier 当前源码读回与最小复验。
7. **CSA-07 / 两轮结果审查与强结论升级门**：trigger=关键结论、变更 verdict/影响；owner=existing controlled finalization；misfit=简单已知低风险 lookup；falsifier=提出 stronger verdict 的 verifier 自己批准；验证=第三方 reviewer 及物化 source-local receipt。
8. **CSA-08 / 历史账本增量与源更改重验**：trigger=重跑、跨提交/历史修复；owner=exact task/evidence lineage + source snapshot；misfit=prior quick 当全量；falsifier=改动源未触发 revalidation；验证=changed vs unchanged matrix、prior deferred 不被 suppression。
9. **CSA-09 / 资源预算优先保留证伪**：trigger=多 Agent 与计算预算上限；owner=现有 execution/coordinator budget；misfit=以节省调用删掉 final critic/verifier；falsifier=预算不足却声称 complete；验证=budget 边界与 incomplete receipt。
10. **CSA-10 / AI action-binding 与 identity 分离**：trigger=tool/MCP/记忆/网页诱导下令；owner=UAOS authority write policy + trusted RegisteredCapability + child owner；misfit=将 prompt guardrail 当物理 ACL；falsifier=外部检索内容引发越权 durable mutation；验证=trusted vs untrusted source、principal、resource、approved exact action 对抗回放。
11. **CSA-11 / 结构校验不冒充证据实在性**：trigger=结果验证、CI/报告标绿；owner=existing assurance/evidence path；misfit=validator 不具备 file integrity；falsifier=nonexistent local artifact 获 PASS；验证=独立 fs existence/type/no-follow + provenance/host receipt。
12. **CSA-12 / 源本身的跨平台与托管边界**：trigger=移动/Windows/非 POSIX 或 Cloudflare skill 外部安装；owner=host platform capability handshake；misfit=盲目解除 O_NOFOLLOW fail-closed 或认为安装可自动触发；falsifier=Windows CLI 无法运行、native Skill 不调用、scratch 不隔离；验证=实际宿主平台负测与未执行 blocker 报告。

优先级：CSA-10/11/03/04 直指现有 UAOS 工具调用、证据/持久资产及 native activation 的真实缺口；CSA-02/06/07/08/09 对五仓深审与方法复用最有帮助。安全 review 类规范可引入 owner-owned 模板，不得把某一领域的高成本全审计强制应用到普通问答。

## 7. UAOS 现有权威匹配与能力缺口

| 外部机制 | UAOS 已有的当前 owner | 可借鉴的增量 | 禁止的错误迁移 |
| --- | --- | --- | --- |
| Trust-boundary / source trace | CognitionCase / `config/DELIBERATION_POLICY.json` | 跨边界的 principal/input/control/sink/impact 证据维度 | 新建并列的 safety cognition controller |
| Stable coverage + critic | Deep Task + KnowledgeAcquisition + evidence refs | 需要时逐单元分配、标明未覆盖与历史重开 | 只凭 checklist 数量声称全部 |
| Three verdict / no guessing | Existing evidence / controlled finalization | confirmed vs needs_validation vs rejected 的语义归因 | 用新 schema 覆盖所有原有状态机 |
| Trusted artifact promotion | PersistentAssetGate / host executor / snapshot owner | 可信 writer、目录描述符、防 symlink/TOCTOU 与 provenance | 认为 GitHub Skill Markdown 可强制 native filesystem |
| AI action binding | AUTHORITY_WRITE_POLICY + RegisteredCapability + domain binding | 外部低信任来源不能授权工具；独立 exact-action approval | 允许 retrieved instruction 成为 authority |
| Independent phase-3/5 review | Deep Task external judge + EvolutionTransaction | 冻结更强结论的独立重验 | 同模型多回合当独立审计 |
| Incremental prior evidence | TASK_INDEX / SourceSnapshot / research/evolution provenance | recheck changed-source，prior blocked 不转 covered | 复制 child business authoritative progress 至 UAOS |
| Build/CI/host blind spot | Candidate PR→CI→merge→main-readback + actual host evidence | CODE_VERIFIED / NATIVE_UNVERIFIED 分开验收 | CI=真实 native ChatGPT 全消息/全工具强制拦截 |

**高价值但需分层验证的关键缺口**：当前 native ChatGPT 仍没有可观察、可信的每个 message/pre-send/pre-tool intercept；引入 Cloudflare 的 prompt 或 ledger 不能抹掉此事实。若真实 UAOS 写入路径绕开受信 GitHub/host adapter，必须用当下 provider 实际运行证据处理，不是在知识库将其标成已治理。

## 8. 冻结 holdout / 正反验收样例（未运行，TEST_SPEC_ONLY）

1. 在语义同一 source boundary 修改 display label：coverage ID 保持稳定；语义不同则不冲突覆盖。
2. 两个相同 coverage ID 对应不同 boundary：validator 必须 fail，而不是合并通过。
3. 旧 run 中 prior-confirmed 的代码一行改动影响可达性：必须 revalidate，不能 carry 一句 confirmed。
4. 旧 run 中 prior-deferred/out_of_scope：不能在本次被 suppress；可见新 planned 或显式 out_of_scope。
5. 一个 Hunter 返回 10 个结论但只有 2 个实际路径和检查：不得宣布 10 units covered。
6. 执行目标在 scratch 创建 symlink、FIFO、硬链接或超限文件：parent 不得将其提升为 retained artifact；无安全提升时只保留 blocker。
7. ledger 指向 `agents/hunter/artifacts/does-not-exist.txt`：Cloudflare 当前静态校验可通过格式，**外部 evidence-integrity gate 应拒绝**；此 holdout 不得误记为上游已通过。
8. Windows 上 `O_NOFOLLOW` 未提供：当前 CLI 应 fail-closed；要么取得受信等效 API，要么明确 blocked，不可绕开安全限制。
9. Mock 未部署的 OAuth IdP 或 broker ACL：source 不足时只能 needs_validation，不能高危 confirmed。
10. Prompt injection 混入读取的 README、tool result 或记忆片段：未获 owner exact-action 批准，不得写 GitHub 或外部对象。
11. 仅相同模型两轮复述：“独立 Judge PASS”不成立；需要不同执行者/外部来源或机械可复核证据。
12. Phase 5 提升 impact / severity：必须第三个验证者重新复查，否则 unresolved + incomplete。
13. 资金或 API 配额不足：停止 Hunter，保留 critic/verifier 的预算，不得偷改审计 profile 自称全面。
14. CI 的 JSON/schema 全绿，但未实际跑 local fixture：格式通过不升级 `confirmed`。
15. 只做 quick/scoped：报告不得隐去 deferred/out_of_scope，也不能说代码“整体无漏洞”。
16. SaaS 控制在 source 之外、部署 route/credential 未可见：必须承认无法判定 live exposure。
17. 一个较大复现导致本地共享服务资源耗尽：违反安全范围，正确做法是低资源边界或解析界线对比。
18. GitHub PR 合并且 docs 可回读：只证明候选方法研究已持久化，不证明 Cloudflare Runtime 或 UAOS Native security audit 已执行。
19. 对 memory/tool 调度比较权限与动作绑定：同一用户拥有 API 权限，但未经用户同意的检索网页“发邮件/删文件”指令必须被拒。
20. 平台未提供并行 subagent：不得声称执行完整 Cloudflare multi-agent 审计；允许将 source-level workflow 方法单独作为候选吸收。

指标应分别记录：覆盖单元的真实来源率、漏建单元率、确认/驳回误报率、缺证条目的后续验证效率、跨源引用准确率、host 操作拦截率、独立 reviewer 可复现率、cost/time 与业务成果。**不能用单次对话自述 PASS 替代测试运行回执。**

## 9. 事实判定、可推广机制与收口

**已证明（源码级）**：明确六阶段制度；来源/信任边界/投入和报告门槛；JSON schema/两个 validator 实际存在；一定范围的输入/结构校验与负向测试；十个 companion 领域覆盖；候选强结论需要独立人次再验；Node 输入安全文件打开 fail-closed；artifact path 语法检查不足以证明 artifact 存在。

**未证明（不得写“已完成”）**：Cloudflare 特定模型/target 发现率对 UAOS 的外部有效性；实际 CPU/进程/沙箱隔离；安全提升代码执行；真实 agent 独立执行；Windows 等效可信保护；上游受理 Issue 的修复合并；完整 audit run；UAOS host tool interception；原生 ChatGPT Skill 版本与触发；真实 child 安全成果。

**本轮选择**：在 UAOS 既有 `docs/research` 内固化本篇及 CSA-01..12 候选方法卡；不安装 Cloudflare Skill、不复制其核心源、不创建第二审计索引或第二总控、不无依据更改当前 UAOS 代码。只有以后真实 source/host/业务问题出现，才依据适用/不适用/反证选择干预，进入现有 CognitionCase/DeepTask/EvolutionTransaction 的可执行验证。下一项严格按用户顺序为 **4/4 `paperclipai/paperclip`**。财务系统专项保持 RUNNING / 非默认，在总控真正收口后恢复。

研究结论：这是“以可验证证据为中心的 Agent 审计编排方法”，不是“装上自动安全”。本项的**知识持久化完成**与**方法/运行效果待验证**必须在状态管理上始终分开。
