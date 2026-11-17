目标 {target} 的有效本地同步记录已授权启动同步。从当前 Hook 所属的插件安装中读取 <plugin-root>/skills/maintain-project-config/references/maintenance.md 的维护契约。

先执行 `update`，再执行不带 `--adopt-local` 的 `reconcile`。根据结果选择下一步动作：

| 结果 | 动作 |
| --- | --- |
| `source-updated` | 使用 `apply --accept-existing` 和精确检查指纹自动恢复。 |
| `in-sync` | 用 `apply` 记录一致状态。 |
| `needs-choice` 且为 `local_updates_only` | 展示变更路径和内容差异；询问将本地改动保存到配置仓库，还是暂不同步。 |
| 其他 `needs-choice` | 展示变更路径和内容差异；询问保存本地、使用配置仓库，还是暂不同步。 |
| 更新失败 | 保留双方并报告失败；不得继续应用。 |

接受保存即授权其精确范围内的正常提交和推送，无需再次确认。遵循维护契约中受保护的保存和发布流程。

暂不同步时保留本地文件和原同步记录；报告此结果并继续独立的原任务工作。按各自契约报告独立的 setup 前置条件和部分结果。
