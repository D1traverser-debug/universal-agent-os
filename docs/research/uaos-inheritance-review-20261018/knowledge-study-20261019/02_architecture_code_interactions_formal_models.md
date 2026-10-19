# 02｜软件架构、代码思维、复杂交互、形式化与多路求解：专题知识库

性质：研究证据，不是自动实施的架构决定。当前源代码归属 UAOS 已有 kernel/runtime，研究归属现有总控任务与 EvolutionTransaction。日期：2026-10-19。

## 1. 原始问题

用户要求“系统思维、代码思维、交互全推演、相关交互整合、条条大路通罗马”，不是要求绘制所有维度的图，而是要求一个从任意事实信号出发，能探索对象—事件—约束—方法—后果、发现多条可行路线和潜在系统性失败的统一行为能力。没有任何有限测试集合可保证覆盖无限未来交互；应定义模型覆盖与动态扩展准则，而不能宣称全知。

## 2. 原始来源逐项研究

### A01 — SEI Architecture Tradeoff Analysis Method (ATAM)
https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/
- 从质量属性场景与干系人驱动力出发，找敏感点与权衡点；例如增加研究覆盖与推理成本、质量稳定性之间的权衡。
- UAOS 价值：先识别用户价值场景、失效场景与所有者，不直接从“新模型很先进”推出新架构。
- 限制：ATAM 是架构评价，不是自主执行调度器，不能代替具体状态/实现证明。

### A02 — Architecture Decision Record，Martin Fowler
https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
- 留存决策上下文、替代方案、理由、后果；结论可更新，但旧决策应可追踪。
- 迁移：现有 `docs/adr/` 已承担该职责；拒绝另建平行“架构想法总账”。
- 反例：旧 ADR 记录“部署预期”不能替代当前 GitHub main 的运行状态。

### A03 — Leslie Lamport，Safety, Liveness and Fairness
https://lamport.azurewebsites.net/tla/safety-liveness.pdf
- Safety：坏事不发生；Liveness：好事最终推进；Fairness：满足前提的动作不会被持续饿死的进展假设。
- UAOS 历史：阻止错误终结的门禁只表达 Safety 部分；在宿主没有持续调度/动作选择时，Liveness 不成立。
- 抽象要求：`RUNNING && enabled(safe_action) -> eventually(attempt(safe_action) || legitimate_block)` 只是候选活性性质，不是已通过模型检查的规范。
- 注意：受安全政策拒绝的写入不是被“公平性”允许绕过；活性前提只能包括仍被真实授权的动作。

### A04 — NIST ACTS Pairwise/t-way Combinatorial Testing
https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/faqs
- 用 t-way 覆盖数组约束交互组合爆炸；研究与实例表明许多故障发生在少数变量交互，但不排除高阶交互。
- 用于 UAOS：抽取 `host × authority × action_type × user_fact × tool_result × remaining_work × evidence_confidence`，验证非同质边界。
- 限制：只覆盖声明的因素和值；未知因素仍需故障发现。不能使用覆盖数组指标推导真实智能质量。

### A05 — NIST Event-Sequence Testing
https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/combinatorial-methods-in-testing/event-sequence-testing
- 交互不只是静态参数组合，还涉及事件先后、状态变更、重试、补偿与顺序敏感缺陷。
- UAOS 用例：`PR请求拒绝 → 改为只读探索 → 新证据 → 下一次授权 → 恢复`；另一用例 `API超时但提交可能成功 → UNKNOWN → 先对账再重试`。
- 不适用：没有真实顺序事件证据时，不以画出的事件图声称已执行。

### A06 — BPMN 2.0.2，OMG
https://www.omg.org/spec/BPMN/2.0.2/PDF
- 事件、活动、网关、异常中断、补偿流程、并行/条件分支等语义。
- UAOS 迁移：SOP 只有固定路径；实际长流程需要状态、并发、权限、等待、异常、补偿与恢复。
- 反证：将“工具拒绝”一律当整个流程停止，会错误地取消独立只读分支。

### A07 — NASA SE recursive design
https://www.nasa.gov/reference/4-0-system-design-processes/
- 需求、功能分解、操作概念与设计反复交叉校正。一个组件无法独立保证跨宿主产品目标。
- UAOS 迁移：父控制能力、工具插件、子域业务工作流与最终产品收据必须闭环对齐。

### A08 — AWS Well-Architected Framework
https://docs.aws.amazon.com/wellarchitected/latest/userguide/waf.html
- 运行、可靠性、安全、性能、成本、可持续性相互牵制。引用的是云平台质量评价机制，不强行部署 AWS。
- UAOS 对照：一次每轮全网深研降低漏项是否有证据？若延迟/成本/遗漏下一个行动显著增加，即存在新架构风险。

## 3. 不以六维分类为架构：交互图语义

建议将已有 `TaskIndex`、`TaskContract`、`CognitionCase`、`KnowledgeItem`、`EvolutionTransaction` 视为不同对象的**已有权威所有者**；图是跨所有者的查询/分析视图，不拥有新业务状态。

节点候选：Goal, Requirement, User, Host, Tool, PluginCapability, Agent, BusinessTask, Evidence, Unknown, Alternative, Action, Asset, Version, Outcome, FailureMode, Method, Review。
关系候选：owns, authorized-by, constrained-by, depends-on, causes, contradicts, replaces, blocks, observes, supports, tests, invalidates, promoted-to, applicable-to, transferred-to。

遍历从**事实与目标**进入，不是先排六个研究小组。对关键边执行：
- 向上：为何执行、是否符合真实目标。
- 向下：哪个组件或工具实际执行，出现何种收据。
- 横向：相关任务、共享方法、交叉影响、替代路线。
- 反向：谁能推翻本条证据、谁会受新动作影响。
- 时间：上一版证据在新版本是否失效，未来条件何时改变。
- 外部：已有先进方法、不同领域经验、没有进入现有图的未知机制。

## 4. 交互模型：明确但非完整穷举

因素：`Host={native_chat,controlled_sdk}`；`Permission={read,write,denied}`；`Task={RUNNING,HOLD,COMPLETE}`；`Tool={success,hard_fail,timeout_unknown}`；`Work={safe_remaining,choice_only,none}`；`Knowledge={relevant,stale,unrelated}`；`Evaluation={unit,host_trace,product_outcome}`。

必须覆盖的组合与序列：
1. native_chat + test-green：不得自动声称 native hook 生效；
2. controlled_sdk + verified six-axis study + semantically irrelevant method：结构能过、语义仍失败；
3. denied write + safe_read_remains：原写入不重试/绕道，执行并核实只读动作；
4. timeout_unknown + durable mutation：先核对提交身份，避免重复副作用；
5. choice_only + safe_research：只阻塞依赖用户选择的分支；
6. COMPLETE + new user instruction：新任务与历史任务分别受权威路由；
7. stale knowledge + relevant label：检索命中不能免除新证据验证；
8. direct child + parent policy update：子域业务权威不得被父状态冒名覆盖；
9. heavy research + quick exact answer：交付是否仍正确且符合明确深度约束；
10. unknown failure family：现有固定类别不能把未知问题变为假绿色。

每个用例应包括前置状态、来源、允许动作、禁止动作、观察结果、验证器、恢复分支。不要只写“PASS”；实际执行轨迹与结果需单独持有。

## 5. 竞争架构路径

- NO_CHANGE：保留 PR #163 的六维计数门禁，低迁移成本，但语义深度无法证明。
- OPTION A：继续增加七维/八维和字段，结构冗余上涨，仍缺真实认知证据；不推荐直接晋级。
- OPTION B：在现有评估器中做目标—关系—结果追踪，附加对照评价；最适合受控主机验证，但必须确认谁调用、性能与成本。
- OPTION C：全新知识图服务/多 Agent 元治理；除非 B 无法达到目标且有明确必要证据，否则新增影子权威和运维开销高。
- OPTION D：不增加框架，先用受控端到端测试和现有宿主继续能力修正；可用于需求不确定阶段。
现阶段只保留 B/D 为优先实验候选，不能宣称它们已胜出。

## 6. 蒸馏候选

`K-ARCH-01`：**先建立目标/状态/依赖模型，再评估多个架构候选，遵守 single authority**；触发：提议新增能力层或修复跨模块缺陷；证据：受影响所有者、相邻路径、独立反证；非适用：目标和机制单一、真实影响有界的简单局部修复。

`K-INTERACT-02`：**单工具失败应检查状态图中仍可达的授权动作**；触发：局部失败；非适用：安全拒绝覆盖所有剩余动作；验收：复杂顺序事件和不同宿主的真实收据。

`K-FORMAL-03`：**把不该发生与必须最终推进分别验证**；触发：系统有大量拒绝门禁但 Agent 提前停工；验证：Safety 测试 + Liveness 有真实执行器的调度/续行测试，二者不能互代。

## 7. 本主题未知与扩展

未执行完整 TLA+ 规范模型检查；未有真实 ChatGPT tool-origin 完整审计轨迹；未对全部未来事件做数学完备证明，也无法宣称此事可完成。下一步需以当前任务的真实操作/错误收据、子仓业务边界和不同主机配置建立可复现实验。
