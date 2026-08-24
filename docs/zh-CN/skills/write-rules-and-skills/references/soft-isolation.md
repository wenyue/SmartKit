# 软隔离

此引用负责 Soft-Isolation Probe 资格认定和 Context Packet 边界。软隔离是经过验证的行为边界，不是
文件系统、进程或对抗性安全沙箱。

## 认定 fresh-Agent 启动

每个顶层编写工作流在第一个 Soft-isolated Agent 前运行一个一次性、无工具 Probe。不要跨父运行或
fresh-Agent 启动机制复用其结果。

启动前，在父级可见对话中放置随机 history control，但不要把它加入 Probe prompt。选择答案只存在于
每个可用的源项目 Rule 正文、SmartKit 全局 Rule 正文、Harness Rule 正文和完整 Skill 正文中的确切
问题；不要把答案放入 prompt。还要在 Probe prompt 中放置另一个随机 prompt control。

启动一个不继承 turns 的 fresh Agent。指示它只使用初始上下文，不调用工具、不读取文件、不委派、
不推断，并返回：

- prompt control；
- parent history control 或 `UNKNOWN`；
- 每个 Rule 和 Skill 正文问题的答案或 `UNKNOWN`；
- entry-file 内容、Rule pointer 或 Skill catalog metadata 是否可见；以及
- 它是否使用了工具、文件读取、推断或委派。

`PASS` 要求精确的 prompt control，history control 和每个可用正文问题均为 `UNKNOWN`，且没有
工具、文件读取、推断或委派。entry-file 内容及其中的 Rule 或 Skill pointer，以及 Skill catalog
中的名称、description 或位置可以可见；Probe 不得继续读取这些 pointer，也不得把它们当成 packet
输入。任何被引用的 Rule 正文、完整 Skill 正文、不可用的 fresh 启动、格式错误的结果或其他不匹配
都是 `FAIL`。遇到 `FAIL` 时停止并警告；绝不降级到普通 Agent 或同一对话中的新 prompt。

## 构建一个 Context Packet

Context Packet 包含一个角色的完整语义输入：

- 其单一角色、请求结果和输出 schema；
- 与该角色相关的已接受意图和候选项内容；
- 选择的证据，以及每份必需 Rule、Skill 或引用的完整正文；
- 角色编写内容时的显式文件内容和 canonical target identity；
- 仅在角色的可观察任务需要时提供的允许工具和路径；以及
- 适用的完成、停止和失败结果。

不要用工作区路径替代内容。packet 不完整时，无工具 Agent 返回 `CONTEXT_REQUIRED`，并指出缺失事实
及其用途。控制器可以停止，或者使用完整替换 packet 启动新的 fresh Agent；它不会向现有角色对话追加
材料。

把 packet 和角色结果保留在当前 Agent 上下文。不要持久化 packet manifest、prompt、attestation、
台账或 verdict report。

## 认定例外工具访问

只有候选项的可观察契约无法在没有工具的情况下测试时，Acceptance Runner 才接收工具。在该 case 前，
使用相同有效工具可用性和只需要显式所给目标的任务重复 Probe。该工具政策 Probe 只能对该目标使用
已声明工具；`PASS` 要求它不读取或使用未声明上下文。工具政策 Probe 失败或无法验证时停止工作流。
