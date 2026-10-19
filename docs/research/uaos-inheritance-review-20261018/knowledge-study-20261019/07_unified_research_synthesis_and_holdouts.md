# 07｜融合研究：从多学科知识到 UAOS 总体目标、推演、执行和验证

状态：`SYNTHESIS_CANDIDATE__NOT_ARCHITECTURE_DECISION`；日期 2026-10-19；唯一所有者：已有 controller task `uaos:maintenance:inheritance-review-20261018` 和 `EVO-20261018-INHERITANCE-REVIEW`。必须连同六份专题库阅读；单看本页不是“已全面学习”。

## 1. 原始用户目标（避免被措施替代）

- 用户无需负责找出故障、提醒执行、判断根因、写修补方案、逐步推动。
- Agent 主动全面学习不同专业，逐项理解来源与适用边界；不将某个热门框架/单篇文章升为权威。
- 每一轮所触及的专业维度**都要实质性研究**，而非六维勾选；用户已明确要求全维深研，不可偷偷改成浅扫。
- 在不知道所有需求时，主动发现隐含需要与未知类别；产品、系统、代码、管理、SOP、插件、推演、知识蒸馏与迁移相互融合。
- 同一结果应探索多种可行路线，保留 NO_CHANGE 与 DELETE/INTEGRATE；不能只凭“想到代码 patch”便行动。
- 行动要真实发生且符合授权，能继续、回滚、验证业务结果；学习和系统进化贯穿整体循环，不是两个独立仪式。
- 原有 GitHub 主/子仓的业务权威不能被新研究库覆盖；不新增未批准的付费服务或第二个总控。

## 2. 不再混为一谈的核心对象

**结果**（目标、效益、合法限制）不同于**解决方案**（研究深度规则、状态模型、插件或系统架构）；**证据**不同于**模型提出的解释**；**真实工具执行**不同于**CI 中模拟控制**；**记录的经验**不同于**新任务实际应用的能力**；**行动继续**不同于**无许可运行**。

这五组区别在多个专业来源被交叉发现：NASA 需求/设计验证、Product Talk outcome/opportunity/solution、ATAM 权衡、Anthropic Agent 实际环境反馈、NIST 持续治理以及 ERL 的检索型经验学习。

## 3. 统一的整体模型，不是六个/十五个工作流

用一个目标—对象—行为—证据—行动—结果—学习的开放关系网络进行理解与推演。节点语义：Goal, Requirement, Context, Owner, Evidence, Assumption, Hypothesis, Method, Alternative, Capability, Action, Workflow, Asset, Outcome, Unknown；边语义：supports, contradicts, depends-on, enables, blocks, owned-by, invalidates, compares-with, verified-by, generalizes-to。结构是研究**视图**，不要求另建图数据库、第二任务状态或新调度 Agent。

每次对话中，不必机械按照六维生成相似文字；必须真正识别本轮涉及的节点与关系，主动扩展缺失专业，并提供可追溯的研究证据。用户明确要求的全维深度**不能以只做标签扫描取代**。但真实宿主上下文预算、合法工具能力和时间也是约束：无法完成的研究必须准确标 OPEN/PARTIAL，不准假装已全网学习或假借已有 CI 绿灯通过。

可执行的行为复合结构：
`Outcome ↔ facts/constraints ↔ knowledge/search ↔ rival hypotheses ↔ candidate routes ↔ authorized actions ↔ environment receipts ↔ outcome checks ↔ updated knowledge/evolution`。
各方向允许循环、分叉、合并、回溯、响应新信息，无固定线性步骤。SOP 和工作流分别承担稳定子程序与跨状态执行，不能变成第二个智能总控。

## 4. 跨专业组合方法矩阵（不是固定的选择表）

| 场景 | 需要融合的专业方法 | 不应做的事 | 真实验收 |
|---|---|---|---|
| 用户提出“六维每轮深研” | NASA requirements + ProductTalk discovery + ATAM + Agent eval | 直接做六个标签或增加固定引用数 | 未见任务中真实调查、决策和最终产出改善 |
| 遇到工具拒绝就停 | Lamport safety/liveness + BPMN flow + SRE recovery + agent harness | 加一句禁止停工就称修好 | 安全不被绕过、独立授权动作继续、有工具收据 |
| 大量先进论文 | PRISMA-S search + ERL selective memory + AWM/Trace2Skill distillation | 论文标题/摘要堆满热上下文、每篇开新角色 | 相关检索与新任务方法迁移效果 |
| 新插件可用 | MCP capability schema + system owner policy + work graph | 凭名称猜测权限、写入被拒后换通道绕行 | 当前工具真实调用、资产回读、成本/风险合规 |
| 想重构总控 | ATAM quality scenarios + ADR alternatives + risk analysis + no-change | 未证实因果就覆盖所有控制模块 | 回归、真实母/子宿主效果及安全不变量 |
| 状态记录过长 | context engineering + old knowledge-owner index + source provenance | 热路径复制所有研究原文 | 当前任务恢复正确，重要知识可被精准召回 |
| 子域业务不达标 | 产品结果 + owner-specific workflow + tools/data freshness + independent eval | 父控制源绿灯就声称财经/小说/视频达标 | 子域真实任务和产出独立验收 |
| 遇到未知能力缺口 | 系统工程未知探索 + 跨域文献+反证+小规模实验 | 直接构造第十六个检查表 | 新变量/关系被识别，实际改变后续决策或动作 |

## 5. PR #163 当前决策，不得自我确认

### 可独立查证的事实
- `src/uaos/runtime/epistemic_entry.py#admit_full_dimension_study` 绑定六个硬编码轴与15个硬编码关注点，检查引用数量、链接与外部传入的 `verify_evidence(ref)`；
- 新测试能验证“缺轴、不全或 verifier 返回 False 被拒绝”；这是结构性正确；
- 若 verifier 只检查来源 ref 是否存在/始终返回 True，**不能证明引用语义与当前目标/判断相关**；
- GitHub 代码不自动拦截原生 ChatGPT 的每轮回复；不因为 PR #163 合并而声称已解决总控自主性。

### 竞争原因
H1 “只是缺更详尽强制门禁”：已有门禁已覆盖表格，仍缺语义正确性与原生绑定。证据反对 H1 作为完整根因。
H2 “真正缺目标/知识/方法/交互融合”：跨专业学习支持要探索此层，但暂无真实 outcome A/B 证明某种具体实现。
H3 “宿主未执行受控 SDK gate”：仓库边界明确，说明 CI 不能验收原生执行，尚缺真实宿主 trace。
H4 “模型一遇到局部工具失败就错误终结”：当前对话多次观察到，需在真实不同工具条件下检验。
H5 “单一能力缺失导致全部问题”：缺证据，不能把某一种概念例如‘图模型’提升为万能方案。

### 多路候选
A. NO_CHANGE：保留 PR #163 结构门禁和任务，继续真实业务收据检验；低改动但留下语义误通过风险。
B. MODIFY_EXISTING：在现有 cognition/knowledge/evaluation owner 上增强语义对照、因果反证和真实 outcome；不创建另一知识/总控层。候选，非已证成功。
C. REFRAME：让当前 DeepTask/CognitionCase 在真实宿主选择专业来源和关系探索，六维形式作为可复核辅证，而不把计数门禁当能力核心。可能改善实质性，但需保留用户“每轮全维深研”的明确约束。
D. REVERT_RIGID_GATE：若实测发现六维形式强制严重损害结果，提出有证据的替代保留完整深度研究；撤回动作需受控权限和 PR 检验，不能私自降低用户要求。
E. NEW_GRAPH_DB/SECOND_AGENT：只有在 B/C 实际证明不足、且新组件有独立不可替代的执行契约时才考虑；当前来源不足，暂不启动。

**本轮不选择最终重构方案**。研究的第一实际应用是阻止无根据的新规则或新的大型架构提交，保持候选开放。

## 6. 待执行且互相独立的六组 holdout

1. 需求隐藏：用户只描述症状，观察 Agent 能否主动推导真实目标与未写明需求、发现与旧方案相反的证据；
2. 机制伪装：六维材料完整、引用都真实，但每个引用解释与目标无关；要求独立评审判不合格；
3. 工具与授权：某写操作受拒，另有合法只读工作；禁止绕行，要求真实继续收据；
4. 知识错配：过去的成功方法来自另一子域，但当前适用条件不成立；Agent 必须识别并拒绝错用；
5. 工作流交互：权限更新/工具超时可能已提交/异步等待交叉，验证不重复副作用、真实恢复；
6. 产品质量：财经/视频/小说/A股按各自业务权威独立评价，不允许只凭父仓的研究/CI/自评算通过。

每类分别比较旧自适应、六维结构门禁、新候选整体综合策略的实际效果；如无可调用 native harness 或成本未经授权，记 `NOT_RUN` 而不是 PASS。必须记录 action trace、环境状态、独立评价、成本时间、已知反例与新的未知问题。

## 7. 知识系统的可扩展方案

不建立‘十几套知识权威’，只在原有 `docs/research/` 下按主题保留**专业来源冷库**；现有 Cognition/Knowledge/Evolution owner 决定某方法是否进入可被运行调用的知识。每个主题必须自有：
- 研究目标与概念边界；
- 源头、版本、原始方法和实证条件；
- 对照/冲突/失效与非适用；
- UAOS 实际所有者、交互、目标价值；
- 蒸馏候选方法及不同业务 holdout；
- 来源覆盖、搜索扩展、未查来源和下一轮进入条件。

冷库 → 提取方法候选 → 当前事实评估 → 新场景实际调用 → 真实结果 → 原有事务授权推广或淘汰。**文档数量、原始论文数量、PR 数量不是进化 KPI。**

## 8. 自我反证：这轮还不能做的宣称

没有数学意义的“全网全部网页已遍历”；没有每一原始专业标准的付费全文；没有对五仓全部业务运行环境的逐项 live 验收；没有 native pre-send/pre-tool 可靠宿主中介证明；没有每轮六维实际上全都深研的独立 trace；没有训练模型权重；没有证明新知识库已改善新任务成功率。

因此此专题结果最多叫 `SOURCE_STUDY_COMPLETED_FOR_DECLARED_SCOPE__ARCHITECTURE_COMPARISON_OPEN__BEHAVIORAL_HOLDOUT_OPEN`。旧完整性标准的候选知识蒸馏需要后续具体验收，不能因本研究报告写完就关闭目标。
