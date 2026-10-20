# Structure

Use this Rule for placement and responsibility decisions in the SmartKit repository. Resolve the paths below from the repository root.

## Keep feature context together

Place implementation, policy data, and other private resources with the feature that interprets them. Prefer an existing feature directory over a new top-level category based only on file type. For example, recommended-tool policies belong in `runtime/recommended-tools/policies/`: checking and maintenance consume the same feature's decisions.

Extract shared support when existing independent consumers need the same capability and its responsibility is clear. Keep each consumer's selection, interpretation, and task-specific behavior with that consumer; share the common mechanism. Prospective reuse alone does not justify another shared directory.

Extract long Agent behavior instructions from runtime code into the owning feature's `prompts/` directory. Keep generated metadata, tables and short diagnostics in code. Resolve prompts from the installed feature's location, independently of the target working directory, and handle unavailable resources through the consuming Hook or command's error contract before recording successful delivery.

## Choose by execution role

Use `runtime/<feature>/` for implementation and resources that Hooks need, including a persistent service started by a Hook, and `hooks/` for Harness lifecycle wiring. Other consumers may reuse those Hook-required capabilities. A shared command entry point alone does not establish runtime ownership; manual invocation and local state changes do not change an existing Hook responsibility.

Keep Hook-required read-only parsing and project-state inspection in runtime, with Skills reusing those mechanisms. Runtime must not import or invoke Skill implementation. It may read supported Skill-owned data and documentation or name Skill commands in its output; command execution remains with the consuming workflow under the command's authorization requirements.

Use `scripts/` for tools that maintain SmartKit's own sources and distribution metadata, such as repository-wide synchronizers. Keep a Skill's documentation, helpers and assets under that Skill. Other Skills may consume explicitly supported resources there through the plugin paths and loading requirements defined in [Project Policy](project-policy.md); sharing does not require a new `shared/` directory.

Project configuration maintenance belongs to [Maintain Project Config](../../skills/maintain-project-config/SKILL.md), including its reference, commands and engine for updating project configuration. [Setup Project Agents](../../skills/setup-project-agents/SKILL.md) consumes that lower-level capability for full setup. Keep this dependency one-way: maintenance must not depend on setup's implementation, command routes or workflow invocation.

Keep reusable plugin Rules and Skills in `rules/` and `skills/`, and SmartKit's own maintainer guidance in `.agents/`. Keep target-project setup blueprints, templates, and catalogs in `setup-assets/`; they describe future target assets rather than this repository's active Rules.

## Find the owning input

The capability directories can contain both canonical inputs and generated output. Use these routes to locate the input for a change; the registries and owning generators contain the live membership and exact output lists.

| Area | Canonical inputs | Derived output and owning tool |
| --- | --- | --- |
| Plugin Agents | `agents/source/` and `agents/registry.json` | `agents/<harness>/`, through `scripts/sync_agent_adapters.py` |
| Plugin MCP | `mcp/registry.json` | `mcp/<harness>.json`, through `scripts/sync_mcp_adapters.py`; external server implementations remain outside this configuration boundary |
| Third-party Skills | Source declarations in `skills/registry.json` and patches in `vendor/patches/` | Selected `skills/` snapshots, `licenses/`, and `vendor/external-skills.lock.json`, through `scripts/update_external_skills.py` |
