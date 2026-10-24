# Structure

Place SmartKit code and guidance with the responsibility they serve. Resolve all paths below from the repository root.

## Keep a feature's context together

Keep implementation, policy data, and private resources with the feature that interprets them. Prefer an existing feature directory to a new top-level category based only on file type. For example, recommended-tool policies belong in `runtime/recommended-tools/policies/` because both checking and maintenance consume that feature's decisions.

Extract shared support when existing independent consumers need the same capability and its responsibility is clear. Share the mechanism while retaining selection, interpretation, and task-specific behavior with each consumer. Prospective reuse alone does not justify a shared directory.

Move long Agent behavior instructions out of runtime code into the owning feature's `prompts/` directory; keep generated metadata, tables, and short diagnostics in code. Resolve prompts from the installed feature rather than the target working directory. An unavailable resource must follow the consuming Hook or command's error contract before successful delivery is recorded.

## Let execution responsibility determine placement

| Responsibility | Location and boundary |
| --- | --- |
| Hook-required implementation and resources, including a persistent service started by a Hook | `runtime/<feature>/`; `hooks/` supplies Harness lifecycle wiring. Other consumers may reuse the capability. |
| Maintenance of SmartKit's own sources and distribution metadata | `scripts/`, including repository-wide synchronizers. |
| A Skill's documentation, helpers, and assets | Its Skill directory. Other Skills may consume explicitly supported resources through the routes in [Project Policy](project-policy.md); sharing does not require a new `shared/` directory. |
| Portable plugin Rules and Skills | `rules/` and `skills/`. |
| SmartKit maintainer guidance | `.agents/`. |
| Future target-project blueprints, templates, and catalogs | `setup-assets/`; these are not this repository's active Rules. |

A shared command entry point alone does not establish runtime ownership. Manual invocation or local state changes do not change an existing Hook responsibility.

Keep Hook-required read-only parsing and project-state inspection in runtime so Skills can reuse it. Runtime must not import or invoke Skill implementation. It may read supported Skill-owned data and documentation or name Skill commands in output; the consuming workflow executes those commands under their authorization requirements.

Project configuration maintenance belongs to [Maintain Project Config](../../skills/maintain-project-config/SKILL.md), including its reference, commands, and update engine. [Setup Project Agents](../../skills/setup-project-agents/SKILL.md) consumes that capability for full setup. Keep the dependency one-way: maintenance must not depend on setup implementation, command routes, or workflow invocation.

## Find canonical inputs among derived files

Capability directories may contain both source and generated output. Use these routes to find the owning input; the registries and generators hold live membership and exact output lists.

| Area | Canonical inputs | Derived output and owning tool |
| --- | --- | --- |
| Plugin Agents | `agents/source/` and `agents/registry.json` | `agents/<harness>/`, through `scripts/sync_agent_adapters.py` |
| Plugin MCP | `mcp/registry.json` | `mcp/<harness>.json`, through `scripts/sync_mcp_adapters.py`; external server implementations stay outside this configuration boundary |
| Third-party Skills | Source declarations in `skills/registry.json` and patches in `vendor/patches/` | Selected `skills/` snapshots, `licenses/`, and `vendor/external-skills.lock.json`, through `scripts/update_external_skills.py` |
