# SmartKit

SmartKit distributes reusable agent capabilities while preserving each target repository's
ownership of its project-specific agent configuration.

## Language

**Harness（宿主）**:
An agent host application, such as Codex, Cursor, or GitHub Copilot, that loads and executes
SmartKit capabilities through its native interfaces.
_Avoid_: Platform, operating system, runtime

**Platform（平台）**:
An operating-system family, such as Windows, Linux, or macOS, on which a Harness and SmartKit run.
_Avoid_: Harness, agent host

**Harness Adaptation（宿主适配）**:
A plugin-private, Harness-scoped Rule that maps shared SmartKit actions to one Harness's native
tools, capabilities, lifecycle semantics, constraints, and missing-capability fallbacks.
_Avoid_: Platform adaptation, duplicated workflow policy

**Instruction Governance（指令治理）**:
The shared policy that defines Rule strength and precedence, Skill authority and overlap, and
semantic conflict resolution.
_Avoid_: Rule configuration, Skill Governance, workflow routing

**Third-Party Skill Policy（第三方技能政策）**:
SmartKit-owned behavioral constraints applied to Skills supplied by third-party plugins or external
sources without modifying their upstream content.
_Avoid_: Upstream Skill patch, project Skill policy, Skill Governance

**Workspace Policy（工作区政策）**:
The shared policy that selects the current checkout or an isolated linked worktree and governs local Git state,
commit authority, and remote actions independently of any Skill workflow.
_Avoid_: Skill configuration, worktree Skill, repository setup

**Plugin MCP（插件 MCP）**:
An MCP server distributed with the SmartKit plugin and made available through each supported
host's plugin integration.
_Avoid_: Global MCP, shared project MCP

**Project MCP（项目 MCP）**:
An MCP server declared by a target repository as canonical project configuration and rendered by
setup into the native configuration of each enabled host.
_Avoid_: Plugin MCP, hard-coded project template

**MCP Adapter（MCP 适配器）**:
A host-native MCP configuration generated from a canonical Plugin MCP or Project MCP declaration.
_Avoid_: MCP source, handwritten harness copy

**Managed Asset（受管资产）**:
A project file, directory tree, or structured field that setup may update or delete because its
identity and current digest are recorded in the SmartKit Ownership Manifest.
_Avoid_: User-owned asset, inferred-by-name asset

**SmartKit Ownership Manifest（SmartKit 所有权清单）**:
A target repository record of resolved external sources, digest-bearing managed assets, and
non-owned seeded documents.
_Avoid_: External Skill lock, Project MCP lock, migration ledger

**Configured MCP（配置交付型 MCP）**:
An MCP capability delivered as host configuration while its server remains owned by an external
package, remote service, or project runtime; SmartKit does not copy the server implementation merely
to distribute the configuration.
_Avoid_: Vendored MCP, installed MCP

**Vendored Plugin Skill（随插件内置的第三方技能）**:
A third-party Skill reviewed, licensed, locked, and copied into SmartKit before release because the
supported plugin hosts load Skills from plugin-local paths and do not share a remote Skill dependency
contract.
_Avoid_: Referenced Skill, runtime-fetched Skill

**Static MCP Readiness（静态 MCP 就绪性）**:
The configuration and local prerequisites that can be checked without starting an MCP server,
probing a remote endpoint, triggering authentication, or requiring an application runtime to be live.
_Avoid_: MCP health, live MCP availability

**Daily Project Check Gate（每日项目检查门控）**:
The first step of the automatic check pipeline, allowing at most one evaluation per canonical project
root, Harness, and local calendar day regardless of the number or outcome of downstream checks.
_Avoid_: Global daily check, per-check throttle, session throttle

**MCP Readiness Profile（MCP 就绪性检查配置集）**:
A typed, non-interactive static check set interpreted after the Daily Project Check Gate. Plugin MCP
declares it explicitly; Project MCP derives it from command paths and environment-variable names.
_Avoid_: MCP-specific Hook, arbitrary check script
