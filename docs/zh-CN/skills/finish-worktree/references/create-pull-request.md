# 创建 Pull Request

发布 verified delivery head，并保留其本地 worktree 供 follow-up。scope 为 **Already Delivered** 时，
复核 resolved pull-request base 仍没有 scope diff，保留 source branch 和 worktree，报告 proof 和
skipped publication，然后停止，不 push，也不创建 empty pull request。

1. 解析准确 remote、base branch、head branch、pull-request title、body 和 draft state。repository
   evidence 和 accepted request 无法确定任何值时询问。
2. 再次确认 source worktree clean、resolved pull-request base 是完整 owned range 要求的 history
   boundary，并且 review 和 verification 仍 current。moved base 返回 finalization。
3. 不 force 地 push 准确 source branch，然后通过 available host-native 或 repository-authorized
   interface 创建 pull request。
4. 验证 remote branch commit、pull-request base 和 head、draft state 及返回 URL。
5. 保留本地 source branch 和 worktree 供 review updates。把后续 published review-fix commits 保留为
   review history；由 repository 的 pull-request policy 负责 repository-host finalization。只有之后
   单独授权 completion outcome，才移除 local state。
