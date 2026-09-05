# 公共结果

为 `implement-tickets` 等调用方保留这些词汇。返回选定路径、`status`、`classification`、`causal_boundary`、
`history_result`、`outcome_result` 和 `cleanup_result`。每个阶段结果携带自身状态及证明它所需的证据或残余信息。
包含身份、准确的相关提交头与树或快照、适用时的验证与审查绑定、发布情况、保留位置，以及下一位负责人和动作。
无关细节应保持有界。

| 阶段状态 | 含义 |
| --- | --- |
| `not-started` | 阶段从未进入；标明作为原因的更早边界。 |
| `inapplicable` | 当前路径和历史策略不需要此阶段。 |
| `stopped` | 前置条件或保护条件拒绝阶段尝试，且完整观察证明未产生影响。 |
| `failed` | 已产生影响、影响仍不明确，或必需的操作后证明失败。 |
| `proven` | 历史或结果具有其路径要求的正面证明。 |
| `complete` | 清理为每个生命周期项给出了已授权的移除、保留或委派处置。 |

整体 `status: complete` 要求结果已证实、清理已完成。路径就绪前的拒绝，在 `causal_boundary: preflight` 返回
`status: stopped`；必需阶段保持 `not-started`，本来就不使用的历史阶段为 `inapplicable`。进入阶段后，整体状态
为作为原因的阶段的 `stopped` 或 `failed`，直到其未完成工作得到解决。历史尝试失败时，结果和清理保持
`not-started`。记录恢复或后续完成时，保留原始尝试及其因果结果。

分类表达独立证实的最强事实。从 `no positive result` 开始。历史证明增加 `history finalized`；已证实交接增加
`non-integrating handoff`；只有已证实的本地整合或**Already Delivered**才增加 `authoritative delivery`。
已证实丢弃使用 `explicit discard`。阶段停止或失败都不能抹去或提升此前正面事实。仅推送仍属于残余发布，
不是已证实的 PR 结果。

代表性的合法结果如下，阶段列依次为历史、结果、清理：

| 情况 | 状态 | 分类 | 阶段状态 |
| --- | --- | --- | --- |
| 有意保留未完成的脏工作 | `complete` | `non-integrating handoff` | `inapplicable`, `proven`, `complete` |
| 改动已转移，来源和备份保留 | `complete` | `non-integrating handoff` | `inapplicable`, `proven`, `complete` |
| 发布就绪前缺少审查 | `stopped` | `no positive result` | `not-started`, `not-started`, `not-started` |
| 历史已证实后、结果影响发生前目标移动 | `stopped` | `history finalized` | `proven`, `stopped`, `not-started` |
| 推送已证实，创建 PR 失败 | `failed` | `history finalized` | `proven`, `failed`, `not-started` |
| PR 已证实，保留的生命周期项已交接 | `complete` | `non-integrating handoff` | `proven`, `proven`, `complete` |
| 交付已证实，清理移除失败 | `failed` | `authoritative delivery` | `proven`, `proven`, `failed` |
| 转移部分应用，恢复受保护条件限制或不可执行 | `failed` | `no positive result` | `inapplicable`, `failed`, `not-started` |
| 准确授权的丢弃完成 | `complete` | `explicit discard` | `inapplicable`, `proven`, `complete` |

这些组合描述有因果关系的阶段，不只是最后一条命令的退出码。若某个子操作已经改变状态，该阶段后续未产生影响的
拒绝仍属于部分失败。在失败期间保留状态属于保护残余，并不因此证明选定结果或整次运行完成。反过来，交付后的清理
失败应保留权威交付，让调用方继续合法的交付后工作，而不重复整合。
