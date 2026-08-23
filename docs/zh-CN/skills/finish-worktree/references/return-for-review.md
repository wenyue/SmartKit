# 返回 Review

把 delivery head 的净结果 materialize 到 target working tree，不推进其 branch，也不改变其 index。
scope 为 **Already Delivered** 时，复核 target 仍没有 scope diff，保持其 working tree 和 index 不变，
保留 source branch 和 worktree 作为 review evidence，报告 proof 和 preserved state，然后停止。

1. 记录 target `HEAD`、index tree、staged changes、unstaged changes 和 untracked paths。在仓库外备份
   每个 scope path，并在 manifest 中记录 original file types 和 absent paths。
2. 从 recorded target boundary 与 delivery head tree 之间的完整 diff 推导 accepted result。对没有
   target-local changes 的 scope paths，先检查 transfer，然后只通过不改变 index 的 mode 更新 working
   tree。
3. 对重叠 text paths，在 temporary files 中 three-way merge merge-base content、当前 target working
   file 和 accepted result。仅 pathname 相同只是 mergeable evidence，不是 conflict。
4. 只解决 unambiguous、scope-owned、verifiable merges。遇到 delete/modify conflicts、complex renames、
   binary conflicts、mutually exclusive behavior、ambiguous generated output，或任何无法验证的结果时
   停止。只有项目提供 deterministic generator 且该 mutation 已单独授权时，才从 source 重新生成
   generated files。
5. 只在 target checkout 中运行 known non-mutating checks。没有 adequate checks 时，报告 limitation，
   不运行 formatter、generator 或 fixer。
6. 证明记录的 target `HEAD` 和 index tree 未改变、original staged state 已保留、merged files 同时包含
   compatible local 和 accepted work，且 returned scope changes 为 unstaged 或 untracked。
7. 保留 source branch、worktree 和 external backup。报告其 locations，使 source 和 recovery data 在
   用户接受 review result 前仍可独立检查。

完整结果存在前 transfer 失败时，只从 external backup 恢复 touched paths。transfer 后 verification
失败时，保留 returned result 和全部 recovery data 供 manual review。
