# 16 — UAOS 已观测消息原始角色防伪：源码证据、反证和最小完整修复

**Owner**：UAOS controller；当前唯一任务 `state/tasks/uaos-inheritance-review-20261018.json`。**审计对象**：受控 `src/uaos/runtime/epistemic_entry.py#admit_turn_evolution_coverage` → `src/uaos/runtime/finalization.py#admit_final_response`。**结论范围**：受信调用它的 Python 宿主；**不**证明 ChatGPT Native 存在非旁路 pre-send/pre-tool hook。方法来源：原有 UAOS turn coverage 实测，Cloudflare 研究中的 CSA-06/10（独立边界验证/Agent 低信任动作绑定），Paperclip 研究 PAP-01/12（运行身份/语义负向合约），均为**候选借鉴**，不是已提升 canonical。

## 1. 驱动目标与源码级事实

目标：在“逐条检查本轮真实消息 + 实际助手输出”的受控入口，防止 Agent 自报 `USER`、`TOOL`、`STATE` 角色，而真实来源属于另一身份，造成虚假的“已覆盖用户输入”“已审核工具观察”结论。

源代码以前：
1. `host_observed_source_refs` 比较与 `review.observed_source_refs` 的集合及数量，阻止普通漏条。
2. `verify_source_digest(ref, sha)` 能对**非最终回复的内容字节**验证，最终回复 SHA-256 由真实 `actual_assistant_response` 算出。
3. **漏洞**：`TurnUtteranceAssessment.origin` 完全来自待审查的记录；只检测“至少一个 origin=USER”，没有逐条向可信 host 核对消息最初的原始角色。
4. 反例：源集合 `session:user-1, session:tool-1, session:assistant-final` 的内容 digest 全都正确，Agent 把第 1 条标为 TOOL、第二条标为 USER；原路径对来源集合、digest、USER 数量、assistant digest 仍可满足并返回成功。更危险的精简反例：真实宿主只观察 TOOL + ASSISTANT，但 Agent 把 TOOL 当 USER，满足原有 user-presence 检查。
5. 这**不是**现有 ChatGPT 已实际遭到攻击的现场证明，而是该 Python 受控函数的身份绑定不变量缺失，源本身足以证明可构造。

## 2. 竞争解释、备选与所选机制

- **A：增加模型提示“别伪造角色”**：没有受信确认，不解决。拒绝。
- **B：只验证所有消息摘要**：当前已这样做；它证明字节/来源，不证明来源的 `USER/TOOL/STATE` 类型。拒绝为充分方案。
- **C：改造 Native ChatGPT 托管系统，实现强制不可旁路的 hook**：真实权限、宿主 API 与调用点均不可观测，也不是本仓能完成。不能虚称已部署；保留另一项真实能力缺口。
- **D：沿用唯一 `TurnEvolutionCoverage` 和 `FinalizationContext` owner，要求控制宿主在枚举 sources 时同时提供原始 `ref → UtteranceOrigin` 映射，集合完全一致、枚举类型严格、逐条相等，否则 fail-closed**：当前可实现、可负测，选。
- **E：新建统一事件监控/第二控制系统**：增加 authority 分裂、不解决受信接收方实际鉴权，拒绝。

## 3. 实施范围与来源信任

1. `admit_turn_evolution_coverage(..., host_observed_source_origins=...)` 使用受信调用者输入的 `Mapping[str, UtteranceOrigin]`；未传、非 Mapping、缺额外 ref、非枚举或 agent-origin 不符全拒绝。
2. 继续先做旧有 source/digest/assistant/user-presence 检查，再做 host-origin 核对，以保证既有缺消息和文本篡改回归仍报告最早真实的错误，安全强度不降低。
3. `FinalizationContext.observed_turn_source_origins` 只做受信宿主的传输；`admit_final_response` 将其交给已有 canonical gate，不创建额外身份裁决者。未传新参数的旧宿主 fail-closed；必须同时升级调用点。
4. 现有三个受控测试 fixture 用独立的宿主角色映射，不允许从 assessment 反向派生宿主输入（否则由同一低信任声明自证）。
5. **信任限制**：当宿主本身从 Agent 复制角色列表而不读取真实转录 metadata，这个 Python 检查仍会被绕过。不得把 `host_observed_source_origins` 的存在当作宿主真实性证书，更不能向 native ChatGPT 推导。

## 4. 冻结验收与赤绿回归

| ID | 场景 | 预期 |
| --- | --- | --- |
| HTO-01 | 工具/用户互换角色，所有真实 digest 未改 | 拒绝 `host origin mismatch` |
| HTO-02 | 真实只有 TOOL + ASSISTANT，Agent 伪造 USER | 拒绝 `host origin mismatch` |
| HTO-03 | 无宿主原始角色映射 | 拒绝 `independently observed host origins` |
| HTO-04 | 源 ref 映射缺失或额外混入 | 拒绝 `host origin enumeration` |
| HTO-05 | 以普通字符串 `"USER"` 冒充类型化枚举 | 拒绝 `typed origins` |
| HTO-06 | 正常 USER/TOOL/ASSISTANT + 正确 digest | 允许受控原路径通过 |
| HTO-07 | 缺消息、伪摘要、改最终回复、自评价未验证、未获许可完成 | 维持原负测路径 |
| HTO-08 | 既有受控 finalization、blocked-operation、product-outcome | 传宿主角色后不退化 |
| HTO-09 | 任意生产声称“Native 全消息/所有工具均硬拦截” | **禁止**；仍 `NATIVE_UNVERIFIED` |
| HTO-10 | PR frozen head 通过 GitHub promotion-gate 且 main readback | 源码受控验证，非 Native 完全验证 |

**赤灯证据**：PR #137 初始测试先于入口实现，旧签名因新宿主-origin 参数报 `TypeError`，GitHub Actions run 39163876309 = 11 failed / 627 passed / 2 skipped。这仅证明新契约尚不存在；漏洞机理另由源中的自报 `origin` 与 host verifier 未覆盖角色构成，不将 TypeError 冒充真实 exploit。第二轮有功能 638 passed / 2 skipped、因 `finalization` 未传参及治理门禁未齐而未能晋升，随后逐层修复。

**成本与接受规则**：只用仓库 CI、既有 pytest，不启动外部 Agent、付费模型、真实 ChatGPT hook 或 provider write。报告需要区分受控源+tests / GitHub CI / 主分支回读 / 实际 Native 用户会话四个等级。

## 5. 剩余风险与下一实际任务

- 宿主可信来源和角色枚举仍不能从 GitHub 代码获得完整 Native 激活证明；未知 host API 前无证据可安装该拦截。
- 当前 `EntrySignal` 的语义分类仍可能由 Agent 作错；本修复只绑定**身份/来源**，不是保证认知判断本身正确。应使用独立 judge/holdout 检验其他声明，不以本次身份修复泛化为自动自我治理。
- 继续 UAOS 五仓深审：已有 controller review 的 source evidence 不等于真实跨域行为验证；给下一个高风险场景独立而有负向结果的 host/provider 验收。Fin Writing 原态继续 RUNNING，但本次不修改其业务资产。

状态：**受控候选修复，等待保护分支 CI / main 回读；真实 Native/跨域应用尚未验证。**
