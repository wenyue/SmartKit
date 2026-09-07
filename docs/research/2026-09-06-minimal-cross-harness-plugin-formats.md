# Minimal Cross-Harness Plugin Formats

Research date: 2026-09-06. Brainstorming evidence, not an accepted migration or
implementation plan. Current documentation and upstream source are not proof of
support in every released CLI/App build. No plugins or tools were installed.

## Conclusion

No single format is established here as preserving all SmartKit capabilities on
all target hosts. The accepted investigation goal is to minimize delivered plugin
formats and distinct loading paths while preserving required behavior. Generating
several formats from shared sources reduces editing but does not satisfy that goal
by itself. Keep existing ownership of VERSION, MCP, Rules, and Agents during this
investigation; no format migration has been authorized.

Agent Plugins 1.0 is a real package standard, not merely Agent Skills portability.
Its portable contract covers Skills and MCP only. It is distinct from legacy
OpenPlugin at `.plugin/plugin.json`, and from schema-less Copilot `plugin.json`.
Adding `$schema` changes discovery and semantics, not just validation. [S1], [S4], [S5]

## Host Evidence Matrix

"Unknown" means not established by this bounded research, not unsupported.
Manifest recognition does not establish component or execution equivalence.

| Host | Native/documented entry | Claude `.claude-plugin/plugin.json` | Legacy `.plugin/plugin.json` | Agent Plugins 1.0 |
| --- | --- | --- | --- | --- |
| Codex CLI | `.codex-plugin/plugin.json` [S2] | Upstream discovery test explicitly accepts it [S3] | Unknown | Upstream loader supports schema-marked root manifest; release floor unverified [S3] |
| Codex App | Same documented packaging; current docs refer to Codex in the ChatGPT desktop app [S2] | Shared Codex source evidence, not an App-build guarantee [S3] | Unknown | Shared-source evidence only; installed App support unverified [S3] |
| Cursor | `.cursor-plugin/plugin.json`; also standard root manifest [S7] | Not listed in the official two-format table; direct compatibility unverified | Unknown | Explicitly documented for Skills/MCP, not Cursor-specific components [S7] |
| GitHub Copilot CLI | Root `plugin.json`; reference lists additional paths [S4] | Explicit manifest lookup path | Explicit lookup path, checked before root manifest | Explicit schema opt-in documented |
| VS Code Copilot | Root Copilot manifest or schema-marked standard manifest [S5] | Explicit format and parser branch [S5], [S6] | Explicit legacy format and parser branch | Explicit support; Copilot components use `com.github.copilot` |
| Qoder CLI | `.qoder-plugin/plugin.json`; optional for convention-based local loading [S8], [S9] | Unknown: retrieved CLI documentation does not establish this alias | Unknown | Unknown: no conformance claim in retrieved CLI references |

Qoder IDE documentation separately advertises plugin Rules, Skills, Agents,
Commands, Hooks, and MCP. That capability listing is not evidence that its
manifest parser equals the CLI parser; this research does not establish IDE/App
format aliases. See retrieval scope below.

## Verified Primary Snippets

Short excerpts below are verbatim; surrounding interpretation is deliberately
narrow. These ten source groups are the decision evidence.

1. **[S1] Agent Plugins specification 1.0.0**, sections 5-9 and 11:
   "Agent Plugins v1 defines exactly two component types: **skills** and **MCP servers**."
   "Clients MUST ignore component types they do not support."
   Requires root `plugin.json` with
   `$schema: https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`, fixed
   `skills/` and `mcp.json`; client-specific behavior belongs in reverse-domain
   extension namespaces. A conformant client may support only one component type.
2. **[S2] OpenAI packaging documentation**, Plugin structure and Bundled MCP
   servers and lifecycle hooks:
   "Every plugin has a manifest at `.codex-plugin/plugin.json`."
   "Codex also sets `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` for compatibility with existing plugin hooks."
   Also documents `PLUGIN_ROOT/DATA`, default `hooks/hooks.json`, and explicit
   Hook review/trust. Its Claude *marketplace* compatibility is a separate fact.
3. **[S3] Codex upstream source**, commit
   `ac192cd7937b0d73edc6dffe009940ae53782dd4`:
   `uses_name_from_alternate_discoverable_manifest_path` sets
   `ALTERNATE_PLUGIN_CLA_MANIFEST_RELATIVE_PATH = ".claude-plugin/plugin.json"`
   and asserts `find_plugin_manifest_path(&plugin_root) == Some(manifest_path)`.
   `preserves_codex_claude_cursor_legacy_precedence` tests Codex before Claude;
   a separate test accepts Cursor's manifest too. Schema-marked root detection
   precedes legacy discovery. Crucially, `load_plugin` uses
   `if loaded_manifest.format == PluginManifestFormat::AgentPlugin { (Vec::new(), Vec::new()) }`
   for Hook sources/warnings. Thus this standard-format path supplies no Hooks.
   These are inspected code/tests, not tests run here or a released-version claim.
4. **[S4] Copilot CLI reference**, File locations and Open Plugin Spec support:
   "`.plugin/plugin.json`, `plugin.json`, `.github/plugin/plugin.json`, or `.claude-plugin/plugin.json` (checked in this order)"
   "Declaring the canonical `$schema` in `plugin.json` opts a plugin into the [Agent Plugins (Open Plugin Spec)](https://agent-plugins.org) v1.0.0 format, additively on top of standard plugin loading:"
   Documents Agents, Skills, Hooks and MCP path fields, plus persistent
   `COPILOT_PLUGIN_DATA` / `CLAUDE_PLUGIN_DATA`. Do not derive CLI Hook execution
   from VS Code source.
5. **[S5] VS Code plugin documentation**, Plugin formats and Cross-tool compatibility:
   "VS Code continues to support existing Copilot, Claude, and legacy OpenPlugin formats."
   "VS Code reads custom agents, slash commands, rules, and hooks from the `com.github.copilot` namespace, which GitHub Copilot CLI and the GitHub Copilot app also read."
   The root manifest's canonical schema selects Agent Plugins semantics.
6. **[S6] VS Code parser**, commit
   `3d7cfab6d77dce362755ac573a7a350e8f64528f`:
   Copilot `parseHooks` returns `parseHooksJson(hookUri, json, workspaceRoot, userHome)`.
   Claude/OpenPlugin instead call `interpolateHookPluginRoot`, which assigns
   `(hook.env as Record<string, string>)[envVar] = fsPath`.
   Detection is Agent Plugins first, then OpenPlugin, then Claude, then Copilot.
   Plain Copilot parsing therefore performs no root injection at this boundary,
   despite the documentation's broader variable table. This is not proof about
   every downstream runtime. Agent Plugins parsing also defers root handling.
7. **[S7] Cursor plugin reference**, Supported plugin formats:
   "Cursor loads plugins in two formats, identified by their manifest location:"
   The table lists root Agent Plugins for "Skills, MCP servers" and
   `.cursor-plugin/plugin.json` for "Skills, MCP servers, rules, agents, commands, hooks, variables".
   This is positive evidence for those two routes, not a claim that every
   undocumented compatibility route is impossible. No Claude manifest alias is
   established by this reference.
8. **[S8] Qoder CLI plugin reference**, Plugin Manifest:
   "The manifest file is located at `.qoder-plugin/plugin.json` and **must not be placed in the plugin root directory**."
   "This file is optional"
   It documents convention loading, custom Agents and Hooks, and `.mcp.json`
   with `mcp.json` fallback. Reading those components without a manifest would
   not prove Agent Plugins schema semantics or Claude metadata compatibility.
9. **[S9] Qoder CLI plugin guide**, Writing Plugin Hooks:
   "When executed, plugin Hooks receive two extra environment variables:"
   Its table names `QODER_PLUGIN_ROOT` and `QODER_PLUGIN_DATA`. The example uses
   `PreToolUse` with nested `matcher` / `hooks`; no Claude-root alias is established.
10. **[S10] Qoder IDE plugins**, Plugin components:
    "**Rules**" are "Behavioral and style constraints injected into AI context".
    "Installed plugins are available in both Editor and Quest."
    This is an IDE capability statement, not CLI Rules/format equivalence.

## Behavioral and Platform Limits

- Hooks remain host-specific: event names, matching, input/output and approval
  semantics matter even when the manifest loads. Cursor lists camelCase events;
  VS Code documents ignoring Claude matcher values. Its parser also lacks the
   SmartKit CLI keys `userPromptTransformed` and `preCompact`. [S5], [S6], [S7]
- Root placeholders and shell environment reads are different mechanisms.
  PowerShell uses `$env:PLUGIN_ROOT`, Bash uses `$PLUGIN_ROOT`; a literal
  `${PLUGIN_ROOT}` requires the appropriate host interpolation. Codex and Qoder
  document different native variable families. Cursor's standard MCP example
  uses `${PLUGIN_ROOT}`, but this research does not establish that same token's
   native Cursor Hook injection. [S2], [S7], [S9]
- Standard v1 guarantees `PLUGIN_ROOT/DATA` for stdio MCP subprocesses and
  expansion in `args`, `env`, `cwd`, not `command`; it does not standardize Hooks.
  A shared variable name is not a universal execution contract. [S1]
- SmartKit's current README promises four hosts on Windows/Linux, delivers
  Rules through Hooks except on Cursor, and keeps Codex Agents setup-managed.
  Codex's inspected loader loads Skills/MCP/Apps/Hooks, not custom Agents or a
  native plugin Rules component. Changing manifests does not remove that gap.
- No host was installed, upgraded, or runtime-tested. No minimum released version
  was verified for these format combinations. CLI, desktop App, IDE, remote
  execution, enterprise policy and OS availability must remain separate claims.
  In particular, the README's host support is not a new guarantee of every App
  surface on Linux. Current docs and `main` can be ahead of installed builds.

## Defensible Candidates, Not a Proven Minimum

| Candidate | What the evidence supports | Remaining cost or uncertainty |
| --- | --- | --- |
| Existing four native formats | Conservative baseline preserving explicit host routes; VS Code can recognize Copilot format | VS Code Hook behavior still needs separate validation; generate duplicate metadata rather than hand-maintain it |
| Claude + Cursor + Qoder (three) | Claude recognized by Codex source, Copilot CLI docs, and VS Code; native Cursor/Qoder routes retained | Shared Claude components and host-specific Hook behavior must be proven; Codex App/release floor unknown |
| Cursor + Copilot + Qoder (three) | Codex source also recognizes Cursor's manifest, offering another discovery-level grouping | Cursor/Codex Hook and MCP semantics differ; recognition is insufficient for SmartKit parity |
| Agent Plugins 1.0 + Qoder (two) | Plausible Skills/MCP-only grouping for Codex source, Cursor and both Copilot clients, plus native Qoder | Not equivalent to full SmartKit: Codex standard path drops Hooks; Cursor's standard path lacks its native extras |
| Agent Plugins alone, Claude alone, or legacy OpenPlugin alone | None established for full cross-host SmartKit | Qoder standard/Claude support and Cursor Claude support are unverified; do not convert missing evidence into exclusion |

These are candidates to evaluate against a capability acceptance matrix, not a
mathematical lower bound. Qoder's manifest-free loading and client extensions
also prevent inferring a minimum merely by counting documented file names.
One repository may carry several generated manifests; that is not one runtime
format. Additional markers can change parser precedence, including routing Codex
away from Hook-capable legacy loading or changing both Copilot clients at once.

For future evaluation, distinguish manifest discovery from preserved Skills,
MCP, Agents, Rule delivery and Hook behavior on each selected host/build/OS.
This note authorizes no migration, new adapter, or change of current contracts.

## Follow-up: Shared Entry Versus Shared Behavior

- Cursor explicitly supports Claude hook settings through third-party hook
   compatibility and maps event names. The documented inputs are Claude settings
   files, not proof of `.claude-plugin/plugin.json` package discovery. This requires
   the relevant third-party configuration feature. No retrieved source establishes
   whole-package Claude import as either direct loading or conversion. [S11]
- Qoder CLI explicitly permits manifest-free convention loading. Its marketplace
   `strict` option defaults to true and requires a manifest; `strict: false` relaxes
   that requirement. Therefore a shared package with Qoder convention loading is a
   candidate, not proof that Qoder reads Claude manifest metadata or custom paths.
   Enterprise ZIP distribution separately requires a `.qoder-plugin/` directory.
   Do not generalize the CLI candidate to every Qoder distribution route. [S8],
   [S9], [S12]
- `Claude + Cursor`, with Qoder CLI using convention loading, is consequently a
   two-manifest-format candidate, not an established two-loading-path solution.
   Shared Hook behavior and package metadata remain unverified. Three formats are
   not a proven lower bound.
- Adding a Claude manifest alone changes VS Code discovery but does not replace
   the existing Copilot CLI root manifest or Codex native manifest: their higher
   precedence still selects the existing entries. Codex's inspected legacy order
   is Codex, Claude, Cursor; Copilot CLI checks its root manifest before Claude.
   Multiple markers in one repository must be evaluated together. [S3], [S4], [S6]
- SmartKit currently fixes `--harness codex` or `--harness copilot` in separate
   Hook commands. This selects Rule scope, state, and response protocol. Copilot's
   `userPromptTransformed` uses `modifiedTransformedPrompt`; Codex prompt injection
   uses `UserPromptSubmit` and nested `hookSpecificOutput.additionalContext`.
   Merely sharing the Claude manifest does not translate these contracts. [S13],
   [S14], `hooks/codex.json`, `hooks/copilot.json`, `runtime/rules/dispatch.py`
- No common manifest-level host selector for Hook configuration was established.
   Combining host-specific events in one JSON is not itself evidence of a shared
   protocol: acceptance, missing events, duplicate execution, and runtime host
   selection all need verification. `CLAUDE_PLUGIN_ROOT` is a shared compatibility
   variable, not a reliable host identity. [S3], [S4], [S6], [S15]

The bounded next question is whether one Claude package can preserve Codex and
both Copilot clients' required behavior, followed by Cursor package recognition
and Qoder's selected distribution route. Required checks include discovery,
SessionStart script execution on Windows/Linux, prompt Rule delivery, tool Rule
decisions, compaction recovery, Agents, and MCP. Do not remove native entries
solely because an alternative manifest is discoverable.

## Retrieval Scope

The decision evidence above is bounded to ten primary-source groups (the Codex
group includes the adjacent discovery and loader files). Routing reads included
OpenAI's plugins overview, Cursor's overview, GitHub's creation guide, Qoder's
documentation index and publishing guide, and adjacent Codex manifest code.
Qoder `/plugins/overview` extraction failed and `/en/plugins/develop-plugins`
returned 404; the current index resolved the CLI/IDE pages cited above. Neither
failure is evidence of unsupported formats. No retrieved Qoder primary source
explicitly confirmed Claude manifest compatibility. The parent delegated research
through the available synchronous subagent tool; it was not background execution.

## Sources

[S1]: https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md
[S2]: https://developers.openai.com/plugins/build/plugins
[S3]: https://github.com/openai/codex/blob/ac192cd7937b0d73edc6dffe009940ae53782dd4/codex-rs/utils/plugins/src/plugin_namespace.rs
[Codex loader]: https://github.com/openai/codex/blob/ac192cd7937b0d73edc6dffe009940ae53782dd4/codex-rs/core-plugins/src/loader.rs
[S4]: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference
[S5]: https://code.visualstudio.com/docs/agent-customization/agent-plugins
[S6]: https://github.com/microsoft/vscode/blob/3d7cfab6d77dce362755ac573a7a350e8f64528f/src/vs/platform/agentPlugins/common/pluginParsers.ts
[S7]: https://cursor.com/docs/reference/plugins
[S8]: https://docs.qoder.com/cli/plugins-reference.md
[S9]: https://docs.qoder.com/cli/plugins.md
[S10]: https://docs.qoder.com/extensions/plugins.md
[S11]: https://cursor.com/docs/reference/third-party-hooks
[S12]: https://docs.qoder.com/account/enterprise/marketplace.md
[S13]: https://docs.github.com/en/copilot/reference/hooks-reference
[S14]: https://learn.chatgpt.com/docs/hooks
[S15]: https://code.claude.com/docs/en/plugins-reference#component-path-fields

Codex Hook and component-loading statements in S3 refer specifically to the
[Codex loader] at the same pinned commit.