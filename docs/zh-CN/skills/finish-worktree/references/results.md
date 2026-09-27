# 公共结果

返回任何结果前读取本文件。`implement-tickets` 等调用者依赖这些字段名和值。报告所选路线、`status`、`classification`、`causal_boundary`、`history_result`、`outcome_result` 和 `cleanup_result`。

每个阶段结果包含其状态及支持证据或残留。提供确切的相关身份、头提交/树或快照、适用时的验证/审查绑定、发布、保留位置和下一责任方/行动。细节以足以证明结果并支持继续处理为界。

## 描述各阶段

| 阶段状态 | 含义 |
| --- | --- |
| `not-started` | 从未进入该阶段；指出更早的因果边界。 |
| `inapplicable` | 所选路线及历史策略不需要该阶段。 |
| `stopped` | 前置条件或保护拒绝了尝试，完整观察证明其未产生效果。 |
| `failed` | 已产生效果或效果仍含糊，或必需的效果后证明失败。 |
| `proven` | 历史或结果已有其路线特定的正面证明。 |
| `complete` | 清理已为每个生命周期项目安排有权实施的删除、保留或移交。 |

路线就绪前的拒绝产生 `status: stopped` 和 `causal_boundary: preflight`。必需阶段仍为 `not-started`；本来就不使用的历史为 `inapplicable`。进入阶段后，总体状态遵循其因果上的 `stopped` 或 `failed` 状态，直到未完成工作得到解决。历史尝试失败时，结果和清理保持 `not-started`。记录恢复或后续完成时，保留原尝试及其因果结果。

总体 `status: complete` 要求结果已证明且清理已完成。单靠命令退出码不能确定这些阶段状态。如果较早子操作改变了状态，即使后续保护拒绝本身无效果，该阶段仍已部分产生效果，应为 `failed`。

## 保留最强的已证明结果

分类从 `no positive result` 开始。历史证明支持 `history finalized`；已证明交接支持 `non-integrating handoff`。只有已证明的本地集成或**Already Delivered**支持 `authoritative delivery`。已证明丢弃使用 `explicit discard`。

后续停止或失败不能抹去或升级一个已独立证明的事实。仅推送成功只算残留发布，不是已证明 PR 结果。失败中的保留保护残留，但本身不能证明所选结果或完成整次运行。反过来，权威交付在清理失败后仍成立，使调用者能够继续有依据的交付后工作，而不再次集成。

下表说明此契约。阶段列依次列出历史、结果和清理。

| 情况 | 状态 | 分类 | 阶段状态 |
| --- | --- | --- | --- |
| 有意保留脏状态的未完成工作 | `complete` | `non-integrating handoff` | `inapplicable`, `proven`, `complete` |
| 修改已传输，源和备份保留 | `complete` | `non-integrating handoff` | `inapplicable`, `proven`, `complete` |
| 发布就绪前缺少审查 | `stopped` | `no positive result` | `not-started`, `not-started`, `not-started` |
| 历史已证明后、结果效果前目标移动 | `stopped` | `history finalized` | `proven`, `stopped`, `not-started` |
| 推送已证明，PR 创建失败 | `failed` | `history finalized` | `proven`, `failed`, `not-started` |
| PR 已证明，已交接保留的生命周期项目 | `complete` | `non-integrating handoff` | `proven`, `proven`, `complete` |
| 交付已证明，清理删除失败 | `failed` | `authoritative delivery` | `proven`, `proven`, `failed` |
| 传输部分应用，还原受保护条件阻止或不可用 | `failed` | `no positive result` | `inapplicable`, `failed`, `not-started` |
| 确切已授权丢弃完成 | `complete` | `explicit discard` | `inapplicable`, `proven`, `complete` |
