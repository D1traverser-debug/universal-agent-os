# 13 — Orca 多 Agent 执行协调：源码级学习、机制蒸馏、反证和 UAOS 适配

研究对象：stablyai/orca（用户截图 2/4 项）。源版本：main commit c7942252b58bca576867ca77f14908519e9a6702（2026-10-19 检索）；权威 owner：UAOS controller；唯一进度：state/tasks/uaos-inheritance-review-20261018.json。
状态：SOURCE-STUDY / CANDIDATE KNOWLEDGE / NOT DEPLOYED / NOT UAOS-RUNTIME-VERIFIED。
本资料放在 UAOS 既有 docs/research 中，属于外部方法证据，不构成独立的调度中心、执行主机、任务索引、分布式锁或授权层。用户要求逐项学习，尚未研究截图第 3、4 项。

## 1. 问题、对象与来源充分性

Orca 自称并在源码中实现编程 Agent 的工作环境：桌面 IDE + 多 Git worktree + Agent CLI/会话终端 + 可选监督协调 Run/Task/Dispatch + SSH/Remote Orca Server + 移动配对/云端 Relay + CLI Skill/自动化。它不是一个能仅凭安装 SKILL.md 就运行全功能的 Agent 内核。Orca Skill 入口明显说明：skills/orchestration/SKILL.md 是发现入口，真正的操作说明需通过当前实际二进制的 skills get orchestration 动态读取；版本不匹配不能安全猜测 API。研究本身没有启动 Orca 二进制、真实 Agent、远程 relay 或移动设备。

本轮根目录树中 38,335 个条目，37,448 个 blob。以源码职责轴、任务/身份/持久化轴、远程/恢复/安全轴、核心正反测试、外部专业安全方法轴取样，而非自称逐行审核全部。即便浏览了源码，也不能替代经过运行的契约测试、集成/并发现场观察或真实用户成果评估。

### 原始来源表

| 角色 | 冻结来源 | 核验重点 |
| --- | --- | --- |
| 产品、范围与许可证 | [README](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/README.md); [MIT](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/LICENSE) | 多模型终端、Workbench、SSH、CLI、移动端、适用平台；MIT 许可不等于自动可控授权 |
| 版本匹配 Skill | [orchestration SKILL](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/skills/orchestration/SKILL.md); [orca-cli SKILL](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/skills/orca-cli/SKILL.md) | 二进制决定当前命令语义；supervised 和 handoff 分工；不是凭发现 Skill 就能操作 |
| 完整业务契约 | [orchestration guide](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/skill-guides/orchestration.md); [worker contract](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/skill-guides/orchestration/references/worker-contract.md); [recovery guide](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/skill-guides/orchestration/references/recovery-and-cleanup.md) | 活 Dispatch 代表完成权，消息处理和 ACK，超时/未知状态不重复创建任务 |
| 工作空间模型 | [worktrees](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/docs/site/content/docs/model/worktrees.mdx); [parallel recipe](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/docs/site/content/docs/recipes/parallel-agents.mdx); [Git official worktree](https://git-scm.com/docs/git-worktree.html) | 任务独立 checkout，仍共享底层 Git repo common dir；不能称为容器级沙箱 |
| 状态/协调运行时 | [coordinator](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/coordinator.ts); [worker settlement](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/db/dispatch-context/worker-report-settlement.ts); [dispatch completion](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/db/dispatch-context/dispatch-completion.ts) | 完成需精确 Task+Dispatch+有效身份；事务、去重、失败和回收属于不同边界 |
| 多消费者与联邦 | [mailbox consumer](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/db/messages/mailbox-consumer.ts); [federation observation fence](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/db/federation/federated-dispatch-observation-fence.ts); [remote relay import](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/db/federation/federation-relay-import.ts) | 同一消息的消费 generation，epoch 和序列检查，拒绝跨时期旧观察和乱序远程回报 |
| 失败/恢复负向测试 | [mailbox fence test](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/db/dispatch-mailbox-consumer-fencing.test.ts); [federation fence test](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/db/federation/federated-dispatch-observation-fence.test.ts); [report settlement tests](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/worker-dispatch-settlement.test.ts) | 陈旧 worker ACK 被拒；跨 epoch 观察被拒；重复与失效完成不重改当前任务 |
| 故障与真实工作区测试 | [startup breaker test](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/db/worker-dispatch/failed-start-circuit-breaker.test.ts); [real-git deletion test](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/git/worktree-removal-real-git.test.ts); [repair matrix test](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/worker-dispatch-repair-safety.test.ts); [terminal census loss test](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/coordinator-terminal-census-unavailable.test.ts) | 启动重试预算、实际 Git 删除副作用、45 种状态组合幂等修复、未知终端时不重复启动 |
| 宿主与远程 | [remote servers](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/docs/site/content/docs/remote-servers.mdx); [SSH](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/docs/site/content/docs/ssh.mdx); [cloud relay](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/cloud/README.md) | 进程在执行端而非 UI；失联不能等同退出；移动中转 relay 并非授权权威 |
| 治理反例 | [agent sessions](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/docs/site/content/docs/model/agents-sessions.mdx); [stale base parser](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/coordinator-stale-base-flag.ts); [decision gate code](https://github.com/stablyai/orca/blob/c7942252b58bca576867ca77f14908519e9a6702/src/main/runtime/orchestration/coordinator-decision-gates.ts) | 默认跳过多种 agent 审批/沙箱；自由文本开关污染；显式决策门禁与状态标志不是同一物 |
| 外部专业检验 | [Kleppmann fencing](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html); [OWASP LLM06](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/); [Git worktree](https://git-scm.com/docs/git-worktree.html) | fencing 只有资源接受写入时检查旧 token 才有效；Agent 过度权限风险；worktree 不是权限沙箱 |

## 2. 从界面产品到实际执行系统：层次区别

1. Visual workbench：终端、多工作树、会话面板、编辑器、Git/Issue UI、Agent 状态投影。
2. Execution host：本地/远程主机实际运行 agent CLI 和 PTY，身份/进程/会话在宿主，不在某个移动设备的卡片。
3. Orchestration：Run 是持久命名空间和 coordinator inbox；Task 是任务定义和 DAG 节点；Dispatch 是 Task 的单次可计数执行尝试，直接绑定实际 worker/终端的完成与心跳权威；Message 是独立可确认投递；Decision Gate 是带任务和有效请求者身份的等待批准阻塞。
4. Transport：SSH/remote server/cloud relay/mobile 解决连接和传递，但通信活跃度不等于任务完成，也不替代核心所有权。
5. Skills：可通过 CLI 取得和二进制版本匹配的指南；只是调用方式，不是后端真实执行成功与权限证明。

重要区别：Run 本身不会自动调度执行，不应把 Run ID 当已创建 worker；Task completed 与 Worker process exited 不是同一事件。尤其源文件 worker-dispatch-settlement.ts 明确只修复 assignment bookkeeping，不声称物理进程已退出，也不等于可删除终端。

## 3. 十项可迁移方法与真实测试对应

### O1 结构化身份：Run / Task / Dispatch + attempt identity

同一 Task 可有失败重试，每个 Dispatch 单独记录执行尝试和其特定 worker/process/session 身份。worker_done 需 taskId、dispatchId、实际发送者 provenance；提交完成需还检查任务是否已经 settled、是否存在冲突的活跃 dispatch。拒绝 stale_dispatch、inactive_dispatch，并对合法重复结算返回 duplicate 等语义。这个结构避免“一个终端回复说完工了”就覆盖其他 Agent 的当前任务状态。
证据：worker-report-settlement.ts、worker-contract.md、coordinator.test.ts。

UAOS fit：当前已有 task index、ActionCoordinator ExecutionRequest、Action/UNKNOWN 及 EvolutionTransaction，但 ChatGPT 当前 GitHub 会话并没有受控的 Orca dispatch runtime。方法适用于未来有多个真实并发 Tool/Worker 回传的宿主；不能直接把一个新的 Run/Dispatch 总库另建在 parent 或 child 旁边。

### O2 竞争方案隔离：独立 Git worktree，再审查/选择

Orca 的平行模式把相同任务发到不同 Agent 的独立 checkout，diff/检查后选优胜，再 PR；支持开始 ref、关联 issue、多分支工作流。适合代码实现比较、互不影响的不同 PR 或受控 A/B 方案。官方 Git worktree 文档说明不同 checkout 共享 git common dir、对象库/部分 refs；Agent 在同一宿主的 shell、凭据和网络仍可能共享，worktree 不是容器、ACL 或恶意代码执行沙箱。sharedDirectories 甚至会显式共享忽略目录，不能盲目认定无数据竞争。
证据：worktrees.mdx、parallel-agents.mdx、worktree-removal-real-git.test.ts、git-scm.com 官方文档。

UAOS fit：已有 GitHub candidate branch → PR → CI → merge → main 回读；本会话并无同机多个独立 CLI worktree。可以学习独立方案比对/真实差异验证，但不可声称 GitHub branch 本身可防止多个 worker 同时写入同一外部资产。

### O3 真正的完成权来自活 Dispatch，不来自界面标题

Orca 文档明确状态图标可由 OSC title/Agent hooks 获得；这是观测/UX 信号，不是可信完成裁决。只有符合身份和生命周期门禁的 worker_done 报告能 settlement。源文件 coordinator-decision-gates.ts 还对请求者的 task/dispatch provenance 验证；非法伪造另一个 Dispatch 的门禁被测试拒绝。人类批准/decisions 不由协调器代替回答。
证据：agents-sessions.mdx、coordinator-decision-gates.ts、coordinator-decision-gates.test.ts、worker-report-settlement.ts。

UAOS fit：模型回复“已经完成”、GitHub 单次 CI success 或外部截图上的绿色点都只能作为一条来源证据，不得覆盖实际主分支/原业务验收状态；写入必须仍通过当前的 owner/approval/mutation admission。

### O4 Mailbox ACK generation / fencing：旧执行者不得确认新执行者的消息

db/messages/mailbox-consumer.ts 在消息交付事务中核对 runId、source 和 consumer generation；test dispatch-mailbox-consumer-fencing.test.ts 中旧 worker A 和新接管者 B 的 generation 不同，A ACK 被 consumer_fenced 拒绝，B 保留未读消息；retry Dispatch 获得新 mailbox 地址。
这比“重试时看一眼是否还在线”强，因为每次交付结算检查身份版本。

外部 Kleppmann 进一步强调 fencing token 必须被实际资源写入端拒绝旧 token，只有协调库里 generation 加一，**不能自动阻止已经逃逸到 GitHub/外部 API 的旧执行者继续改文件**。因此若转化为 UAOS 方法，要在受信 provider/tool adapter 写端验证，而不能只在状态记录表里发一个新整数。

### O5 远程安全：Live / Unverifiable / Exited 是有证据界线的互斥判断

remote reconnect 与 Worker 生命周期分层。网络断开时任务可能仍在主机运行；要从真实执行主机读取证据才可证明退出、授权重试或清理。recovery guide 明确缺少联机证据时只可继续查证，不能默认 stop、abandon、retry、release；terminal census 不可用测试证明暂缓 dispatch，不创建第二个 worker。Release 只应在确认 worker_done settled/实际后续 owner 接手后操作。
证据：recovery-and-cleanup.md、ssh.mdx、coordinator-terminal-census-unavailable.test.ts、remote-attachment-liveness.ts。

UAOS fit：一次外部工具超时、主对话连接中断或 provider 状态未知必须进入 UNKNOWN/Reconcile，不得从「未收到回答」推断动作没发生，然后重试创建相同外部资源；已有 ActionCoordinator.reconcile 是当前 owner，不能新造 recovery coordinator。

### O6 联邦消息：顺序/epoch/消费者身份同时校验

federation-relay-import.ts 明确在 BEGIN IMMEDIATE 内检查 to_home_imported_sequence，要求连续序号，重复序号须有对应消息记录；不连贯则 operation_unknown。federated-dispatch-observation-fence.ts 记录跨主机 epoch、终端、当前 Dispatch/Task/Worker 快照，再在事务中对比，避免网络慢回包修改最新 owner 的状态；专项测试对旧 epoch 和释放前观察做了负向验证。

UAOS fit：跨 Gmail/Drive/GitHub/第三方 connector 的回执若缺 provider-side identity/operation id，无法从“工具回复成功”合成统一原子事务；应保留 provider refs、版本、unknown，并在已受控的工具路由层逐个核对。单个 GitHub repo CI 不证明所有 native ChatGPT connectors 拦截/超时重试安全。

### O7 Circuit Breaker：失败有预算但归因必须精确

failed-start-circuit-breaker.test.ts 模拟 Agent 在交互界面启动失败，第三次同一 Task 尝试失败后阻断第四次重复启动；测试也覆盖迟来的 worker 报告能否纠正记录。未启动失败和 worker 自己正常执行后报告失败不应盲目累加成一个指标。真正进化不只是“重试三次后提示用户”而是区分 provider 输入、CLI readiness、鉴权、业务失败和执行副作用。

UAOS fit：目前路由层也有 capability circuit breaker；可以迁移“失败类型分离 + 不导致外部副作用的重复尝试 + 带运行回执的恢复判决”。**不得**将“用户重复指出问题三次后才升级”当自治治理的入口，更不能把等待用户纠错作为失败发现器。

### O8 Decision gates / DAG：阻塞条件是状态约束，不是文案

Task 可依赖先行任务；并行仅适用于真正独立节点。人工选择和授权通过 Decision Gate 形成结构化阻塞，协调器不会自动批准；决定后才允许继续。它是一种编排机制，非所有工作都要分 DAG。decomposition 的有效性须由产物依赖/冲突和 owner 可观测性判断。

UAOS fit：只对有明确跨 repo 依赖、验证义务或外部审批的场景考虑 DAG；当前 controller 和四 domain 的 Authority / stage / task 仍由原来的 owner 维护，不扩建第二个总控调度器。

### O9 Cleanup 与持久化：完成回报不直接执行销毁

worker-release 有资源归属与档案保存；active/unknown worker 不可仅凭 UI 消失、自动归档或过期状态就删除。真实 Git 删除前检查 dirty checkout、submodule、branch registration；real-git test 覆盖“删除本 checkout 不影响 sibling”、拒绝 dirty checkout、恶意/错误 registration 等。worker-dispatch-repair-safety.test.ts 枚举 45 个状态组合并检测幂等、事务回滚、旧记录恢复及大量历史记录处理。

UAOS fit：复制其「确切 object identity → 生命周期候选 → 变更前复核 → 负向删除试验 → 操作后回读」，但本系统已有 PersistentAssetCatalog/PersistentAssetGate/MutationContract；不能通过引入 Orca 删除工具来绕过它们。

### O10 指令与配置版本：Skill 与 binary 版本配对，文字状态不得变成权限

技能文件是 discovery stub，明确需从当时真实 Orca 二进制取得 version-matched guide。动态加载实际环境比旧 SKILL 静态拷贝安全，至少能够减少文档/命令漂移；但是能读到指南不等于宿主自动强制执行，且 provider 权限仍要显式检查。

特别发现 coordinator-stale-base-flag.ts 使用多行正则从 Task spec 正文识别 allow-stale-base: true；源码注释承认它可能命中 fenced code block，导致故意 fail-open 的工作流。**因此不要照搬“自然语言中的貌似配置字段=治理授权”设计。** 即使选择兼容的 CLI，必须将控制字段从不可信长文本中独立结构化，并测试 prompt injection / quoted-example / code block 的 negative cases。

## 4. 安全与运行边界：明确不适配的设计

1. 高权限启动：agents-sessions.mdx 明确说明默认 Agent launch 使用 Claude --dangerously-skip-permissions、Codex --dangerously-bypass-approvals-and-sandbox、Gemini --yolo 等，全权运行意图依赖 worktree 作为所谓 sandbox。对受限资产而言，这是功能性取舍而非完整安全控制。OWASP LLM06 明确过度功能、权限、自主性会放大间接注入风险，建议最小权限、服务端审批/细粒度工具。UAOS 不能复制默认跳过审批的设置。
2. 实验性质：Orchestration 文档标注 Experimental，启用后需运行时 Orca CLI，旧 run/run-stop 入口无效。不能把文档列出的所有命令当稳定平台 API；要读取版本匹配命令和能力后再执行。
3. 并行不是科学共识：在多个代理相同回答中得到一致答案，最多提高关注优先级，不是独立 ground truth。受相同模型数据、提示词偏差和同一错误来源影响，一致结果可同时错。需要外部 evaluator/holdout 与工具/用户验收。
4. 资源争用：不同 worktree 共享 common git dir、外部帐号/token、系统内核、缓存、可能被共享的依赖目录。隔离 checkout ≠ 隔离工作账户、网络、进程权限；并发修改同一 API 资产仍需写入端版本/租约控制。
5. 安全数据：云 relay 和 remote server 提供多设备接线但也扩展访问面，必须在真实主机采用窄授权和凭据控制；不能因为出现配对 UI 就声称 E2E 安全、业务数据天然不流出或插件受到物理拦截。
6. 用户可见状态：Agent 面板中的状态 glyph、readiness、idle 依赖 hook/OSC/PTY 检测，有盲点。最终任务完成只能由可信 owner 成功判断和结果 V&V 验证。
7. 实验范围不足：只进行了源文档/实现/测试审阅；未安装运行二进制、启动容器、真实 SSH 复现、真实 CLI provider 调度，也未验证 native ChatGPT 的外部工具权限拦截。此研究阶段可以存为候选知识，但不能宣称 UAOS 获得 Orca 的实际多 Agent 执行能力。

## 5. 源级可信度与外部独立理论对照

Orca AGENTS.md 是其仓库贡献者规约，不是 UAOS 的执行指令。该文档明确要求 worktree safety、remote host ownership、Git 2.25 compatibility、真机运行验证、远程 unavailable 不等于死亡，以及仅在 exact PR head 的完整 aggregate CI success 后合并。这些说明项目关注多平台一致性和真实行为，但仍不是独立证明所有路径没有漏洞。

Kleppmann 的 fencing token 论证：https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html 。对 Orca 邮箱 generation 测试的真正迁移是：令资源消费端拒绝 stale generation，而不是只用 lease 心跳显式标记“我还是 leader”；遇到外部 tool 侧无 fencing 接口时必须承认保证未建立。

OWASP LLM06：https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ 。对 Orca 默认全权启动模式的真正迁移是反向边界：最小权限、缩小通用工具操作面、按用户或 owner 身份实行真实授权、对高冲击写入实行必要审批，避免 agent 因意外/不可信输出造成不可逆副作用。

Git 官方文档：https://git-scm.com/docs/git-worktree.html 。多个 checkout 的真正隔离是工作目录和部分 Git worktree 私有 metadata，而非所有仓库 refs、认证凭据、文件外部资源或 OS 进程。不能用“worktree-native”推导完整权限隔离。

## 6. UAOS 当前能力对照（不新增治理中枢）

| Orca 机制 | UAOS 已有 owner | 应蒸馏的能力 | 非适用 / 禁止 |
| --- | --- | --- | --- |
| Run/Task/Dispatch | TASK_INDEX / exact state / ActionCoordinator | 每一次外部执行尝试与原任务分离，精确身份与回执 | 新建第二套 UAOS TaskRegistry/Run DB |
| Worker_done settlement | ActionCoordinator + approvals + owner V&V | 只有可信执行回执+task/attempt 对应且无更新的冲突 attempt 才结算 | 接受聊天“成功了”、UI 绿色状态作为业务最终验收 |
| Consumer generation & federation | Trusted mutation contracts / UNKNOWN reconciliation | 不可让旧执行者延迟回包覆盖后来的状态；写入端需要 fencing | 单靠状态中加 generation 证明 native provider 阻断旧写 |
| Worktree parallelism | GitHub candidate branch / PR / CI / main reread | 独立候选干预、多方案比较与反证 | 把分支等同同机安全沙箱或全局资源锁 |
| Remote liveness | ActionCoordinator UNKNOWN + provider receipts | unreachable / unverifiable / exited 明确区分，缺证不得重试破坏 | 断线=没写入=重新创建 |
| DAG/Gate | Current Cognition/Deep Task/Evolution and approval owners | 真依赖的多阶段任务、批准阻塞与结果 V&V | 所有简单任务过度编排或 parent 代 child 写业务状态 |
| Clean release/delete | PersistentAssetCatalog + asset lifecycle | 拥有者证明、真实 Git/Provider 删除前检查，后验复核 | 未知执行状态时释放资源/删知识 |
| Binary-matched skill | NATIVE_SESSION_RUNTIME_PROFILE + owner binding | 运行指南与受控宿主版本同步，避免静态 Skill 漂移 | 外部 SKILL 授权升级为 UAOS policy |

治理上应继续坚持：存在仓库代码/Skill 机制，不代表当前原生 ChatGPT 自动触发或 non-bypassable enforcement。能运行受控代码再评估启用时机，不复制另一套完整 Orca。

## 7. 九张候选方法卡（全部 CANDIDATE，非 Canonical）

命名 ORC-01 至 ORC-09；每张卡未来进入正式 KnowledgeItem，必须保留 source commit、source ref、applicable_scope、trigger、misfit、falsifier、owner、V&V refs。当前没有真实通过的 usage_links。

- ORC-01：任务与单次执行尝试双重身份。触发：重试、远程回调、多 Agent 并行；反证：旧 worker_done 能终结新 attempt；owner：ActionCoordinator / exact task。
- ORC-02：接管后过期消费者封锁。触发：多客户端 mailbox 或 worker reattach；反证：旧 generation ACK 令新 worker 丢消息；owner：消息 adapter 的真实接收端。
- ORC-03：Live/Unverifiable/Exited 判定。触发：断线、超时和外部 UNKNOWN；反证：断线时重复发外部写并造成两个资产；owner：ActionCoordinator.reconcile。
- ORC-04：外部写入端 fencing。触发：远程并发或 provider 可能接收迟到写；反证：只有状态表做 fencing，但旧 token 仍能写 provider；owner：trusted connector adapter，缺接口则 UNKNOWN。
- ORC-05：独立 worktree 候选和真实 Git 资源生命周期。触发：并行方案比较；反证：共享外部资源/凭据冲突，dirty 工作树被删除；owner：GitHub PR / asset gate。
- ORC-06：ACK 后结算、可恢复投递。触发：异步消息重发和发送者宕机；反证：ACK 发生前只处理部分消息，重复/丢失无法重放；owner：host mailbox adapter。
- ORC-07：DAG/决策门禁 + 明确执行授权。触发：真实前置/审批关系；反证：来自非当前 Dispatch 的请求打开其他任务门禁；owner：existing approval gate。
- ORC-08：失败类型分离及有限重试。触发：Agent 无法启动或反复同因执行失败；反证：超时/没检测到就自动重复产生并发实例；owner：CapabilityRouter/CircuitBreaker。
- ORC-09：Skill-binary 版本一致与自由文本控制位负向检验。触发：外部命令语义变动、Markdown 中伪配置；反证：引用代码示例中的 allow-stale-base 值被当作真实授权；owner：runtime profile / trusted structured admission。

候选知识价值评估：ORC-01/03/04/09 与现有 UAOS 的真实未验证边界高度相关；ORC-02/06 只有在确实启用持久消息多消费者环境时适用；ORC-05/07/08 很多原则已有受控代码，建议用负向实测检验是否已达标，不要继续堆重名机制。

## 8. 冻结反证/验收场景（未执行，TEST_SPEC_ONLY）

1. 旧 Worker A 对 Task1 的 Dispatch1 完成回报晚于 Dispatch2 激活：必须不能更改 Task1 的新事实。
2. Worker 进程真实结束但终端 PTY 仍活：不得把终端活跃等于 Agent 持续运行；需来源级区分。
3. 远程 provider 回应丢失但操作实际写成功：必须先 reconcile，重复 CREATE 不得产生第二个持久资产。
4. 消息交付后未 ACK 主机崩溃：恢复可重放且不重复结算任务。
5. 接管新消费者 B 后旧 A 的 ACK：必须拒绝旧世代，B 的消息仍未读。
6. 多主机旧 epoch 的 heartbeat/worker_done：必须拒绝更新新 epoch 状态。
7. 支撑发布的必要审批未解决：即便 DAG 其他任务完成也不得发布。
8. 两个 worktree 并行调用同一个外部删除接口：不能因为 git checkout 隔离就放弃 owner/asset gate。
9. 文本中引用 allow-stale-base: true 作为样例：不得变成真实允许过旧代码的命令。
10. Agent 反复启动失败：有限尝试后阻断无意义重试，但仍保存异常回执和人工可恢复路径。
11. 正确 PR head 下 CI success，但远程 host 没执行 final output guard：判 HOST_UNVERIFIED，不得转 NATIVE_PASS。
12. 用户实际业务成果：必须检验 child 原权威、最终产物质量、审查与工作结果，而非仅记录多个 Worker 的 done 报告。
13. 缺失 CLI binary/版本冲突：Skill discovery 不等于执行能力，系统 fail-closed 不猜命令。
14. 删除工作区：dirty/submodule 或非 owner 目标应拒绝删除且不损坏 sibling。
15. 历史修复重放：对多个生命周期组合做 recovery 幂等与滚回，不允许误写正活跃 worker。

未来可以采用独立 holdout 指标：身份误归属率、重复外部副作用、失联假死亡率、丢/重 ACK 率、已阻塞越权率、错误删除率、owner 过界率、CI 与实际执行分层一致性、尾延迟和成本。要和 UAOS 当前 exact task + GitHub CI + ActionCoordinator 的基线比较；不能凭文档宣称实验通过。

## 9. 方案比较与当前选择

A. 把 Orca 直接当 UAOS 的新全权控制器：放弃。新建立调度主权、需要本地/远程 binary/凭据/全权限启动、与 ChatGPT 工具和父子权威不兼容，未验证真实痛点属于缺失 Orca UI；对安全/运维成本不划算。
B. 在 UAOS 已有研究资料里保存来源固定、对照明确且可反驳的方法；未来在现有 ActionCoordinator/host adapter/资源权威上做独立负向 V&V。选定：不增加另一运行总控，保留已被测试的机制的 fit/misfit 和来源，验收用例由原治理任务管理。
C. 不学习：作为对照基线，可能重复发生旧 worker 覆盖新任务、断线重复执行的未知风险。
D. 仅引入 worktree UI：若未来有受控多 agent code 修改需求可以作为工具候选，但用户并未要求安装/使用，不得主动切换工作流或导出敏感仓库。

来源自信边界：产品/源码/专项负向测试/独立公开工程方法相互支持其设计意图；并未重跑 Orca 3.8 万条树的所有测试、全平台真实运行、权限穿透或联邦故障现场，故本轮仅到 SOURCE-BOUNDED CANDIDATE，不是 Orca 架构完整形式化证明、更不是 UAOS 多 Agent 主机部署结果。

## 10. 下一步与跨技能连续性

第 1 项 Hindsight 的 HIN-01..07 解决「记忆与知识证据的来源/撤回」。本项 ORC-01..09 解决「任务尝试/执行身份、分发、接管、确认与失败恢复」。两者可在现有 UAOS CognitionCase/ActionCoordinator/KnowledgeItem 之间互补，但不能令 Hindsight 的知识 Page、Orca 的 Task/Dispatch 和 UAOS 的唯一控制 authority 三套实体互相冒充。

本项合并完成后，以本研究资料和同一 exact controller task 作为持久证据。依截图顺序才进入第 3 项 cloudflare/security-audit；第 4 项 paperclipai/paperclip 仍未学习。学习研究完成不代表实际把 Orca 安装在 ChatGPT，本仓库也无法从 GitHub CI 证明 Native hooks/agent 宿主全链路治理完成。
