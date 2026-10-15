# SmartKit

SmartKit distributes reusable agent capabilities while preserving each target repository's
ownership of its project-specific agent configuration.

## Language

**Harness（智能体宿主）** :
An agent host application, such as Codex, Cursor, or GitHub Copilot, that loads and executes
SmartKit capabilities through its native interfaces.
_Avoid_: Platform, operating system, runtime

**Platform（操作系统平台）** :
An operating-system family, such as Windows, Linux, or macOS, on which a Harness and SmartKit run.
_Avoid_: Harness, agent host

**Harness Adaptation（智能体宿主适配）** :
A plugin-private, Harness-scoped Rule that maps shared SmartKit actions to one Harness's native
tools, capabilities, lifecycle semantics, constraints, and missing-capability fallbacks.
_Avoid_: Platform adaptation, duplicated workflow policy

**Instruction Governance（指令治理）** :
The shared policy that defines Rule precedence, Skill authority and overlap, and
semantic conflict resolution.
_Avoid_: Rule configuration, Skill Governance, workflow routing

**Workspace Policy（工作区管理规则）** :
The shared policy that selects the current checkout or an isolated linked worktree and governs local Git state,
commit authority, and remote actions independently of any Skill workflow.
_Avoid_: Skill configuration, worktree Skill, repository setup

**Plugin MCP（插件 MCP）** :
An MCP server distributed with the SmartKit plugin and made available through each supported
host's plugin integration.
_Avoid_: Global MCP, shared project MCP

**Project MCP（项目 MCP）** :
An MCP server declared by a target repository as canonical project configuration and rendered by
setup into the native configuration of each enabled host.
_Avoid_: Plugin MCP, hard-coded project template

**MCP Adapter（MCP 配置适配器）** :
A host-native MCP configuration generated from a canonical Plugin MCP or Project MCP declaration.
_Avoid_: MCP source, handwritten harness copy

**Managed Asset（受管理资产）** :
A project file, directory tree, or structured field that setup may update or delete because its
identity and current digest are recorded in the SmartKit Ownership Manifest.
_Avoid_: User-owned asset, inferred-by-name asset

**SmartKit Ownership Manifest（SmartKit 所有权清单）** :
A target repository record of resolved external sources, digest-bearing managed assets, and
non-owned seeded documents.
_Avoid_: External Skill lock, Project MCP lock, migration ledger

**Configured MCP（配置型 MCP）** :
An MCP capability delivered as host configuration while its server remains owned by an external
package, remote service, or project runtime; SmartKit does not copy the server implementation merely
to distribute the configuration.
_Avoid_: Vendored MCP, installed MCP

**Vendored Plugin Skill（插件内置第三方技能）** :
A third-party Skill reviewed, licensed, locked, and copied into SmartKit before release because the
supported plugin hosts load Skills from plugin-local paths and do not share a remote Skill dependency
contract.
_Avoid_: Referenced Skill, runtime-fetched Skill

**SmartKit Local Web Service（SmartKit 本机 Web 服务）** :
The shared user-local SmartKit host for application pages, feature data interfaces, and generated previews. Each presented feature retains ownership of its meaning and source data.
_Avoid_: Skill-specific server, native link handler

**Preview Artifact（预览产物）** :
A fixed SmartKit-generated output retained for human inspection, distinct from an application page whose displayed data can change. Its preview lifetime is separate from the lifetime of any canonical source material.
_Avoid_: Authoring Artifact, live application page

**Static MCP Readiness（MCP 静态就绪条件）** :
The configuration and local prerequisites that can be checked without starting an MCP server,
probing a remote endpoint, triggering authentication, or requiring an application runtime to be live.
_Avoid_: MCP health, live MCP availability

**Daily Project Check Gate（每日项目检查关口）** :
The first step of the automatic check pipeline, allowing at most one evaluation per canonical project
root, Harness, and local calendar day regardless of the number or outcome of downstream checks.
_Avoid_: Global daily check, per-check throttle, session throttle

**MCP Readiness Profile（MCP 就绪检查配置）** :
A typed, non-interactive static check set interpreted after the Daily Project Check Gate. Plugin MCP
declares it explicitly; Project MCP derives it from command paths and environment-variable names.
_Avoid_: MCP-specific Hook, arbitrary check script

**Project Setup Version（项目设置版本）** :
项目最近一次成功完成 setup 时使用的 SmartKit 发布版本，代表项目当前已完成的设置基线。
_Avoid_: 当前安装的插件版本、独立配置版本号、上一次尝试的版本

**Required Project Migration（必要项目迁移）** :
因 SmartKit 改变项目 setup 的要求、生成结果或读取方式，受影响项目必须完成的设置更新。
共享 Skill 更新和纯措辞修正本身不构成必要项目迁移。
_Avoid_: 插件版本不一致、每次插件升级、完整发布日志
