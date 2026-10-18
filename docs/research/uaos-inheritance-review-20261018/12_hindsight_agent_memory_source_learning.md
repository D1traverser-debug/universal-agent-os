# 12 | Hindsight 长期记忆引擎：深度学习、蒸馏、反证与 UAOS 方法知识候选

研究对象：vectorize-io/hindsight（截图清单第 1/4 项）。来源冻结版本：main @ 5331da2f4db369528bb122075341a7de9c3df6df。调研日期：2026-10-19。
归属：UAOS 总控；精确任务：state/tasks/uaos-inheritance-review-20261018.json。新知识状态：CANDIDATE / NOT_CANONICAL / NOT_INSTALLED。
本文件是现有 docs/research 知识证据的继续，不创设第二个知识目录、认知内核、任务索引或进化控制器。不将用户图片、GitHub 搜索结果或第三方 SKILL 当作 UAOS 的运行权威。

## 一、总体结论

Hindsight 是一套长期记忆服务与 Agent 接线机制，并非完整的 Agent OS。其工程优点是：原始材料抽取为事实、实体和时间关联；语义/关键词/图/时间多路召回；工具驱动的基于来源反思；从事实到 Observations、Mental Models、Knowledge Pages 的层次化归纳；支持证据依赖、历史更新、来源撤回；可通过 Skill、MCP、SDK 或 wrapper 接入。

UAOS 已具备 SourceSnapshot、KnowledgeItem、KnowledgeCatalog、CognitionCase、EvolutionTransaction、精确任务状态和权限/资产规则。真正值得学的是「证据入库、历史经验能否被正确召回、反证、应用、撤回」的机制，不是拷贝 Hindsight 的另一套状态权威。引入一个检索引擎本身不能证明原生 ChatGPT 会主动调用它，也不能证明用户业务结果改善。

## 二、来源、实读范围和可证程度

- 原始 Skill：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/hindsight-integrations/agent-plugin/skills/hindsight-memory/SKILL.md。它通过 recall、retain、reflect 暴露简单行为入口；实际能力仍依赖运行中的 Hindsight 服务与 MCP。
- 文档 Skill：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/skills/hindsight-docs/SKILL.md。是按技术文档自动生成的阅读入口，不是完整运行时的自动执行保证。
- 官方 README：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/README.md。列出 SDK、Docker、本地/托管、PostgreSQL、MCP、LLM wrapper 与许可。
- 一手研究论文：https://arxiv.org/abs/2512.12818 。四网络与 Tempr/Cara 的理论框架、实验条件、限制。
- 官方 Best Practices：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/skills/hindsight-docs/references/best-practices.md；Retain、Recall、Reflect API：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/skills/hindsight-docs/references/developer/api/retain.md、https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/skills/hindsight-docs/references/developer/api/recall.md、https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/skills/hindsight-docs/references/developer/api/reflect.md。
- 观察与知识：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/skills/hindsight-docs/references/developer/observations.md、https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/skills/hindsight-docs/references/developer/api/mental-models.md、https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/skills/hindsight-docs/references/developer/api/knowledge-pages.md。
- 代表性运行实现：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py、https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/hindsight-api-slim/hindsight_api/engine/memories/pg/recall.py、https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/hindsight-api-slim/hindsight_api/engine/reflect/agent.py。
- 反证实现/测试：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/hindsight-api-slim/hindsight_api/engine/reflect/retractions.py、https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/hindsight-api-slim/tests/test_mental_model_retractions.py、https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/hindsight-api-slim/tests/test_recall_temporal_window.py、https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/hindsight-api-slim/tests/test_memory_defense.py。
- 官方安全指南：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/skills/hindsight-docs/references/developer/memory-defense/index.md。外部批判性论文评述：https://github.com/lhl/agentic-memory/blob/main/ANALYSIS-arxiv-2512.12818-hindsight.md 。
- 许可：https://github.com/vectorize-io/hindsight/blob/5331da2f4db369528bb122075341a7de9c3df6df/LICENSE，MIT，复制/改造代码须履行许可中的声明义务。

当前源码树约 5,837 项。研究以源码目录的真实架构轴和接口/实现/负向测试/部署/安全五类横截面取样。不是对全仓 5,837 项逐行审计，没有部署 Hindsight 或复现所有性能结果。与第三方版本强相关的陈述以冻结 commit 为准。

## 三、理论架构与公开 API 的语义边界

论文提出四类逻辑网络：World（客观世界事实）、Experience（Agent 事件/经历）、Opinion（主观信念、置信和时间）、Observation（对实体/经验的综合概括）。Tempr 偏重时间/实体关联的记忆和多路召回；Cara 偏重有行为倾向的反思。当前 Recall API 主流 types 过滤项是 world、experience、observation，而 opinion、Mental Model、Knowledge Page 和 Directives 并不等同于可随意互换的“第四种 API 事实类型”。

迁移禁令：论文概念不直接成为 UAOS KnowledgeState、TaskStatus 或 authority_context。主观记忆/看法必须是可检验候选，不得因高 confidence 或被频繁检索而被视为系统指令。

## 四、八项方法蒸馏

### M1 Retain：保留结构与时间，而非盲目把原文浓缩成一句话

来源事实的结构应明确是谁说的、发生在什么时候、何时被记录、来自哪个文档/版本及怎样支持当前断言。稳定 document_id 有助于更新同一会话文档，context 描述材料来源；动态抽取还需要处理零事实/未能抽取的情况，不能把「空检索」解释成「来源没有信息」。同 document_id 的重处理有覆盖或替换语义，不是不可变事件日志。

限制：官方文档“retain 不逐字保存原文”的宽泛描述与 raw document、chunk expansion、verbatim/chunks 模式不能混为一谈。UAOS 已有 Git commit、SourceSnapshot、原始工具结果和不可变历史档案，知识蒸馏绝不能取代原文、历史提交或审计日志。

可迁移方案：在现有来源型候选里显式记录 source-id、version/hash、observed-at、occurred-at、owner、claim、counterexample、proof-ref、scope，保留事实与提炼方法的区别。

### M2 Recall：四种检索信号互补，但要先保证当前权威精确命中

语义搜索捕获不同表述，关键词/文本检索捕获 PR 编号、Commit SHA、专有错误码；实体关系扩展捕获间接依赖，时间搜索区分历史与当下。Rank fusion（RRF）融合多路排名，cross-encoder 二次重排，再按 token 预算截取。计算深度 budget 和返回 max_tokens 是两个不同控制维度。Temporal arm 在查询或请求存在有效时间约束时有意义，非所有查询都跑四路。部分原生 PostgreSQL 方案使用 tsvector 而不是严格 BM25；不能将所有后端统一宣称 BM25。

UAOS 方法借鉴：先精确从 TASK_INDEX 和 exact state 恢复当前身份，不许用语义相似把用户带去历史任务。只有寻找「类似失败类/方法」时才考虑多信号检索，再由来源证据和当前 owner 辨别适配性。适当减小召回 token；精确任务不要为简单读取启动整套语义图推理。

### M3 Reflect：有来源的推理不同于单纯 recall

Reflect 是会使用工具的推理流程，文档和实现采用 Mental Model → Observation → raw fact 的层级信息，并可输出 based_on/trace。高层综合可能过期，矛盾时要回查事实证据。Bank dispositions（skepticism 等）会影响回答语气与处理方式，但不能代替独立事实验证、业务授权或系统治理。可放在“为什么这个方法在新场景适用/不适用”的审查里。

UAOS 当前 cognition 唯一 owner 是 DELIBERATION_POLICY#cognition_kernel 和 CognitionCase；不新增一个叫 Reflect 的上级控制器。外部 Skill 或 bank Directives 只是非权威输入。

### M4 Observations：证据关联的概括和历史矛盾保留

后台 Consolidation 对新事实与既有 Observation 进行 create/update/delete，保存具体 supporting facts、历史措辞、proof_count，并在矛盾时尝试保留“过去→现在”的状态演进。任务可能先于后台整合完成，所以“retain 成功”不等于“所有 observation 最新”；stale 必须回查尚未整合的 raw facts。

UAOS 借鉴：多个历史 PR 可以蒸馏为同一失败类及方法，但不能把同一源的多次复制当成独立支持。更正应保留旧事实的时间与失效说明，不应无声覆盖。

### M5 Mental Models / Knowledge Pages：按需更新、避免循环自证

预计算的 Mental Model 可以回答反复出现的稳定问题；Knowledge Pages 是基于观察归纳、可按局部触发更新的知识页。Delta refresh 尽量只使用新增材料并保留旧结构，可通过排除其他 Mental Model 避免相互引用漂移；标签默认 strict 与非 strict 的细节会影响底层数据范围。错误的页面过滤甚至会生成空结果，不能仅凭操作成功认定数据完整。

**独立的关键反例**：Knowledge Pages 文档明确指出部分 is_stale 的判断只检测新增写入，而看不到底层事实被删除；已撤回事实仍可能让页面看似最新。项目的 retractions 代码尝试检查 based_on 引用是否仍存在，负向测试用 stub 验证确定性机制，**尚不证明真实 LLM 总能正确删除不实结论**。

UAOS 借鉴：有必要对引用的失效证据进行反向依赖失效传播，并在结果重算后验证用户可见结论没有保留已失效断言。不要只观察最后更新时间。

### M6 Banks / Tags：索引隔离、可见性过滤和真实授权是三件事

Bank 用来隔离不同上下文；读取不存在的 Bank 可能返回 404，而写操作可自动创建。tags_match 有 any、all、any_strict、all_strict、exact 等模式；非严格模式可能包含未标签化的共享数据。某些 Directives 的匹配方式不完全等于事实的匹配方式；多租户系统不能把 tags 当成访问控制表。

UAOS 保留 AUTHORITY_WRITE_POLICY、PersistentAssetGate 和 owner binding 的实际权限判定。候选知识跨领域可引用，但个人数据或 child 私有资产不能因为可被检索就被提升为共享知识。

### M7 Memory Defense：未经信任的内容可能变成永久污染源

源码与测试显示可选择启用针对秘密/API token/PII 的入库前扫描、脱敏或部分 block 路径，并有针对多种格式、密钥紧贴中文字符等负向测试。官方源明确 Memory Defense 默认关闭，新增配置不自动清洗旧知识；OSS 与 Enterprise 文档对规则数量和高级注入检测的口径不同，不要跨版本组合成“默认全安全”。

UAOS 必须把第三方仓库文档、检索片段、网页和工具返回值作为 UNTRUSTED_DATA。外部文本里的伪系统提示不能进入控制权威；秘密不能写入外部记忆服务或上传到本研究记录。防护属于执行路径而非模型“记住不受骗”。

### M8 Evidence Retraction：删除原始证据仍可能留下综合误信念

反向证据损失（引用的事实被删除、失效、重新摄入）不能只靠「有哪些新事实」判断。官方 retractions 模块直接讨论了这个盲区并在纯代码层处理 cited fact IDs 仍存活与否。实测测试涵盖存在性、跨 bank 约束、非事实 ID 忽略与选择性撤回，但它也明确某些测试绕过真实模型决策。

UAOS 最直接可用的方法：被知识页或失败类引用的唯一证据失效，相关方法候选必须转为复核或停用；不允许仍以 CANONICAL 状态被无条件使用。相邻多个引用要独立追踪，不能把一条虚假结论被复制三次当作三份证据。

## 五、评测、来源可信度与反证

论文报告在其指定 LongMemEval 环境下，开源 20B 底座结合 Hindsight 的总体成绩由全上下文基线 39% 到 83.6%，更大模型方案可达 91.4%；项目后来的公开 benchmarks 页面给出不同配置下更高的 94.6% 等数字。这些数字来自不同版本/底座或条件，不能拼为一个连贯实验，更不是 UAOS 真实运行结果。项目维护者具有商业推广利益；外部分析指出 LLM judge、基线可比性、成本/延迟、样本泄漏和默认安全边界有待额外核验。

可查来源：https://arxiv.org/abs/2512.12818 ，https://vectorize.io/benchmarks ，https://github.com/lhl/agentic-memory/blob/main/ANALYSIS-arxiv-2512.12818-hindsight.md 。

不部署直接移植的另一原因是：PostgreSQL/embedding/reranking、LLM 调用、保留策略、bank scope、密钥和跨会话授权增加运维与隐私边界。如果 UAOS 精确 Git 检索和现有知识证据路径已足够，那么部署新服务可能只增加复杂度，不增加可信实际结果。

## 六、映射到 UAOS 的既有权威及 Fit/Misfit

| Hindsight 概念 | UAOS 已有 owner | 建议蒸馏进已有能力 | 不适用或禁止 |
| --- | --- | --- | --- |
| 事实入库与时间 | SourceSnapshot / KnowledgeItem / Git 证据 | 来源修订、事件时间和信念时间分开；保留原始依据 | 历史抽取摘要冒充权威状态或删除 source |
| 多路召回 | RETRIEVAL_POLICY / exact TASK_INDEX / KnowledgeCatalog | 对方法候选可用精确关键词+语义+时间+关系组合检索 | 模糊召回覆盖 task ID 和 child owner |
| 证据反思 | CognitionCase / DELIBERATION_POLICY | 先匹配故障类与旧方法，然后用当前反证检验 fit / misfit | 第二套 cognition/Reflect 管理层 |
| 逐步观察归纳 | 知识生命周期 RAW→CANDIDATE→EVALUATED→CANONICAL→RETIRED | 归纳方法时保留支持数、冲突、因果适用条件 | 模型自评或重复文档直接 CANONICAL |
| 证据撤回 | SourceSnapshot 与 Evol. evidence refs | 失效依赖的反向检测、拒绝使用旧证据 | 只看新写入水位、更新“状态”不撤回结论 |
| Bank/Tag | authority_context / PersistentAssetGate / owner binding | 私有知识与共享方法隔离 | 用 tag 替代 ACL、资产权威与审批 |
| 持续刷新 | EvolutionTransaction / 真实验证与复盘 | 只在内容或引用失效时重评，记录实际效果 | CI 绿灯=原生技能已调用或业务已成功 |

当前根本差距并非完全没有历史资料，而是 UAOS 未证明「真实 ChatGPT 选择 Agent → 检索以往方法 → 确认适用性 → 实际修复 → 验证后效 → 将反例反向撤回」的完整闭环。Hindsight 借鉴只能提升某个环节，不能替代缺失的 host 观察、授权执行或用户业务验收。

## 七、可迁移的七张候选方法卡

每张卡必须保留 source commit、适用触发、明确 non-fit、反证条件、owner 及后来验证引用。未经使用不得虚构 usage_links：

1. HIN-01（来源和双时态）：适用于状态演进与跨会话更正；非适用：用“最后一条消息”直接覆盖不可变历史。反证：旧日期与新日期的问题回答是否可同时正确。
2. HIN-02（多路方法召回）：适用于旧问题类换词/跨领域重现；非适用：当前精确任务状态已知。反证：跨仓方法匹配是否比 exact+keyword 基线减少漏检且不误匹配 owner。
3. HIN-03（证据支持的观察）：适用于重复错误模式抽象；非适用：只有多个相同摘要无独立事实。反证：删除唯一真实 source 后观察应失效。
4. HIN-04（撤回传播）：适用于依赖被撤销事实的方案/指南；非适用：只加一条更正让旧建议继续在知识页出现。反证：基于不存在 fact ID 的结论必须被拦截。
5. HIN-05（检索预算与增量刷新）：适用于大规模外部知识；非适用：简单精确查找。反证：增量方案的成本/延迟/正确率与现有方案比对。
6. HIN-06（知识隔离）：适用于共享技术方法与业务私有上下文共存；非适用：用 tags 管理强制读写权限。反证：跨域隐私污染负向测试。
7. HIN-07（污染隔离）：适用于第三方文本和工具结果进入长期知识；非适用：默认假设安全过滤自动启动。反证：对抗文本不得改变 UAOS authority 或绕过 mutation gate。

**知识状态：这些卡全部是 CANDIDATE，只在本研究文档内留存。** UAOS 的 KnowledgeCatalog 实现是运行时对象而非该文档所创建的持久活跃数据库。现有知识契约要求必须经过 CANDIDATE→EVALUATED，有有效的验证使用记录才允许 CANONICAL。本研究尚未完成上述冻结实验，所以不得假装已晋升 Canonical。

## 八、下一阶段的独立冻结验收（TEST_SPEC_ONLY，未执行）

1. 双时间窗：过去偏好 A 后改 B；“过去”和“现在”同时答对。
2. 证据撤回：删除唯一来源后相关方法/知识页不可继续无条件使用。
3. 错误跨域：金融写作的发布建议不能变成视频 Agent 的执行权限。
4. 同源双计数：反复引用同一个网页不提高独立证据数。
5. 精确继承：已有任务索引优先于相似度记忆；只有真正歧义才请用户选。
6. Scope 越权：untagged/global、tagged directive 不泄漏跨用户敏感信息。
7. Prompt injection：外部伪 system/instruction 不能提升权限或调用未经授权写入。
8. 异步观察：retain 返回成功但 consolidation 尚未完成，必须回查原始事实。
9. 文档重处理：同一 document ID 更正后仍能溯源旧 committed evidence。
10. 业务后效：方法召回不等于真实文章合格/视频盈利；仍依 child owner 验收。
评价：记录任务通过数、来源支持正确率、误检漏检、越权率、检索 token、延迟/成本；固定对照为当前 UAOS exact 读取与已存历史方法检索。不能用自述 PASS 代替执行证据。

## 九、候选方案比较与治理结论

方案 A：直接部署 Hindsight 服务、MCP 与自动 retain。潜在多路检索收益，但有运行依赖、数据权责、隐私/费用、host 激活与第二记忆存储边界。缺少实测增益和获授权迁移数据，当前不选。

方案 B：在 UAOS 现有知识研究文档及原任务引用中持久化方法卡、来源、反例、冻结验证要求；以后按具体真实问题评估方法调用效果。本轮选 B：改动局部、成本低、保留独立可反驳性、不新增权威。

方案 C：完全不学习。无法降低反复遗忘方法的风险，仅作为对照基线。

**结论：完成第 1 项的来源级研究、机制蒸馏、知识候选与反证设计；尚无 Hindsight runtime 真实部署/性能实测，不能宣称完整知识饱和或 UAOS 记忆进化闭环验收。** 本文件的下一次更新必须基于新 commit、独立实验或实际跨仓复用，而非重复改写描述。

下一对象依次为 2. stablyai/orca，3. cloudflare/security-audit，4. paperclipai/paperclip。按用户要求一项一项学习，不在本份文档中擅自假称已经完成其余三项。
