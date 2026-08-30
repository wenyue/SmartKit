---
name: diagnose-agent-session
description: 诊断一个稳定智能体 Session 中疑似异常的 Token 或 API 等价费用消耗、模型或工具活动、子智能体协作、等待或未完成调用。
---

# 诊断 Agent Session

诊断一个已确定身份的智能体 Session 的稳定快照；该 Session 可以仍在进行，也可以已经完成。确定性包装脚本负责采集事实证据；随后回到以证据为依据的判断，根据任务上下文决定这些证据是否异常。包装脚本先完成 Tokscale 尝试并取得不可变的 Codex 本地日志内容，然后记录一个 UTC 快照截止时间，并只评估截止时间以内的内容。报告的截止时间之后不得再采集任何来源。不要保留任务回执，并且只在本次诊断期间读取转录内容。

## 运行证据包装脚本

调用包装脚本前，先把受支持的 client 和稳定 Session ID 解析为一对值。client 仅可为 `codex`、`cursor` 和 `copilot`，其中 `copilot` 表示 GitHub Copilot CLI。未知 client 不受支持。只有当 `CODEX_THREAD_ID` 提供当前 Codex thread 的身份时，Codex 才可以同时省略这两个标识符；不得推断其他身份，也绝不能选择最新日志。显式提供的受支持 client/Session 对可以指向另一个稳定 Session。如果这对值仍然不完整或缺失，应停止并向用户索取。

默认使用 `--scope both`；只有用户明确选择时才使用 `turn` 或 `session`。把包含当前已安装 `SKILL.md` 的目录解析为 Skill 根目录，然后通过相对于该根目录的路径调用包装脚本。公开支持的平台仅包括：

- 使用 `sh` 的 Linux：

  ```sh
  skill_root='<absolute directory containing the installed SKILL.md>'
  sh "$skill_root/scripts/task-metrics.sh" diagnose --scope both --client <client> --session-id <id>
  ```

- 使用 PowerShell 的 Windows：

  ```powershell
  $skillRoot = '<absolute directory containing the installed SKILL.md>'
  $wrapper = Join-Path $skillRoot 'scripts\task-metrics.ps1'
  powershell -ExecutionPolicy Bypass -File $wrapper diagnose --scope both --client <client> --session-id <id>
  ```

如果平台不受支持，应在运行包装脚本前停止。包装脚本负责解析 Python 3.10 或更高版本；只执行一次包装脚本尝试。如果缺少受支持的 Python，应保留这一明确错误，并把 Python 3.10+ 报告为恢复前提。只有沙箱导致的 Tokscale 失败可以重试一次；重试前必须取得宿主要求的批准，并在沙箱外执行完全相同的命令。
允许的尝试或重试完成后，其输出就是事实证据记录。

Tokscale 必须支持按 client 筛选、按 client/Session/model 分组，以及包装脚本所使用的标准化 JSON 字段；缺少或不兼容的能力是明确的失败证据，而不是进行版本猜测的理由。Cursor 用量可能依赖此前有效的 Tokscale 登录和已完成的同步。诊断过程既不读取也不存储凭据，不执行登录，也不静默同步；缺少设置或同步属于可恢复的前提。Copilot 用量依赖在被诊断活动开始之前配置好的 OTEL 文件导出；对于快照截止时间之前的活动，缺失的遥测是不可恢复的证据缺口。

## 证据契约

Tokscale 是整个 Session 用量和模型活动的共同来源。货币数值必须标注为 `estimated API-equivalent cost`；它们不是账单。Codex profile 还会读取当前 Session 的精确本地日志，从中取得当前 turn、工具调用、未完成调用、子智能体生命周期与协作以及等待证据。Cursor 和 Copilot 目前会把这些行为表面标记为不可用，同时保留所有 Tokscale 用量；这描述的是诊断 profile，而不是声称任一 harness 永远无法暴露这些信息。对于这些 profile，`both` 和显式 `turn` 仍会执行，并报告当前 turn 证据不可用，而不会借用其他 profile 的证据。

Cursor 和 Copilot 的 Tokscale Session 身份必须精确匹配。只有 Codex 可以接受精确 Session ID 或其唯一的 `rollout-{session-id}` Tokscale 别名；遇到重复别名或相互竞争的别名时必须拒绝，不得聚合归属不明确的证据。Tokscale 标准化与 Codex 本地日志文件的精确 Session 发现彼此独立，绝不允许借此选择最新日志。

每个 capability 条目必须严格使用 `available`、`unavailable` 或 `failed`，并附上相应证据或原因。至少覆盖 Session 用量、模型活动、当前 turn、工具调用、未完成调用、子智能体生命周期与协作以及等待。相同的 profile 契约并不意味着观察到的证据相同。某个表面失败时，仍须保留其他所有可用证据。

包装脚本报告是事实证据，不是任务健康状况判决。模型时长与工具时长的总和可能和经过时间重叠，生命周期计数是观察到的下界，只有存在稳定的子 Session 映射时才能归属子 Session 的 Token 用量。不得持久化 prompt、response、转录内容、工具输入或工具输出。

## 判断证据

把可靠证据与任务的预期工作以及适用的并发上限进行比较。只可使用任务上下文和对当前 turn 的直接了解来解释证据；绝不能填补缺失值。Token、调用、费用和时长仅用于描述，没有固定的异常阈值。必须且只能选择一种结论：

- 当存在任何可靠的异常证据时，选择**Abnormal evidence observed**，并把结论限定在该证据能够证明的范围内。
- 只有当请求涉及的每个相关 capability 都足够可用，且不存在异常信号时，才可选择**No abnormality observed**。
- 其他情况均选择**Inconclusive**。

Session 用量覆盖不能证明行为健康。缺失的行为证据不能转化为健康结果。

## 交付

按以下顺序返回一份报告：身份和请求的 scope；harness profile；capability 覆盖；整个 Session 的用量与 API 等价估算费用；turn、工具与协作证据；问题和不可用表面；由 Agent 撰写的三态总体结论；限制；恢复前提。如果在运行包装脚本前停止，应尽可能保留相同结构，并指出确切缺少的身份或平台前提。
