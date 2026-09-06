# PowerShell Plugin Hook Examples

Research date: 2026-09-06. Primary-source, bounded inspection; no plugin was
installed or executed. This is evidence and advice, not an accepted design change.

## Conclusion

This inspection did **not** verify a reputable, widely adopted public plugin
whose bundled Copilot CLI or VS Code hooks implement their behavior in native
PowerShell `.ps1` files. It also did not verify a plugin-specific PowerShell
launch wrapper. This is a limited search result, not proof that none exist.
Official PowerShell hook configuration examples do exist. Do not confuse that
supported capability with demonstrated adoption by a named plugin.

Do not switch to Bash solely because a famous plugin uses it. For Windows-native
Copilot support, PowerShell remains a documented option. Superpowers is a useful
precedent when deliberately accepting Git Bash and maintaining Bash logic across
platforms, but its wrapper does not repair missing plugin-root propagation.

## Three Verified Comparisons

### 1. VS Code: official PowerShell example, not a shipped plugin

The official [OS-specific commands example][vscode-hooks] contains these exact
properties:

```json
"command": "./scripts/format.sh",
"windows": "powershell -File scripts\\format.ps1",
"linux": "./scripts/format-linux.sh",
"osx": "./scripts/format-mac.sh"
```

Scope: a `PostToolUse` hook in general workspace/user hook documentation. The
page does not supply the `.ps1` implementation or establish a named plugin using
it. This is an explicit PowerShell launch command, not verified native hook
business logic. The same page documents mapping Copilot CLI `powershell` to
`windows`, and `bash` to `osx`/`linux`. Selection follows the extension-host OS,
which may differ from the desktop OS under WSL, SSH, or containers.

The [plugin documentation][vscode-plugins] says plugin hooks use the same base
format as workspace hooks. That establishes format support, not successful
execution in every installed VS Code version.

### 2. obra/superpowers: real plugin, Windows batch wrapper plus Bash

Pinned source: `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` (v6.3.0).
The [SessionStart configuration][super-hooks] contains:

```json
"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
"shell": "bash",
"async": false
```

The [polyglot wrapper][super-wrapper] contains this Windows branch:

```bat
set "HOOK_DIR=%~dp0"
```

```bat
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)
```

It also tries the x86 Git path and Bash on PATH; when none is found it exits
successfully without SessionStart injection. Unix execution ends in
`exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"`.

Classification: Claude-format plugin hook; `.cmd`/shell dispatch to Bash, **not
PowerShell**. Its comments explicitly address Claude Code Windows `.sh`
auto-detection. The [upstream README][super-repo] also documents Copilot CLI
plugin installation, but that is not proof of this Windows launch chain working
in VS Code or of Copilot honoring the `shell` property identically to Claude.
Reputation evidence: the fetched repository page displayed approximately 282.3k
stars and 25.3k forks; these are transient repository metrics, not Windows hook
usage counts or a correctness guarantee.

### 3. SonarSource/sonarqube-agent-plugins: vendor plugin, Node hook

Pinned source: `e596969a083cf27bfe439ee2e9459f7ef4124a70` (2.5.0).
The [Claude manifest][sonar-manifest] explicitly declares:

```json
"hooks": "./claude-hooks/hooks.json"
```

That [SessionStart hook][sonar-hooks] contains:

```json
"command": "node \"${CLAUDE_PLUGIN_ROOT}/scripts/setup.js\"",
"timeout": 30
```

Classification: actual bundled Claude plugin hook invoking JavaScript through
Node, not a PowerShell wrapper or native `.ps1` hook. The vendor-authored
[README][sonar-readme] documents Copilot CLI installation through
`sonarqube@awesome-copilot`, followed by `sonar integrate copilot`. The inspected
[Copilot manifest][sonar-copilot] has no `hooks` field. Do not transfer the Claude
manifest's hook declaration to Copilot or count CLI-installed integration hooks
as verified plugin-bundled PowerShell hooks. Vendor ownership and marketplace
listing are provenance evidence; no plugin popularity claim is made.

## PLUGIN_ROOT: Separate Host Injection From Shell Syntax

- [Copilot CLI release 1.0.26][cli-release] explicitly states:
  "Plugin hooks receive PLUGIN_ROOT, COPILOT_PLUGIN_ROOT, and CLAUDE_PLUGIN_ROOT
  env vars with the plugin's installation directory". This is a CLI release
  claim, not evidence about the VS Code local-chat executor.
- [VS Code plugin documentation][vscode-plugins] documents runtime token
  expansion and environment injection: Copilot format accepts `${PLUGIN_ROOT}`
  or `${CLAUDE_PLUGIN_ROOT}`; Claude format uses `${CLAUDE_PLUGIN_ROOT}`.
- PowerShell environment access is `$env:PLUGIN_ROOT` (and
  `$env:CLAUDE_PLUGIN_ROOT`). Without host substitution, `${PLUGIN_ROOT}` is
  PowerShell's ordinary braced-variable syntax, not environment-variable syntax.
  A token in configuration and an environment variable in a running process
  are separate mechanisms. A value absent from an unrelated interactive
  terminal does not establish whether a hook child process received it.
- The [CLI hook reference][cli-hooks] supports `powershell` for Windows;
  Copilot cloud agent runs Linux and ignores `powershell` entries. Neither that
  field nor a `.ps1` file implies cloud-agent support.
- Both quoted plugin commands above still need their root token resolved before
  the script can be located. Changing the script language alone cannot supply
  missing path information. The existing [local launch investigation][local-note]
  records an installed-host failure; it was not reproduced or repaired here.

## Search Boundary and Uncertainties

Sources were fetched synchronously. Candidate inspection was limited to
Superpowers, GitHub's official plugin catalog, two Awesome Copilot hook examples,
Microsoft Modernize Java, and SonarSource. No exhaustive GitHub search, plugin
installation, Windows smoke test, or runtime compatibility test was performed.

Excluded evidence:

- Awesome Copilot [session-logger][logger] and [tool-guardian][guardian] are
  documented as hooks copied into a project and use Bash scripts. Their presence
  in a repository that also hosts a plugin marketplace does not make these
  examples plugin hooks, and neither provides a PowerShell example.
- The [official Copilot catalog][catalog] is a credible discovery source, not
  proof that every listed plugin has hooks. Repository language percentages were
  not treated as hook evidence.
- Modernize Java 1.23.0's [actual nested manifest][java-manifest] declares agents
  and MCP, not hooks. Initial root-manifest and `hooks/hooks.json` requests at the
  catalog-pinned commit returned 404; the nested manifest was then verified.
  This does not establish that all versions or related Microsoft plugins lack
  PowerShell hooks.

The defensible answer is therefore: official PowerShell examples exist, but this
bounded inspection found no convincing named-plugin native `.ps1` precedent.
Choose Bash for its dependency/maintenance tradeoff, not as a presumed cure for
host-specific plugin-root handling.

## Sources

[vscode-hooks]: https://code.visualstudio.com/docs/agent-customization/hooks#_osspecific-commands
[vscode-plugins]: https://code.visualstudio.com/docs/agent-customization/agent-plugins#_plugin-environment-variables
[cli-hooks]: https://docs.github.com/en/copilot/reference/hooks-configuration
[cli-release]: https://github.com/github/copilot-cli/blob/d7ede79b9cbd4a76f64bb4b18a5731c4d008704b/changelog.md#1026---2026-04-14
[super-repo]: https://github.com/obra/superpowers
[super-hooks]: https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/hooks/hooks.json
[super-wrapper]: https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/hooks/run-hook.cmd
[sonar-manifest]: https://github.com/SonarSource/sonarqube-agent-plugins/blob/e596969a083cf27bfe439ee2e9459f7ef4124a70/.claude-plugin/plugin.json
[sonar-hooks]: https://github.com/SonarSource/sonarqube-agent-plugins/blob/e596969a083cf27bfe439ee2e9459f7ef4124a70/claude-hooks/hooks.json
[sonar-copilot]: https://github.com/SonarSource/sonarqube-agent-plugins/blob/e596969a083cf27bfe439ee2e9459f7ef4124a70/.github/plugin/plugin.json
[sonar-readme]: https://github.com/SonarSource/sonarqube-agent-plugins/tree/2.5.0
[logger]: https://github.com/github/awesome-copilot/tree/main/hooks/session-logger
[guardian]: https://github.com/github/awesome-copilot/tree/main/hooks/tool-guardian
[catalog]: https://github.com/github/copilot-plugins
[java-manifest]: https://github.com/microsoft/modernize-java/blob/5ccc2ad4011314602e1b80f0b818c95bcf198f67/plugins/modernize-java/.github/plugin/plugin.json
[local-note]: 2026-09-06-copilot-plugin-hook-script-launch.md