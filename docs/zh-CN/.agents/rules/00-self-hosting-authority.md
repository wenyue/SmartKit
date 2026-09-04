# 自举来源权威

**强度：** Mandatory
**适用范围：**此 SmartKit 仓库中的每项任务。

本 Rule 仅负责自举副本的权威。对于每个独立适用的 SmartKit 或项目 Rule 或 Skill，只要当前
checkout 中存在对应来源，就必须使用该来源：

- SmartKit Rules：`rules/source/**`
- 项目 Rules：`.agents/rules/**`
- 插件清单暴露的 SmartKit Skills：`skills/<name>/**`
- 项目 Skills：`.agents/skills/**`

将用户未限定副本地提到的 SmartKit Rule 或 Skill 解析为上述当前 checkout 中对应的
来源。如果用户明确指定另一副本，则该引用改为指向所指副本。

只有当前 checkout 中不存在对应来源时，才以已安装、注入、打包或缓存的副本作为回退。对于解析到
checkout 的 Skill，必须从同一 checkout 来源树中读取其完整的 `SKILL.md` 及每个必需的引用资源。

副本解析保留通常的适用性、Rule 的强度与优先级，以及 Skill 的组合关系。必须保留每个独立适用的
Rule 和 Skill；解析一个制品的副本不能替代另一个不同的制品。

`.agents/rules/01-project-policy.md` 仍是规范所有权、契约与暴露、翻译、验证以及 authoring-Skill
例外的唯一所有者。
