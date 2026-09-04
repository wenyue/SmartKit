# Controller 的条件审查编排

只加载审查结果或条件所选中的分支。Controller 负责协调这些分支，但不代替 Author 或 Reviewer 作出专业判断。

## 需要 Independent Review

当 Integrated Reviewer 返回 `INDEPENDENT_REVIEW_REQUIRED` 时，结束该身份，并在当前指纹上启动三个全新的 Independent Reviewer。Integrated 的结论不能替代 Independent Review 的结论，也不能让新的 Reviewer 带着预设判断开始审查。这次切换替代本轮的 Integrated 尝试，不另算一轮修复。如果切换或处理其原因需要扩大写入范围、访问权限或其他权限，则返回 `NEEDS_INPUT`。

## 修正 Author brief 或请求用户输入

当负责 Correctness 的审查身份证明 Author brief 遗漏或曲解了用户意图时，只在 finding 及其引用证据限定的范围内修正 brief，然后交回同一个 Author，对 Candidate 进行一次连贯修复。brief 由 Controller 负责，但语义结论不由 Controller 作出。把这次修复视为下一轮，并照常经过 Author 返回门槛、指纹、验证和审查流程。

如果权威上下文无法消除实质性的意图歧义，把 Reviewer 的问题原样提交给用户，不得代为解释，并返回 `NEEDS_INPUT`。

## 需要运行时证据

当负责 Correctness 的审查身份返回 `RUNTIME_REQUIRED` 时，其请求应说明场景、输入、权限和可观察条件。如果请求符合已冻结的任务，启动一个独立 Runner，并向其提供 [Runner 角色](runner.md)的指针。Runner 把观察结果直接发送给同一个审查身份，并且只有该身份的 Correctness 视角可以作出判断。超出已冻结任务的请求应返回 `NEEDS_INPUT`，不得就地扩大权限。

每次 Runner 尝试都必须先安全结束，才能使用其观察结果。提出请求的审查身份还要从 Correctness 视角判断 Runner 返回的 `NEEDS_INPUT`、`BLOCKED` 或不完整观察：缺少必要的用户控制输入或权限时返回 `NEEDS_INPUT`；无法在已冻结任务内取得必要证据时返回 `BLOCKED`。只有在现有权限范围内，并且出现新证据或有望取得进展的新方法时，才能重试。
