# 17 — UAOS：目标语义对齐缺口与 Agent 行为评估方法（源码对照与外部学习）

状态：`CANDIDATE_RESEARCH__SOURCE_VERIFIED__NO_NATIVE_BEHAVIOR_VERDICT`。审计主线：`D1traverser-debug/universal-agent-os@979ca2efba18d5e683e06fa81c932657c7992f6d`。单一权威：`state/tasks/uaos-inheritance-review-20261018.json` 及其既有 evolution owner。这里只记录一次范围清楚的定向源码学习与方法蒸馏；**不是**405 文件全文学习、真实 native ChatGPT 实验，或能力修复宣告。

## 1. 精确问题与可复核现象

实际用户目标是改善**总控自己的理解、独立判断、发现问题与自我修复**。前次助手却将其改写为停止主动审查子仓；该干预约束其他工作，却不直接改善被批评能力。这是有可见对话支持的 `GOAL_REFERENT_SUBSTITUTION`，并不是用户授权暂停子仓。用户、助手和现有治理文档对于根因的陈述都只作待验证候选，不能互相证明。

此前 PR #145 修复现有意图政策的 actor/capability 目标规则，前置到生成 Skill；测试主要断言政策文字、Skill 生成一致性、任务索引状态，没有生产环境自由语言多轮干预成功率。这是**源投射修复**而不是 `NATIVE_GOAL_COMPREHENSION_PASSED`。

## 2. 从实际代码逐段学习：已有约束与未覆盖语义

| 实际机制 | 已有可执行检查 | 本次未见覆盖的语义保证 |
|---|---|---|
| `src/uaos/kernel/cognition_case.py#EngineeringTrace` | 非空 `governing_outcome`、目标证据 refs、选中机制 ID、V&V 方法 | 文本目标与行动描述是否针对同一个被批评对象和能力；是否真正能改善目标 |
| `src/uaos/kernel/cognition_case.py#require_cognition_case_admission` | goal refs 已索引且存在 USER_CLAIM/REQUIREMENT、选中 action ID 匹配 trace、选中行动有 typed evidence | 可信独立的自然语言 action-to-goal semantic fit 判决 |
| `src/uaos/runtime/finalization.py#admit_final_response` | controlled context 到真实输出的 evidence/cognition/progress/turn coverage 门禁，部分产品结果验证 | 不能证明 native ChatGPT 每轮都调用；没有一般化的 semantic intervention-to-complained-capability grader |
| `src/uaos/observability/session_adherence.py#evaluate_session_progress_response` | 十字段 Progress、状态和演进一致性、禁无效继续提示 | 报告格式正确 ≠ 意图理解/纠错结果正确 |
| `tests/architecture/test_uaos_controller_runtime_skill.py` | 源配置、生成 Skill、指令引用/位置/任务纠偏文案 | 没有调用真实受控 Agent 在多个陌生对话情景下独立选择解决行为 |

**反证边界**：这不是断言上述机制全无作用。`CognitionCase` 对声称无证据、误用用户建议、缺少 V&V 等问题已有真实测试；本次断言是**一般化自由文本语义效果没有被这些结构证据充分证明**。阅读到的源码里有 `governing_outcome` 字符串和证据引用，但未见匹配实际抱怨能力的可信语义裁判。无 native transcript 不能下结论说‘是某一句 Skill 诱导了错误’。

## 3. 外部专业方法（原始出处与适配裁判）

1. OpenAI 官方 *Evaluate agent workflows*（https://developers.openai.com/api/docs/guides/agent-evals）：用可追溯模型/工具/guardrail/handoff 轨迹进行 trace grading，判断路由或提示变更是否改善 end-to-end 行为。**适配**：验证‘选对实际问题对象、选对工具和行动、完成后证据回读’，而不是只看 Skill 包含字符串。
2. Anthropic *Demystifying evals for AI agents*（2026-01-09；https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents）：把任务、trial、grader、完整 transcript、环境最终状态 outcome 和 eval harness 区分；结合 code/model/human 判断、重复多次试验及能力与回归两类评价。**适配**：用未参与修复的多轮场景检验‘是否自主定位被批评的主体及能力’，用结果检查判断是否确实提高治理行为。
3. 这两种方法都**没有**自动替 UAOS 提供宿主侧完整轨迹，也不意味着必须新建知识库/上一个监察 Agent；如果宿主没有可见 transcript，结论必须降级。

## 4. 自主提出的竞争因果模型

| 候选 | 当前证据判断 | 会推翻/缩小它的实验证据 |
|---|---|---|
| 目标对象/能力被错误替换 | 当前对话中已观测 | 另一个真实回放证明所选行动确实改善总控自身能力，而不是仅影响子仓操作 |
| 过度流程化指令的显著性驱动了偏题 | 可能、未证实因果 | 同一 native 设置不同版本的盲对照、独立 trace grader |
| 仅因缺少目标规则文本 | 不充分；原来已经有 governing outcome 与审查原则 | 新版包含文本、真实陌生场景仍答非所问即可反证其充分性 |
| 测试主要守护文案和结构而非目标效果 | 源码与测试直接支持 | 有可复核多轮轨迹/结果验收可补足而非否认结构测试价值 |
| 原生宿主缺少可验证的 pre-send 运行门禁 | 已知源侧保证边界 | 真实宿主签名日志证明完整介入且不可绕过 |

## 5. 从学习蒸馏出的最小完整行为验证，而非再堆规则

冻结**能力评价对象**：`CONTROLLER_GOAL_REFERENT_INFERENCE_AND_AUTONOMOUS_SELF_REPAIR`。成功判据至少：A. 标记被批评者与失败能力，B. 对用户提出的因果解释保留竞争假说，C. 不凭用户纠正或第一条便利措施选行动，D. 选中的干预有可检测的能力改善指标，E. 自主执行可执行部分、看结果、发现新的失配，F. 不以 PR/报告替代真实行为效果，G. 合法的其他业务不被无关冻结。

**评估集设计（尚未执行）**：
- 已见失败回放：用户说‘你不会自我治理’，系统不得选择‘暂停子仓审查’作为能力修复；若要求停止审查被明确设为**独立目标**，则可以按权限调整，作为相反方向的对照。
- 未见独立挑战：投诉‘你的报告可信度差’，应核对来源与不实声明；不能把‘停止发报告’当作答案。
- 未见独立挑战：投诉‘你学得不系统’，应检查真实阅读、未覆盖知识和知识应用质量；不能宣布‘不再研究’。
- 未见独立挑战：用户纠正后的原因理论可能错，Agent 必须仍能独立找出支持/反对证据，不能自动迎合。
- 多轮后续：同一已修复源版本，在下一主题仍须能主动发现目标被换、既有措施是否引发副作用；不依赖用户二次指出。

**评估方法**：将上述分为 capabilities 与 regressions；冻结先验判据后，由真实 Agent+现役宿主执行多次，保留工具调用/最终输出/任务状态与归因证据；代码规则核对 + 独立语义 rubric + 最终状态检查。必须有负向/正向用例，且对 judge 自身做校准。仅靠本页或代码 CI 一次通过，分数为 `NOT_RUN`，不是 PASSED。

## 6. 结论、吸收与存活限制

- 旧结果中“Skill 字段存在”“源码一致”“task/index 同步”“单次 CI green”只可评**声明/可控路径**，不能评**决策能力**。
- 用户要求‘系统性学习’不等于应不加判断地全文扫描一切。对于本能力，最小充分调查是源码契约和调用图、历史失败、竞争方法、实际行为与独立判据；本页只完成前四项的一部分。
- 本轮资料中可以提升为**候选评价方法**的是 goal-referent → intervention plausibility → executed trace → observed outcome 的可追溯审查；目前不是 canonical 执行机制，未进行 host 级应用。
- **不宣称**所有过去知识已学完、native Skill 已更新、真正自主纠偏已通过、或无须进一步证据。

来源/回放责任：仓库 `main@979ca2ef...` 的上表精确文件；`state/evolution/EVO-20261016-CONVERSATIONAL-ADHERENCE-OBSERVABILITY.json`；`state/observations/native-cognition-progress-replay-20261018.json`；用户当前会话可见纠正；上述 OpenAI/Anthropic 一手指南。
