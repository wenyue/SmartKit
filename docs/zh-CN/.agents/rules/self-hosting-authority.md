# 自举来源权威

## 为每个工件选择来源

对于每个独立适用的 SmartKit 或项目 Rule 或 Skill，只要当前 checkout 中存在对应来源，
就必须使用该来源：

- SmartKit Rules：`rules/*.md`
- 项目 Rules：`.agents/rules/**`
- 插件清单暴露的 SmartKit Skills：`skills/<name>/**`
- 项目 Skills：`.agents/skills/**`

用户提及 SmartKit Rule 或 Skill 而未限定副本时，将其引用解析为上述 checkout 来源。
如果用户明确引用另一副本，则选择其指定的副本。

只有当前 checkout 中不存在对应来源时，才以已安装、注入、打包或缓存的副本作为回退。
读取失败不能证明来源不存在：现有来源也可能无法访问或读取。
当必需内容仍不可用时，按照核心治理的加载要求报告缺失内容，并停止依赖它的工作。

对于解析到 checkout 的 Skill，必须从同一来源树中读取其完整的 `SKILL.md` 及每个必需的引用资源。

## 保持政策职责边界

来源选择不改变通常的适用性、Rule 的优先级，以及 Skill 的组合关系。必须保留每个独立适用的
Rule 和 Skill；选择一个工件的副本不能替代另一个不同的工件。

`.agents/rules/project-policy.md` 仍是规范所有权、契约与暴露、翻译及验证的唯一所有者。
