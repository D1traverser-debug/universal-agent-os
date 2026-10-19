# 05｜工具、插件、能力发现、多路径求解与真实执行：专题知识库

性质：候选专业方法和当前工具发现审计，不是授权清单。日期：2026-10-19；依附 UAOS 现有控制/工具/权限所有者，不新建工具管理系统，不订阅新付费服务。

## 1. 用户在问什么

“知道善用插件吗？知道条条大路通罗马吗？会用什么优秀的办法结合吗？”的实质：任何新任务进入时，主动发现所有**实际可用**的资源、信息和操作路线；评估每一路线的能力、数据新鲜度、权限、成本、可靠性、可验证结果；不把首选平台写死，不把用户要求变成自动加一个插件的借口。

## 2. 专业来源与方法

### T01 — MCP Specification, July 2026
https://modelcontextprotocol.io/specification/2026-07-28
- 规范化模型—外部工具/数据的交互，2026 版引入或完善状态、路由、授权和扩展的协议细节。
- 工程原则：工具发现≠当前账号获准执行；工具描述≠实际权限；参数模式、可变更性、敏感性与授权边界必须在调用前确定。
- UAOS：GitHub、Drive、Notion、Gmail、Canva、视频能力等从**宿主真实列出的工具**发现，结果由原工具提供，不得猜测 API 参数。

### T02 — Anthropic Building Effective Agents
https://www.anthropic.com/engineering/building-effective-agents
- 增强型 LLM 包含检索、工具和记忆；常见执行形态包括 prompt chaining、routing、parallelization、orchestrator-workers、evaluator-optimizer 和动态 Agent，分别适用不同问题。
- UAOS：不是所有任务都需要多 Agent、多轮系统、外部云；先比较直接调用、工作流复用、受控 SDK 和升级路径的实际收益。
- 原文强调在环境中获得真实反馈验证进度，因此工具调用成功与目标效果仍需分开。

### T03 — Anthropic Context Engineering
https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- 选择高信噪比上下文，包含工具列表、历史、环境文件与检索来源。大量无关工具会占用注意与容量。
- UAOS：全面知识库留在冷路径；工具按需发现，相关能力进入当轮热路径；不能把所有插件说明和所有研究文献每次全文粘贴。

### T04 — AWS operational excellence
https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/operational-excellence.html
- 可观测、可控、可撤销的自动化和业务价值优先；不推荐未经确认的付费基础设施。
- UAOS：低成本工具先行，但选择不仅比价格，还要看数据所有者与版本、操作回滚能力和合规性。

### T05 — NIST AI RMF Playbook
https://airc.nist.gov/airmf-resources/playbook/
- Govern/Map/Measure/Manage 不是线性清单；工具获取、使用和下线涉及角色责任、环境限制、真实风险与运行验证。
- UAOS：插件变更也属于资产与能力生命周期；不可把“另一工具能做”当成绕过拒绝动作的许可。

### T06 — NIST combinatorial interaction
https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/faqs
- 工具组合交互按因子和事件顺序覆盖，不只测单个成功路径；重点包括宿主、权限、外部状态、网络和重复操作。
- 实例：一个工具返回 UNKNOWN，一个返回 stale，决策必须保守并对账。

## 3. 当前聊天宿主实际暴露的工具类别（现场发现）

本轮工具目录可见：`GitHub`、`Gmail`、`Google_Calendar`、`Google_Contacts`、`Google_Drive`、`Notion`、`Canva`、`Descript`、`Firecrawl`、`Parallel_Search`、`TinyFish`、`Opera_Browser_Connector`、`Alpha_Vantage`、`Binance`、`Longbridge`、`Montage`、`Metricool`、`vidIQ`、`DigitalOcean`、`Plugin_Management`。

这表示**存在可发现的接口**，不代表它们都已连接用户账号、用户已授权所有写入、具备任何特定订阅权益，或每次均可用。必须遵守当前调用时的工具 schema 和返回权限。用户已禁止未经批准增加额外付费服务。

子业务选择：财经可按授权使用市场/文档来源；A 股不能把普通财经文本搜索冒充已授权的同花顺 Level-2 数据；视频要区分媒体生成、剪辑和真实发布；小说的版权语料与业务 checkpoint 由小说子仓持有。父 UAOS 不能以跨域能力发现抢占子仓业务判断权。

## 4. Capability Discovery / Match / Verification

**能力查询**（已有工具注册/元数据可承担，不需复制第二份）至少判：
- Required capability：本次真的需要什么——读事实、生成文件、编辑媒体、交易行情、发送消息、写仓库？
- Input/Output Contract：必需参数、返回结构、附件与媒体格式、版本、速率/上下文限制；
- Owner & Authorization：只读/写、外部持久资产、敏感程度、同意/审批、风险/权限；
- Evidence Quality：当前实时性、来源真实性、完整性、是否可回读；
- Cost/Latency：免费与付费、交互耗时、可靠性；未知费用不自动支出；
- Reversibility：写入可撤销还是不可逆副作用；遇到 UNKNOWN 如何避免重放；
- Fallback Semantics：不同工具结果等价吗？替代操作会不会绕过拒绝或造成新风险？
- Domain Fit：是否满足子域专业数据与交付标准，不能只看“工具名字类似”。

### 示意四条路：文章研究
A 已有高质量资料直接撰写；B 当前授权网络查询；C 用户已连接的数据仓；D 工具不可用时继续结构分析并标缺。比较事实时效性、完整性、来源、成本、领域验收。不能把必须真实查询的数据“凭模型常识编造”。

### 示意四条路：受拒绝的代码合并
A 原 PR 流程通过 → 发布；B 仅测试与只读评估继续 → 暂缓受拒写入；C 用其他 API 绕过拒绝 → **禁止**；D 更换等价工程设计但仍需同样授权审查。路径多≠全部可用。

## 5. 多路求解的真正准则

“条条大路通罗马”不是让 Agent 每次列五个方法名；要有目标、条件、边界及可执行差异。

方法候选表应包含 `outcome / route / tools / assumptions / evidence / expected effects / nonfit / risks / authority / verification / fallback`。
- 若 A/B 同样达标，比较成本、速度和可靠性；
- 若一条路线不满足硬约束，不因为便宜而采纳；
- 若任一路线都不可行，标明确切阻碍，执行仍被允许的其他事项；
- 若用户已经合法明确指定工具，只在目标、权限和异常确有问题时重新提议其他路线；
- 若当前无需外部工具，NO_TOOL 是有效候选，不制造插件调用。

## 6. 插件编排错误清单及反例

P1 只凭插件名称猜测它有写入权限；必须询问或读取 capability contract。
P2 把工具搜索返回当已授权且可以直接操作；错误。
P3 同时派给多个工具执行同一不可逆操作导致重复侧效；正确应有协调事务/幂等身份。
P4 工具输出无出处、已过期但被提升为权威；须核查版本和可靠性。
P5 安全拒绝后换服务继续同一被禁止操作；违反边界。
P6 工具成功但文章/视频/推荐结果未达到子域业务要求；不能称产品交付已验收。
P7 购买额外 API/云服务而用户仅允许免费已有能力；应拒绝或取得明确批准。

## 7. 蒸馏候选

`K-TOOL-01`：**先匹配任务能力，再发现插件与授权；对每条可行路径比较效果、限制和可验证性。**
`K-ROUTE-02`：**多路线搜索允许 NO_TOOL、NO_CHANGE 和安全的非写入路径；禁止绕过明确安全拒绝。**
`K-EFFECT-03`：**外部工具返回“成功”后，对目标资产执行真实回读/验证；不可把提供者 API 状态当产品验收。**

## 8. 范围/饱和度

本轮已核对：2026 MCP 官方规范、Agent 作者工程文献、云运营、NIST 风险与交互测试、当前可用工具目录。未做：所有插件逐个外部授权测试、费用核价、四个业务子仓全工具运行态验证。没有权限则保留能力候选，不能生成假的“已装已用”收据。后续以新的任务能力要求驱动具体工具接口深入研究，尤其检查数据来源和授权，而不是先安装全部工具。
