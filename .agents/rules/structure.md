# Structure

Use this Rule for placement and responsibility decisions in the SmartKit repository. Resolve the paths below from the repository root.

## Keep feature context together

Place implementation, policy data, and other private resources with the feature that interprets them. Prefer an existing feature directory over a new top-level category based only on file type. For example, recommended-tool policies belong in `runtime/recommended-tools/policies/`: checking and maintenance consume the same feature's decisions.

Extract shared support when existing independent consumers need the same capability and its responsibility is clear. Keep each consumer's selection, interpretation, and task-specific behavior with that consumer; share the common mechanism. Prospective reuse alone does not justify another shared directory.

## Choose by execution role

Use `runtime/<feature>/` for installed-plugin implementation reached by Hooks or shared resource entry points, and `hooks/` for Harness lifecycle wiring. A runtime operation may be invoked manually or change local state; those properties do not make it a repository-maintenance tool.

Use `scripts/` for tools that maintain SmartKit's own sources and distribution metadata, such as repository-wide synchronizers. Keep a Skill's private helpers and assets under that Skill. Move them to shared runtime support only when actual consumers justify that boundary.

Keep reusable plugin Rules and Skills in `rules/` and `skills/`, and SmartKit's own maintainer guidance in `.agents/`. Keep target-project setup blueprints, templates, and catalogs in `setup-assets/`; they describe future target assets rather than this repository's active Rules.

## Find the owning input

The capability directories can contain both canonical inputs and generated output. Use these routes to locate the input for a change; the registries and owning generators contain the live membership and exact output lists.

| Area | Canonical inputs | Derived output and owning tool |
| --- | --- | --- |
| Plugin Agents | `agents/source/` and `agents/registry.json` | `agents/<harness>/`, through `scripts/sync_agent_adapters.py` |
| Plugin MCP | `mcp/registry.json` | `mcp/<harness>.json`, through `scripts/sync_mcp_adapters.py`; external server implementations remain outside this configuration boundary |
| Third-party Skills | Source declarations in `skills/registry.json` and patches in `vendor/patches/` | Selected `skills/` snapshots, `licenses/`, and `vendor/external-skills.lock.json`, through `scripts/update_external_skills.py` |
