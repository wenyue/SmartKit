# 返回 Review

把交付提交头的净结果 materialize 到目标工作树，不推进其分支，也不改变其索引。
范围为**已交付**时，复核目标仍没有范围 diff，保持其工作树和索引不变，
保留源分支和工作树作为审查证据，报告证明和保留的状态，然后停止。

1. 记录目标 `HEAD`、索引树、已暂存改动、未暂存改动和未跟踪路径。在仓库外备份
   每个范围路径，并在清单中记录 original file types 和 absent 路径。
2. 从记录的目标边界与交付提交头树之间的完整 diff 推导已确认的结果。对没有
   目标本地改动的范围路径，先检查转移，然后只通过不改变索引的模式更新工作
   树。
3. 对重叠 text 路径，在 temporary files 中 three-way 合并 merge-base content、当前目标工作
   file 和已确认的结果。仅 pathname 相同只是 mergeable 证据，不是 conflict。
4. 只解决 unambiguous、范围-owned、verifiable merges。遇到 delete/modify conflicts、complex renames、
   binary conflicts、mutually exclusive 行为、ambiguous 生成的输出，或任何无法验证的结果时
   停止。只有项目提供 deterministic generator 且该修改已单独授权时，才从源重新生成
   生成的 files。
5. 只在目标检出目录中运行 known non-mutating checks。没有 adequate checks 时，报告 limitation，
   不运行 formatter、generator 或修复者。
6. 证明记录的目标 `HEAD` 和索引树未改变、original 已暂存状态已保留、merged files 同时包含
   compatible local 和已确认的 work，且 returned 范围改动为未暂存或未跟踪。
7. 保留源分支、工作树和外部 backup。报告其 locations，使源和恢复 data 在
   用户接受审查结果前仍可独立检查。

完整结果存在前转移失败时，只从外部 backup 恢复 touched 路径。转移后验证
失败时，保留 returned 结果和全部恢复 data 供 manual 审查。
