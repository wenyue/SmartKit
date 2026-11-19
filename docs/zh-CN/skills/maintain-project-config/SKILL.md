---
name: maintain-project-config
description: 维护随项目共享、仅保留在本机，或备份到独立个人配置仓库的项目 Agent 配置。
disable-model-invocation: true
---

# 维护项目配置

在业务项目中维护 Agent 配置。先在项目中验证，再将选定文件完整保存到配置仓库。

从已加载的插件确定此目录为 `<skill-root>`，业务项目为 `<target-root>`，`<skill-root>/scripts/maintain.py` 为 `<maintain>`。按选定操作阅读[项目配置维护](references/maintenance.md)中链接到的章节。命令或必需资源不可用时，报告缺失项并暂缓依赖它的工作。

## 1. 确定要执行的操作

```text
python "<maintain>" inspect --target "<target-root>"
```

检查读取维护模式、绑定、可查明的范围和差异，不拉取也不写入。保留两个 checkout 中已暂存、未暂存、未跟踪和未发布的工作。只要求检查时，报告发现和无法取得的证据后结束。

显式恢复时，按[来源选择和恢复流程](references/maintenance.md#restore-explicitly-or-synchronize-at-startup)执行并报告结果。恢复备份和保存本地改动各自需要授权。

项目尚未绑定时，一起呈现三种[维护模式](references/maintenance.md#choose-the-maintenance-mode)，取得用户选择后再[绑定](references/maintenance.md#bind-or-deliberately-change-a-source)。后续维护沿用有效绑定。若要在已有配置上初始化，比较实际内容，提出具体的替换方案并取得用户决定。首次导入配置仓库应在本地验证之后进行。

## 2. 在项目中编辑并验证

根据业务项目的证据确定改动内容和验证方式，编辑项目实际使用的配置文件。编写或修订 Rule 或 Skill 时，使用[编写 Rule 和 Skill](../write-rules-and-skills/SKILL.md)，将这些文件作为 Candidate，并提供符合要求的项目证据。

备份不可访问或同步选择尚未确定时，可以继续范围已知、已获授权且能独立完成的本地工作。对实际结果完成适用检查，包括任何[必要的生成](references/maintenance.md#render-local-configuration-only-when-required)。必要检查或生成受阻时，保留本地工作，报告缺少的验证，暂缓备份。

即使暂缓备份，也检查本地结果的 [Git 处理方式](references/maintenance.md#keep-personal-configuration-out-of-business-git)。报告已被 Git 跟踪的配置、尚未生效的排除规则，以及未满足的 setup 或迁移前提。两种本地模式均以经过验证的本地结果结束。

## 3. 备份经过验证的选定内容

保存到配置仓库已获授权时，新条目走[首次导入流程](references/maintenance.md#import-verified-files-into-a-new-entry)。已有绑定走[备份经过验证的改动](references/maintenance.md#back-up-verified-local-changes)，刚连接到已有条目的绑定也适用。记录一致状态后，验证最终范围的 Git 处理方式，再按[精确范围发布](references/maintenance.md#publish-an-exact-verified-scope)。

## 报告结果

报告模式、来源、已接受和保留的路径、已执行的检查，以及业务 Git 已跟踪的配置文件。适用时附上确切的提交和经验证的发布结果。后续步骤受阻时，保留已完成的工作，分别报告本地结果、已保存的备份、一致性记录、保留的提交和待完成的发布。
