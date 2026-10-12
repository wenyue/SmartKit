# 项目迁移

生成项目内容前，读取 `start` 选定的条目。 `setup-assets/catalog/migrations.json` 中的机器可读声明标识哪些发布版本要求项目改变； SmartKit 发布了新版本，本身不要求迁移。按顺序，在一次完整 setup 中应用项目成功 `setupVersion` 之后、直至选定源版本的每项条目。无需安装中间插件版本。

已有 `.agents/smartkit.lock.json` 却没有 `setupVersion` 时，需要完整 setup 来建立基线。保留既有所有权记录和项目内容，不猜测之前的版本。没有该初始化记录的项目不会被 setup 检查拦截。

保留历史上的必要条目。每项条目解释变化及项目必须采取的动作；共享 Skill 变化和仅措辞修改不属于这里的内容。

## 项目更新与版本基线 <a id="project-refresh-and-version-baseline"></a>

**发布版本：1.2.19。** 蓝图现在区分经常更新的项目事实和稳定的流程决定。完整 setup 评估每个声明工件和项目 Agent，保留有效内容，不再要求换一套措辞。成功的 setup 记录其源发布版本。

执行一次完整 setup。根据每份蓝图的更新指引协调既有 Rules 和 Skills，保留项目补充及有效义务。发现自定义 Agents，将它们纳入权威项目配置时保留其行为，并评估模型与思考设置。解决报告的冲突，然后让成功的 `finish` 写入 `setupVersion`。