---
name: maintain-project-config
description: 维护随项目共享、仅保留在本机，或备份到独立个人配置仓库的项目 Agent 配置。
disable-model-invocation: true
---

# 维护项目配置

在业务项目中修改并验证配置。使用配置仓库时，将验证过的文件备份并推送到选定的仓库。

`<target-root>` 指业务项目，`<maintain>` 指已加载插件中的 `skills/maintain-project-config/scripts/maintain.py`。按当前操作查阅[项目配置维护](references/maintenance.md)的相应章节。

1. **在本地修改并验证。** 如果初始化会覆盖已有配置，先请用户[确认替换内容](references/maintenance.md#choose-the-maintenance-mode)，再开始编辑。根据项目自身的实际情况修改，使用项目的检查方式验证。修改 Rule 或 Skill 时，以项目实际使用的文件为候选稿，按[编写 Rule 和 Skill](../write-rules-and-skills/SKILL.md)操作。需要生成配置时执行[本地生成](references/maintenance.md#render-local-configuration-only-when-required)。如果备份不可用或冲突阻碍同步，继续完成已授权且可独立进行的本地工作。
2. **按所选模式保存。** 沿用项目现有绑定。尚未绑定时，先向用户列出三种[维护模式](references/maintenance.md#choose-the-maintenance-mode)。选择任一本地模式时，工作在项目内完成。使用配置仓库时，[保存并推送验证过的改动](references/maintenance.md#back-up-verified-local-changes)，或[将文件导入新条目](references/maintenance.md#import-verified-files-into-a-new-entry)。必要检查或保存失败时，保留本地改动，并说明停在哪一步。

即使暂缓保存，也要检查 [Git 如何处理这些文件](references/maintenance.md#keep-personal-configuration-out-of-business-git)。报告变更文件、验证结果、尚缺的前提条件，以及备份或推送的实际结果。

用户只要求检查时，[检查](references/maintenance.md#choose-the-maintenance-mode)完即结束。用户明确要求恢复时，按[恢复流程](references/maintenance.md#restore-explicitly-or-synchronize-at-startup)操作。
