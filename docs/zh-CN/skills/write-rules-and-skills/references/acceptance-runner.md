# Acceptance Runner

此引用负责 Ordinary Artifact Acceptance 的通用隔离和执行协议。父 Skill 负责 Acceptance 何时开始
以及谁可以担任 Runner。选择的生命周期和语义类型引用负责代表性 case 和范围特定通过条件。

## 提供一个 Context Packet

向 Runner 提供运行时可见的冻结候选项、一个触发任务或政策应用、一个选定 case 输入，以及完整所需
上下文。不要在 packet 中提供预期结果、语义台账、diff、Author 推理、finding、Reviewer 指令或先前
case 输出。

每个 case 都使用新的 Soft-isolated Runner 及其声明的冻结输入。不要让一个 case 的结果成为另一个
case 的输入。当 Readiness 要求 Behavior Control 时，只在两者完成后比较其原始结果与匹配的候选项
运行；不要把任何一项结果暴露给另一个 Runner。

## 应用工件

默认使用无工具 Runner。当响应是 Rule 或写作或判断 Skill 的可观察结果时，在返回响应中应用它就是真实
Acceptance；把相同内容写入文件不会增加证据。

只有候选项的可观察契约需要真实效果时才提供工具。先通过 `soft-isolation.md` 中匹配的工具政策 Probe，
然后在 packet 中命名每个允许工具、输入、路径和效果。候选项归属的测试或 fixture 提供任何一次性
文件系统状态；编写工作流不创建通用 Acceptance 工作区。

可用时使用真实公共作业入口或政策应用 seam。通过公共入口运行归属的确定性资源。把环境无法运行的受
支持执行报告为未测试。受控 walkthrough 可以解释该表面，但不能替代要求的真实效果或建立机器 PASS。

每个 case 运行一次。对于不确定或不稳定的 case，最多使用新的 Soft-isolated Runner 重复一次；结果
分歧即失败。向 Reviewer 返回可观察结果以及已测试或未测试表面，但不根据未披露的预期结果自行判断。
不要持久化 Runner 输出或 case 报告。
