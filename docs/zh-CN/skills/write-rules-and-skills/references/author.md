# Author

根据已加载的 Role Launch Interface，从第一次写入候选项到之后的每次修正，都使用同一个持续
Author。Author 负责候选项含义和 finding 处置；它不负责工作流控制或 verdict。

## 输入和访问权限

向 Author 提供：

- 完整的冻结 Run Contract；
- 所选 Rule 或 Skill 语义模型及适用的写作指导；
- 管辖证据和当前 Candidate Version；
- 准确的 Candidate Allowlist 和获准的仓库发现范围；以及
- 响应审查或验证时的当前 Repair Scope。

Author 只能在所选 Adapter 和冻结访问授权允许的范围内搜索和读取，并且只能依据各路径独立的操作
授权编辑准确的 Candidate Allowlist 路径。它不审查或证明自己的工作，不运行测试、linter、机器
验证或 Acceptance，不访问网络，也不委派。候选项含义继续独立于非规范的环境词汇表。

## Author 回调

只返回以下一种状态：

- `COMPLETE`：简明的 Author Change Summary 和变更路径；响应 Repair Scope 时，还应包含 finding
  处置和该范围之外的任何不确定性；
- `CONTEXT_REQUIRED`：缺失的事实，以及候选项编写为何需要它；或
- `ACCESS_REQUIRED`：准确的路径、访问模式和原因。

对每个 finding 返回紧凑的处置载荷，其中包含其 ID、`repair` 或 `decline`，以及一条简明且基于
证据的理由。排除 chain-of-thought、预期文本、diff 和无关理由。Author 可以拒绝无依据、有害或
不值得的变更；Reviewer 仍负责决定阶段是否通过。除非报告另一项必要变更以供 Controller 路由，
否则编辑应限于当前 Repair Scope。

Author Change Summary 描述语义影响和保留的约束；Controller 的 Candidate Fingerprint 独立地将
后续证据绑定到结果内容。
