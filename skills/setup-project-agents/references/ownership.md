# Ownership

Read this before full setup or either local synchronization operation. The catalog and project schema define supported inputs; recorded ownership determines which existing surfaces setup can replace or retire. Preserve independently owned content even when it occupies a nearby path.

## Establish project inputs

The shipped catalog enables Codex, Cursor, Copilot and Qoder. It installs declared shared Rules and Skills, Codex Plugin Agent defaults and every catalog-declared project blueprint. Optional project configuration adds external Skills, project Agents, MCP servers and supported project-level host settings.

When `.agents/config.json` exists or accepted intent needs non-default inputs, reconcile or create that project-owned file before `start` using the loaded plugin's schema: `<skill-root>/../../setup-assets/catalog/project-config.schema.json`. Absence means shipped defaults; a missing `maintenance` choice remains readable and is resolved during explicit full setup. The same schema governs local synchronization and defines external Skill sources, project Agent mappings, MCP declarations and supported host settings. Settings currently address structured fields in `.codex/config.toml` and `.cursor/cli.json`; their renderer preserves undeclared fields.

The target's `maintenance` declaration selects where portable configuration is authored. Local mode keeps existing project canonical inputs. Repository mode selects one personal private GitHub repository, branch and entry; the source entry owns its declared configuration files and portable `skills`, `agents`, `mcp` and `settings` values. Read [Project Configuration Maintenance](../../../runtime/project_config/maintenance.md) before binding or working with a repository source. Use the business project's evidence while editing that source, then apply it through the supported route.

The binding, `setupVersion`, ownership records and runtime state remain target-local. `.agents/project-config-state.json` records applied-source evidence; it does not authorize replacement of setup-owned assets. Source files may include generated project Rule and Skill sources, but exclude delivered plugin assets, external snapshots, native adapters and generated indexes. The source copy of `AGENTS.md` excludes setup's generated `Project rules` section; the owning renderer maintains that section in the target.

`setupVersion` is the last successful full setup's SmartKit release, not the currently installed plugin version or a record of this user's runtime state. The public workflow writes this one field only after CodeGraph readiness, configuration convergence and private-session cleanup. Preparation, failure and local synchronization leave the prior value intact. Preserve the other project configuration values; never advance the field by hand to silence a hook. Session hooks use the project setup record to require a fresh local CodeGraph check, rather than treating this durable version as proof that a runtime is still ready.

For full setup, `start` validates input against its selected canonical or installed-fallback source before freezing the request. If that source rejects input prepared under the loaded schema, follow [Preflight](session-protocol.md#preflight): correct the reported cause within accepted authority and start a fresh invocation. The returned source and request stay immutable.

Project Rule and Skill contents under `.agents/rules/` and `.agents/skills/`, including generated sources and their supporting files, belong to the project. In local mode they can be edited there between sessions; in repository mode edit the declared source copies and apply them back. Setup discovers and preserves additional project-owned Rules and Skills. Project Agent sources follow the same selected authoring location. A target edit is preserved as a difference until explicitly adopted; it is not an automatic update to the source. Codex Plugin Agent defaults are fallbacks, not project Agent declarations. Native Cursor, Copilot and Qoder Plugin Agents, and native plugin Rules, Skills and MCP, are outside this workflow.

Project custom Agents discovered in native host directories must be reconciled during full setup, including undeclared ones. The `native_source` harness branch preserves a complete native document under `.agents/agents/` and copies it verbatim to its adapter; that source alone owns its prompt and settings. It is exclusive with structured settings for that harness. A shared prompt `source` is required only for harnesses using the structured branch. Existing recorded plugin defaults retain their owner. The adoption helper's guarded import preserves independent canonical content and existing adapter digest protection; it does not authorize rewriting an ownership record. In repository mode, it saves the accepted canonical native sources and portable Agent declaration to the entry before its guarded target transaction, retaining source evidence when target recovery is needed.

## Preserve the policy's loading meaning

Every direct `.agents/rules/*.md` file is an unconditional required Rule. Numeric filename prefixes carry no category or precedence. The owned `AGENTS.md` section lists all discovered paths in one required list.

Conditional policy belongs in a native `.agents/skills/rule-<domain>/SKILL.md`. Its frontmatter name matches its folder, and its nonempty model-facing description supports discovery. Ordinary project Skills keep their existing discovery behavior. Harness-native plugin Rules retain their own loading policy.

Full setup and both local operations refuse explicit legacy conditional Rule declarations, including old conditional index rows. Before retrying, separately authorize the source migration to rule-led Skills and the update or removal of legacy `AGENTS.md` declarations. Setup does not silently change when policy loads. Fenced examples are not operative index rows.

## Distinguish reauthoring from recorded retirement

For each generated Rule or Skill, `.agents/smartkit.lock.json` records its blueprint fingerprint and exact output paths, including supporting files. It stores no persistent digests of their contents. Every full session requests the complete current blueprint set; use existing content and current project evidence to preserve qualified intent during assessment and any necessary revision. An unchanged complete handoff preserves exact bytes.

Blueprint removal retires its recorded outputs. A renamed catalog target retires old recorded paths and generates the current destination. A supporting output omitted from a new complete handoff is retired; unrecorded supporting files remain project-owned. Exact records bound retirement, so nearby or apparently obsolete files do not acquire removal authority by association.

Project synchronization preserves generated sources and blueprint records. Full setup separately records project Agent adapters and MCP fields from shared/default ownership. Broad local sync needs that established record; an older or absent record requires full setup first. It retires only recorded project mappings on declaration deletion or rename, keeping shared/default/external assets and provenance intact. Changed external Skill declarations require full setup.

Managed rendered, shared and external assets retain digest protection. Within a frozen session, setup-relevant target drift is governed by the [Full Session Protocol](session-protocol.md).

## Preserve unowned bytes and structured fields

Setup owns only files and structured fields recorded in `.agents/smartkit.lock.json`, plus one `## Project rules` section in `AGENTS.md`. A configuration-source declaration remains subject to those owners; it cannot turn a delivered or rendered asset into an independently replaceable source. Full setup renders that section through the next level-one or level-two heading, or file end, and appends it when absent. Fenced headings do not define section boundaries. Duplicate Project rules sections, ownership conflicts or digest conflicts stop setup before replacement.

Preserve every byte outside the owned section and every undeclared file, field, directory and secret value. MCP environment fields name environment variables; URL, command, argument and override literals remain project input. An arbitrary string is not evidence of a secret. When qualified repository evidence identifies a real sensitive literal, stop before rendering and ask its project owner to replace it with supported indirection.

MCP readiness declarations are project configuration to preserve and validate. Their runtime owner executes checks. Full setup additionally prepares and verifies CodeGraph through the public `setup-codegraph` command and rechecks readiness at finish, as specified in [Full Session Protocol](session-protocol.md). That scoped preparation may install the CodeGraph package and create or update the target's local index and runtime state; preserve existing data and unrelated configuration. SmartKit's plugin MCP registry and adapters retain ownership of CodeGraph's MCP declaration. Use this preparation route instead of CodeGraph's broad host installer, which can rewrite independently owned host configuration.

Other MCP dependencies and runtime checks remain with their owners. Local synchronization performs no dependency installation or runtime preparation, and its `clean` result establishes configuration convergence only. CodeGraph databases, process state and logs are local runtime evidence, not transferable proof of readiness or project setup-version content.
