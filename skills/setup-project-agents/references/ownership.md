# Ownership

Read this before full setup or either local synchronization operation. The catalog and project
schema define supported inputs; recorded ownership determines which existing surfaces setup can
replace or retire. Preserve independently owned content even when it occupies a nearby path.

## Establish project inputs

The shipped catalog enables Codex, Cursor, Copilot and Qoder. It installs declared shared Rules and
Skills, Codex Plugin Agent defaults and every catalog-declared project blueprint. Optional project
configuration adds external Skills, project Agents and MCP servers.

When `.agents/config.json` exists or accepted intent needs non-default inputs, reconcile or create
that project-owned file before `start` using the loaded plugin's schema:
`<skill-root>/../../setup-assets/catalog/project-config.schema.json`. Absence means shipped defaults.
The same schema governs local synchronization and defines external Skill sources, project Agent
mappings and MCP declarations.

For full setup, `start` validates input against its selected canonical or installed-fallback source
before freezing the request. If that source rejects input prepared under the loaded schema, follow
[Preflight](session-protocol.md#preflight): correct the reported cause within accepted authority and
start a fresh invocation. The returned source and request stay immutable.

Project-local Rule and Skill contents under `.agents/rules/` and `.agents/skills/`, including generated
sources and their supporting files, belong to the project and can be edited between sessions.
Setup discovers and preserves additional project-owned Rules and Skills. Project Agent sources also
stay project-owned. Codex Plugin Agent defaults are fallbacks, not project Agent declarations.
Native Cursor, Copilot and Qoder Plugin Agents, and native plugin Rules, Skills and MCP, are outside
this workflow.

## Preserve the policy's loading meaning

Every direct `.agents/rules/*.md` file is an unconditional required Rule.
Numeric filename prefixes carry no category or precedence. The owned `AGENTS.md` section lists all
discovered paths in one required list.

Conditional policy belongs in a native `.agents/skills/rule-<domain>/SKILL.md`. Its frontmatter name
matches its folder, and its nonempty model-facing description supports discovery.
Ordinary project Skills keep their existing discovery behavior. Harness-native
plugin Rules retain their own loading policy.

Full setup and both local operations refuse explicit legacy conditional Rule declarations,
including old conditional index rows. Before retrying, separately authorize the source migration to
rule-led Skills and the update or removal of legacy `AGENTS.md` declarations. Setup does not silently
change when policy loads. Fenced examples are not operative index rows.

## Distinguish reauthoring from recorded retirement

For each generated Rule or Skill, `.agents/smartkit.lock.json` records its blueprint fingerprint and
exact output paths, including supporting files. It stores no persistent digests of their contents.
Every full session requests the complete current blueprint set; use existing content and current
project evidence to preserve qualified intent during reauthoring.

Blueprint removal retires its recorded outputs. A renamed catalog target retires old recorded paths
and generates the current destination. A supporting output omitted from a new complete handoff is
retired; unrecorded supporting files remain project-owned. Exact records bound retirement, so nearby
or apparently obsolete files do not acquire removal authority by association.

Project synchronization preserves generated sources and blueprint records. Full setup separately
records project Agent adapters and MCP fields from shared/default ownership. Broad local sync needs
that established record; an older or absent record requires full setup first. It retires only
recorded project mappings on declaration deletion or rename, keeping shared/default/external assets
and provenance intact. Changed external Skill declarations require full setup.

Managed rendered, shared and external assets retain digest protection. Within a frozen session,
setup-relevant target drift is governed by the [Full Session Protocol](session-protocol.md).

## Preserve unowned bytes and structured fields

SmartKit owns only files and structured fields recorded in `.agents/smartkit.lock.json`, plus one
`## Project rules` section in `AGENTS.md`. Full setup renders that section through the next level-one
or level-two heading, or file end, and appends it when absent. Fenced headings do not define section
boundaries. Duplicate Project rules sections, ownership conflicts or digest conflicts stop setup
before replacement.

Preserve every byte outside the owned section and every undeclared file, field, directory and secret
value. MCP environment fields name environment variables; URL, command, argument and override
literals remain project input. An arbitrary string is not evidence of a secret. When qualified
repository evidence identifies a real sensitive literal, stop before rendering and ask its project
owner to replace it with supported indirection.

MCP readiness declarations are project configuration to preserve and validate. Their runtime owner
executes checks. Setup and synchronization run no readiness checks and install no dependencies:
`clean` proves configuration convergence only.
