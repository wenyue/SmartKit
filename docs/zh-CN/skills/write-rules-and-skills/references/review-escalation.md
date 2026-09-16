# 审查升级

只加载审查结果或条件所选中的分支。Controller 负责协调这些分支，但不代替 Author 或 Reviewer 作出专业判断。

## 需要 Independent Review

当 Integrated Reviewer 返回 `INDEPENDENT_REVIEW_REQUIRED` 时，结束该身份，并在当前指纹上启动三个全新的 Independent Reviewer。Integrated 的结论不能替代 Independent Review 的结论，也不能让新的 Reviewer 带着预设判断开始审查。这次切换替代本轮的 Integrated 尝试，不另算一轮修复。如果切换或处理其原因需要扩大写入范围、访问权限或其他权限，则返回 `NEEDS_INPUT`。

## 修正 Author brief 或请求用户输入

当负责 Correctness 的审查身份证明 Author brief 遗漏或曲解了用户意图时，只在 finding 及其引用证据限定的范围内修正 brief，然后交回同一个 Author，对 Candidate 进行一次连贯修复。brief 由 Controller 负责，但语义结论不由 Controller 作出。把这次修复视为下一轮，并照常经过 Author 返回门槛、指纹、验证和审查流程。

如果权威上下文无法消除实质性的意图歧义，把 Reviewer 的问题原样提交给用户，不得代为解释，并返回 `NEEDS_INPUT`。

## 需要运行时证据 <a id="runtime-evidence-required"></a>

当负责 Correctness 的审查身份返回 `RUNTIME_REQUIRED` 时，先对照已冻结任务和现有授权检查请求，再在派发前冻结场景、尝试次数与资源边界、测试条件和验收标准。请求超出已冻结任务时返回 `NEEDS_INPUT`。启动一个独立 Runner，并向其提供 [Runner 角色](runner.md)；请求需要普通非盲测运行时检查时，仍保留这条路径。

进行行为测试时，启动一个全新的任务执行 Agent，只向其提供 Candidate 及版本、正常任务请求与材料，以及必要的执行、权限和观察采集约束。验收标准和预期输出留在 Controller 与 Correctness 一侧。继承的上下文、提示、fixture、相邻文件和会话记录引用中，都不得包含 Author brief、设计讨论或历史、Reviewer finding、预期行为、评分标准或仅供审查方掌握的场景设计理由。采集要求应描述需要观察什么，不得暗示预期答案。每个独立场景和每次重试都应使用全新上下文，避免先前案例或答案造成干扰。宿主的基础指令和工具仍然适用；应记录其相关限制，不得声称已经完全隔离。

安排访问条件，使普通任务中的决策、工具使用、提问和已授权的一次性 fixture 修改能够正常进行，同时保持 Candidate 不可变并保护无关状态。启动前，确认宿主具备所需的隔离、采集、终止和清理能力。Runner 将观察结果直接发送给提出请求的审查身份，只有该身份的 Correctness 视角可以作出判断。

每次 Runner 尝试都必须先安全结束，才能使用其观察结果。提出请求的审查身份还要从 Correctness 视角判断 Runner 返回的 `NEEDS_INPUT`、`BLOCKED` 或不完整观察：缺少必要的用户控制输入或权限时返回 `NEEDS_INPUT`；无法在已冻结任务内取得必要证据时返回 `BLOCKED`，包括缺少必要的隔离或采集能力。只有在冻结边界和现有授权内，针对 Correctness 指出的未决问题，并有新证据或不同方法时，才能派发额外尝试。达到边界后，不得反复运行直到 `PASS`；验收仍须具备必要证据。
