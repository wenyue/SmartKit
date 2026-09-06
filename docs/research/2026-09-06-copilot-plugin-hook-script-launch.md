# Copilot Plugin Hook Script Launch

Research date: 2026-09-06. Evidence only, not an accepted implementation.

## Findings

- Running bundled scripts from plugin hooks is officially supported. Use a
  quoted plugin-root path and the appropriate interpreter; workspace cwd is
  not the installed plugin root. [VS Code plugin documentation][vscode]
- Copilot CLI 1.0.26 release notes document injecting `PLUGIN_ROOT`,
  `COPILOT_PLUGIN_ROOT`, and `CLAUDE_PLUGIN_ROOT` into plugin hooks. PowerShell
  reads environment variables with `$env:PLUGIN_ROOT`, not `${PLUGIN_ROOT}`.
  The latter requires host substitution or an ordinary PowerShell variable.
  [Release notes][release]
- VS Code documents root expansion and environment injection for Copilot and
  legacy OpenPlugin. The inspected Copilot hook parser nevertheless calls
  `parseHooksJson` directly; OpenPlugin calls `interpolateHookPluginRoot`.
  This establishes a parser-path discrepancy, not behavior of every runtime.
  [Documentation][vscode], [pinned source][parser]
- `.plugin/plugin.json` is supported but is not VS Code-only. Current CLI
  documentation lists it before root `plugin.json` in lookup order. Adding
  it can change CLI routing too. [CLI file locations][cli]
- VS Code supports flat handlers and `bash`/`powershell` aliases. Its inspected
  event map does not recognize SmartKit's `userPromptTransformed` or `preCompact`
  keys. Whole-file reuse is therefore not established by command-field support.
  [Hook documentation][hooks], [parser source][parser]
- The inspected local-chat Windows executor explicitly selects Windows
  PowerShell in the normal Windows environment, with a `shell: true` fallback.
  A cmd.exe-only test does not prove this executor was exercised. [Executor][executor]

## Installed Host Evidence

The session header reports VS Code `1.136.1` and Copilot `0.64.1`.
The Hooks output log under the VS Code launch directory `20260906T184822`
records both SessionStart commands at 18:52:29-18:52:31 on 2026-09-06:

- The command uses `$env:PLUGIN_ROOT` and cwd is `d:\wenyue_agents`.
- The logged command configuration contains no `env` field.
- PowerShell reports that `\runtime\recommended-tools\check_recommended_tools.ps1`
  and `\runtime\rules\dispatch.ps1` are not recognized.

This confirms that the plugin-root value was empty during those actual hook
executions, before either script could start. These are existing failure logs,
not a fresh successful launch or proof that any proposed workaround works.
The unverified compatibility proposal was subsequently withdrawn; tracked files
were confirmed identical to HEAD and 19 focused manifest/version tests passed.

## Recommendation

Keep the investigation limited to SessionStart script launch. Preserve correct
CLI environment-variable syntax. Verify installed VS Code plugin-root propagation
with a minimal real-host probe before choosing a workaround. Do not treat a new
`.plugin` manifest as an isolated VS Code entry or expand into output-protocol
migration just to establish script execution.

The documented launch pattern is standard. Switching formats to compensate for
missing root injection is a compatibility workaround with cross-client effects.
No installed-host launch was tested in this research, and no claim is made that
upgrading to an unspecified version fixes the discrepancy. Plugin configuration
was not changed during this research.

## Sources

[vscode]: https://code.visualstudio.com/docs/agent-customization/agent-plugins#_plugin-environment-variables
[cli]: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference#file-locations
[hooks]: https://code.visualstudio.com/docs/agent-customization/hooks
[release]: https://github.com/github/copilot-cli/blob/d7ede79b9cbd4a76f64bb4b18a5731c4d008704b/changelog.md#L1565
[parser]: https://github.com/microsoft/vscode/blob/3d7cfab6d77dce362755ac573a7a350e8f64528f/src/vs/platform/agentPlugins/common/pluginParsers.ts
[executor]: https://github.com/microsoft/vscode/blob/3d7cfab6d77dce362755ac573a7a350e8f64528f/extensions/copilot/src/platform/chat/node/hookExecutor.ts#L183-L208