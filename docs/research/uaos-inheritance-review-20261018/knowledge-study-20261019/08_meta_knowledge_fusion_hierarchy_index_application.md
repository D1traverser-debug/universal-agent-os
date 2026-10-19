# 08｜知识如何融合、概括、细分、索引、蒸馏和真正应用——元知识工程专题

所属：既有 UAOS 总控研究任务、同一 `EVO-20261018-INHERITANCE-REVIEW`；状态：`SOURCE_STUDY__METHOD_CANDIDATES__NOT_NATIVE_SKILL`；研究日期：2026-10-19。

## 0. 研究对象：不仅“学什么”，还应自主发现“需要学习什么思考工具”

用户列举知识融合、概括提炼、细分深入、组件编排、运用索引、总结归纳、方法论、大纲、层级架构；这不是封闭的八项清单，而是要求 UAOS **元学习**：在一个未枚举完的专业领域，自己识别方法族、研究其关系、将原始方法提炼为有边界的操作性知识，并用新任务结果判定是否真正学会。

不能把三个东西混同：
- 资料仓：有论文/文章/指南，可能有摘要错误或来源时效问题；
- 知识导航：让任务找到相关来源及其上下层和关系，**不是**替代原文/业务权威；
- 能力：在新的情境中正确选择方法、合法执行、取得经过独立验证的结果。

## 1. 一手资料逐项学习、机理、反例、适用边界

### M01 — W3C SKOS：多维知识组织与跨语义体系映射
原始标准：https://www.w3.org/TR/skos-reference/
- 事实：concept 可以有 `broader / narrower / related` 及跨方案 `exactMatch / closeMatch / broadMatch / relatedMatch`。特别是 closeMatch 不具备普遍传递性；同义、相似、从属、关联不应混作一类。
- UAOS 学到：一篇“工作流”材料可同时涉及权限、SOP、恢复和产品验收；分类是导航面向，不是唯一所有者。两个框架术语相似，并不意味着可互相替代。
- 失败条件：把风险治理 `measure` 和软件监控 `monitor` 当作等价模块，可能导致重复权威或错误机制选用。不能靠标签相同自动合并。

### M02 — W3C PROV-O：摘要与方法的来源链
原始标准：https://www.w3.org/TR/prov-o/
- 机理：Entity/Activity/Agent 及 `wasDerivedFrom / wasGeneratedBy / used / wasAttributedTo` 关系表达跨上下文来源和责任。UAOS 不必照搬 RDF/OWL 才能吸收此原则。
- 适配：每条摘要标明原始来源、被概括命题、作者实验证据、当前 UAOS 适配推论、相反证据和版本；有合并就保留参与合并的不同原文，不抹除矛盾。
- 反例：论文论文表明测试环境中更好 ≠ UAOS 原生 Agent 已观察到更好。

### M03 — RAPTOR：递归摘要与层级检索
ICLR 原始论文：https://openreview.net/pdf?id=GN921JHCRw
- 原方法：先分块、聚类与概括，逐层构建摘要树，查询可从不同抽象层级召回；对于全局综合比只找几个相邻原始片段有优势，报告的是**原论文基准**。
- UAOS 可用形式：`源文本→机制证据卡→单专题对照→跨专题整体模型→该回合目标解释`；从总体结论应能下钻到原文并反向重建摘要来源。
- 局限：递归概括会丢例外、约束、少数反例；必须允许下钻原始来源，不能用顶层摘要代替具体授权状态。

### M04 — Microsoft GraphRAG / DRIFT：从全局关联到局部细节
研究：https://arxiv.org/abs/2404.16130
实现者说明：https://microsoft.github.io/graphrag/query/drift_search/
- GraphRAG 提取实体关系和群组摘要以回答整体主题；DRIFT 结合全局社区背景、局部探索及后续问题。
- UAOS 推论：输入是“Agent 总是停工”，要先发现产品/宿主/状态/权限/工作流等关联，再向具体未完成工作节点展开，最后检查实际环境结果。
- 不适用：现有 Github 知识量与授权条件不足以支持部署一个新大模型图索引服务；免费只读文档链接可先做真实问题实验。

### M05 — Contextual Retrieval：查得对，不是只查得多
原始工程实验：https://www.anthropic.com/engineering/contextual-retrieval
- 机制：保留分块在原文中的上下文，结合 BM25 与语义召回，再重排序；文章报告自己数据集上 top20 检索漏检降低，不是 UAOS 实验值。
- UAOS 适配：准确标注“该方法属于什么原始问题/宿主/产品、何时发表、哪些事项不适用”；对精确任务ID、工具错误码使用确定性关键词，对广义方法使用跨主题映射。
- 失败：一篇介绍“Agent 监控”的论文因关键词高匹配而误用于“总控主动治理”，必须经独立适用判断拒绝；不能将检索分数提升为因果证据。
- 架构成本：额外 embedding/reranker 常伴随费用和延迟；本轮不采购、不部署。

### M06 — Agent Skills Progressive Disclosure：完整知识与热路径分离
开放规范：https://agentskills.io/what-are-skills
实现示例/目录：https://github.com/agentskills/agentskills
- 启发：简短技能元数据用于发现，完整指令用于激活，参考资料/资源按需加载。知识全面保存与每次把所有原文读入上下文不是一回事。
- UAOS：原有 `docs/research/` 持有完整证据；主题 README 提供发现；激活前还须检查 owner / scope / nonfit / permission；选用的资料真正展开原文，不把目录标题当学过。
- 边界：规范可说明可移植组织方式，无法证明当前 ChatGPT 原生总控已经自动调用本仓 Skill。

### M07 — Agent Workflow Memory：轨迹到可复用方法
ICML 研究：https://proceedings.mlr.press/v267/wang25bx.html
- 从执行轨迹归纳参数化例行方法，再选择性应用于新任务；不是把任务历史归档当可执行能力。
- UAOS：保留 `KnowledgeItem` 原 owner 和 `MethodTransferAssessment` 中 fit/nonfit、actual current refs，实际动作仍归原 task/execution owner；新业务中的失败会反向修订经验。
- 危险：局部 PR 合并成功被蒸馏成“PR 即进化完成”；必须以业务环境 outcome 纠偏。

### M08 — Realist Synthesis：Context–Mechanism–Outcome (CMO)
系统综述：https://pubmed.ncbi.nlm.nih.gov/30633712/
- 问题不是“此方法好不好”，而是 `在什么上下文 / 经什么机制 / 对什么结果` 生效。研究有领域/时间/对象边界，移植需要重审。
- UAOS 方法卡：`context conditions / intended mechanism / target outcome / negative contexts / evidence / alternative explanation / runtime owner / validation`；同一方法若环境变动，可适用性随之变化。
- 反例：“多 Agent 总能提升性能”在单工具明确任务下可能增加协调开销；要允许 NO_CHANGE / ONE_AGENT。

### M09 — OpenAI Agents SDK：组件编排不等于多 Agent
实现者说明：https://openai.github.io/openai-agents-python/multi_agent/
- 明确区分模型决策编排与代码确定性编排，以及 supervisor 管理 specialist-as-tool 与 handoff 交换执行所有者。两者是不同控制权语义。
- UAOS：问题识别/专业研究可以组合专家方法，但不可无授权从父仓代替子域业务 state；模块化必须约束输入、输出、所有权、重试、调用条件和真实效果。
- 不适用：当前原生 ChatGPT 不经 Python SDK，不能用该 SDK 的路由特性宣称原生行为已修复。

### M10 — 2026 faceted-analysis distinction（摘要可查，全文受限）
研究摘要：https://doi.org/10.1080/01639374.2026.2657155
- 将 faceted analysis（分析方法）与 faceted classification（形成的分类产品）区分。作者认为混淆二者会令分类机制掩盖实际认知工作。
- 对 UAOS 的直接警示：六维15格属于某种分类产物，不等于执行了全面分析。
- 来源限制：本轮站点返回 403，只有检索摘要信息，不能声称全文细读、也不能将作者全部实证结论当事实。

## 2. 统一融合：它们解决**不同函数**而非组成固定七步骤

| 问题 | 可借鉴方法 | 在现有 UAOS 中的归属 | 应主动拒绝的等价替换 |
|---|---|---|---|
| 先知道有哪些知识 | Skill metadata / README / source index | 既有 `docs/research/`、`RETRIEVAL_POLICY` | 目录存在 = 知识已用于任务 |
| 关系如何对应 | SKOS、GraphRAG、证据链接 | 原文件关联与非权威导航投射 | 相关/相似 = 同义/因果 |
| 如何向上概括 | RAPTOR、系统综述 | 主题方法卡与综合原文追溯 | 摘要 = 原始事实完整版 |
| 如何向下研究 | 层级回溯与 contextual retrieval | 原始论文、当前仓库原文 | 只看摘要也称深研 |
| 如何融合竞争理论 | CMO+竞争假设+反例 | 既有 CognitionCase/DeepTask | 多篇都引用 = 结论正确 |
| 如何蒸馏执行方法 | AWM + KnowledgeItem + MethodTransfer | 现有知识生命周期和准入 | 历史修复 = 新场景自动可用 |
| 如何编排专业组件 | SDK 编排方式 + owner/authority graph | 原有任务、控制 kernel、业务子域 | 再建一个中央 Agent/图数据库 |
| 如何验证已会用 | outcome eval + holdout + negative control | 当前任务/Evolution + 真实业务结果 | 静态 CI/源码记录 = 原生智慧 |

该表不是强制每轮八次审批：研究时可以对同一主题同时做概括、反证、下钻、比较、运用与再学习。用户每轮全维深研的**实质要求**仍保留，不能以“做了索引”偷换。

## 3. 具体的融合与蒸馏例子（当前用户未指定列出的能力）

`能力：知识发现→理解→改写为有边界的动作→任务中使用→反馈改写知识` 是组合目的，不是八个新目录。

任务 I：“总控遇到 PR 操作失败就停工”
- 原始事实：以前回答结束时任务 `RUNNING` 且仍有只读研究/源码检查路径；原生 Python gate 无调用证明。
- 上层抽象：`局部动作停止 != 全局目标完成/阻断`，需重新分析任务依赖图。
- 相关方法：BPMN 异常分支 + TLA+ liveness + SRE 恢复 + AWM 执行轨迹抽取。
- 非适用：写操作遭到安全拒绝，不得找另一写接口绕行。
- 最小运用：继续授权只读和评估，保留被拒写入为 open，核实工具返回，真实报告下一动作。
- 未通过项：没有证明未来陌生宿主/陌生业务也会无提醒运用此方法。

任务 II：“PR #163 六轴研究门禁都齐全但答错”
- 下层原始事实：`admit_full_dimension_study` 检查引用数量/标签/调用者 verifier 真假，没有验证因果与语义关联；已在 `test_full_dimensional_semantic_holdout.py` 以 1 xfailed 固化。
- 方法组合：产品结果追踪 + SKOS 区分关系 + PROV 来源链 + CMO 适用条件 + 独立真实任务评估。
- 非适用：新增七维标签、更多资料引用，不会单独修复语义有效性。
- 下一步：真实宿主/业务独立评价现有六维分析与另一种上下文—机制—结果驱动研究；没有证据前不一拍脑袋改门禁。

任务 III：“用户需要金融写作，但父仓研究声称解决”
- 来源查找：从业务角色导航找到 Financial 原 owner，读取当前任务要求和业务证据。
- 结构综合：总控可贡献公共问题推理/方法选择，不能把财金领域研究、真实文章、Word 交付收据由父仓虚构或替代。
- 方法应用条件：只有实际子域成果被该领域标准验证，才能宣布产出成功。
- 非适用：父仓 CI 绿灯、某标准方法已被引用，不构成财经产品效果。

## 4. 组件编排契约（**不新建实际软件层**）

从给定目标出发：确定宿主/权限/业务 Owner → 来源检索（目录/全局/精准）→ 获取原文/对立证据 → 合成 CMO 候选方法 → 评估能否调用现有 SOP 或工具 → 执行授权动作 → 以外部环境/业务权威复核 → 将实际效果反馈原任务/Evolution。

选择具体编排形态基于能力：单工具动作无需增加代理；跨多个子域时父子职责不变；需要确定性 Safety 的由受控代码门禁执行；探索未知可以由 Agent 做知识分析。**不得**仅凭“组件编排”这个名词认定应增加组件。

## 5. 反证条件

- 一份美观的层级摘要丢失关键“不适用”条件：**摘要质量失败**。
- 冷库有正确方法但索引只召回相似的错误旧方法：**检索失败**。
- 索引召回正确方法但未验证当前权限就执行：**方法迁移和授权失败**。
- 三个技术论文都成立，但新业务没有正向效果：**目标有效性失败**。
- 新索引/插件引入第二权威导致冲突：**架构治理失败**。
- 按目录成功走完全部环节却反复停工：**续行能力失败**。
- 源材料说法不同但摘要强行统一：**知识融合失败，应保留分歧**。

## 6. 验收策略与不完整范围

首轮主要原始角色：规范（W3C）、学术论文（RAPTOR/AWM/CMO）、作者实现（GraphRAG/Contextual Retrieval/Agent SDK）、开放技能格式、2026分类研究摘要。未做全面系统综述的所有引文滚雪球、未复现实验用的 embedding/GraphRAG 模型、未访问付费标准全文，**不称外网资料饱和**。

**实验必须覆盖：** 已知方法跨任务匹配、错误相似方法错用拒绝、摘要丢失反例、原文/旧摘要冲突、工具权限边界、当前宿主无法自动调用、真实业务结果。研究文档本身只支持 `SOURCE_STUDY`，不是 canonical skill 晋级。
