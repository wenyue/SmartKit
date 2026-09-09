# Ownership

The shipped catalog always enables Codex, Cursor, Copilot, and Qoder. It installs its declared shared
Rules and Skills, the Codex Plugin Agent defaults, and every catalog-declared project blueprint.
Optional project configuration can add external Skills, project Agents, and MCP servers.

If `.agents/config.json` exists or accepted intent requires non-default inputs, use the schema
shipped with this loaded plugin at `<skill-root>/../../setup-assets/catalog/project-config.schema.json`
to reconcile or create this project-owned file before `start`. Its absence means shipped defaults.
This schema also governs local synchronization. Resolve external Skill sources, project Agent
mappings, and MCP declarations through it.

For full setup, `start` validates the project input against the selected canonical or installed
fallback source before freezing the request. If that source rejects input prepared under the loaded
schema, follow the [session protocol](session-protocol.md#preflight): correct the reported cause
within accepted authority and begin a fresh invocation. The returned session source and request
remain immutable.

The contents of project-local Rules and Skills under `.agents/rules/` and `.agents/skills/`, including
blueprint-generated sources and their supporting files, are project-owned and editable between
sessions. Setup discovers and preserves additional project-owned Rules and Skills. Project Agent
sources also remain project-owned. Catalog-declared Codex Plugin Agent defaults are fallbacks, not
project Agent declarations. Native Cursor, Copilot, and Qoder Plugin Agents, and native plugin
Rules, Skills, and MCP, are outside this workflow.

For each generated project Rule or Skill, SmartKit records the contract fingerprint and exact output
paths, including supporting files, in `.agents/smartkit.lock.json`; it stores no persistent digests of
those files' contents. Every full session requests the complete current contract set. Read current
project evidence and existing output content to preserve qualified intent during reauthoring. Removing a contract deletes
its recorded outputs; renaming its catalog target retires the old recorded paths and generates the
current destination. Supporting outputs omitted from a new complete handoff are retired; unrecorded
supporting files remain project-owned.

Project synchronization preserves generated sources and contract records. Full setup records project
Agent adapters and MCP fields separately from shared/default ownership. Broad local synchronization
requires this established record; older or absent ownership requires full setup first. It retires
only recorded project mappings on local declaration deletion or rename. Shared/default/external
assets and their provenance remain intact. External Skill declaration changes require full setup.

Managed rendered, shared, and external assets retain digest protection. Frozen-session target drift
checks apply to the consumed target surface defined by the [session protocol](session-protocol.md).

SmartKit owns only the files and structured fields recorded in `.agents/smartkit.lock.json`, plus
one `## Project rules` section in `AGENTS.md`. Complete setup renders that section through the next
heading of level one or two, or the end of the file, and appends it when absent. Headings inside
fenced code blocks do not define section boundaries. Duplicate Project rules sections or any
ownership or digest conflict stop setup before replacement. Preserve every byte outside the section
and every undeclared file, field, directory, and secret value.

MCP environment fields name environment variables; URL, command, argument, and override literals
remain project input. Do not infer that an arbitrary string is sensitive. If qualified repository
evidence identifies a real sensitive literal, stop before rendering and ask the project owner to
replace it with supported indirection.

Setup preserves and validates MCP readiness declarations as project configuration. Readiness runtime
owns execution of those checks. Setup and project synchronization neither run readiness checks nor
install dependencies; a clean result proves configuration convergence only.
