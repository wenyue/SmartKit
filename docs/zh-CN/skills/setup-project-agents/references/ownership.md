# 所有权

随附的 catalog 始终启用 Codex、Cursor、Copilot 和 Qoder。它安装所声明的共享 Rules 和 Skills、Codex Plugin Agent 默认配置，以及 catalog 声明的全部项目 blueprint。可选的项目配置可以增加外部 Skills、项目 Agents 和 MCP servers。

若 `.agents/config.json` 已存在，或已接受的意图需要非默认输入，应使用当前已加载插件随附的 `<skill-root>/../../setup-assets/catalog/project-config.schema.json` 中的 schema，在 `start` 前协调或创建这个归项目所有的文件。文件不存在时，使用随附默认值。该 schema 也适用于本地同步。外部 Skill 来源、项目 Agent 映射和 MCP 声明都通过它解析。

对于全量设置，`start` 会先依据所选的规范来源或已安装后备来源验证项目输入，再冻结请求。如果该来源拒绝按已加载 schema 准备的输入，应遵循[会话协议](session-protocol.md#preflight)：在已接受的权限内修正所报告的原因，并开始新的调用。返回的会话来源和请求保持不可变。

`.agents/rules/` 和 `.agents/skills/` 下的项目本地 Rules 与 Skills，包括 blueprint 生成的源文件及配套文件，都归项目所有，可以在会话之间编辑。设置流程发现并保留其他归项目所有的 Rules 和 Skills。项目 Agent 源文件也仍归项目所有。catalog 声明的 Codex Plugin Agent 默认配置属于后备配置，不是项目 Agent 声明。Cursor、Copilot 和 Qoder 的原生 Plugin Agents，以及原生插件的 Rules、Skills 和 MCP，不属于此工作流。

对于每个生成的项目 Rule 或 Skill，SmartKit 在 `.agents/smartkit.lock.json` 中记录契约指纹和准确的输出路径，包括配套文件；不持久保存这些文件的内容摘要。每次全量会话都会请求当前的完整契约集合。重新编写时，应读取当前项目证据和已有输出内容，保留有合格证据支持的意图。移除契约时，删除其记录的输出；重命名 catalog 目标时，退役原先记录的路径，并生成当前目标。新的完整交接中未再列出的配套输出会被退役；未记录的配套文件仍归项目所有。

项目同步保留生成的源文件和契约记录。全量设置会将项目 Agent 适配器、MCP 字段与共享及默认配置的所有权分开记录。完整的本地同步需要已建立的这类记录；所有权记录较旧或缺失时，必须先执行全量设置。删除或重命名本地声明时，它只移除记录中的项目映射。共享、默认和外部资产及其来源信息保持完整。外部 Skill 声明变化时，必须执行全量设置。

托管的渲染资产、共享资产和外部资产继续受到摘要保护。冻结会话的目标漂移检查适用于[会话协议](session-protocol.md)定义的目标输入范围。

SmartKit 只负责 `.agents/smartkit.lock.json` 中记录的文件和结构化字段，以及 `AGENTS.md` 中的一个 `## Project rules` 节。全量设置会渲染该节，范围截至下一个一级或二级标题，或文件末尾；该节不存在时则追加。围栏代码块中的标题不构成章节边界。重复的 Project rules 节、任何所有权冲突或摘要冲突，都会使设置流程在替换前停止。保留该节之外的每个字节，以及每个未声明的文件、字段、目录和秘密值。

MCP 环境字段填写环境变量名；URL、命令、参数和 override 中的字面量仍属于项目输入。不要推断任意字符串都是敏感信息。如果合格的仓库证据确认某个字面量确实敏感，应在渲染前停止，并请项目所有者改用受支持的间接引用。

设置流程将 MCP 就绪声明作为项目配置保留和验证。执行这些检查由就绪检查运行时负责。设置流程和项目同步都不运行就绪检查，也不安装依赖；干净结果仅证明配置已经收敛。
