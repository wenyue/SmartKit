# Claude Hook Probe Result

## Scope

Windows VS Code Copilot SessionStart execution through a temporary local Claude
plugin. This verifies script launch and root resolution only, not complete
SmartKit behavior, Linux, or Copilot CLI compatibility.

## Configuration

The temporary plugin used `.claude-plugin/plugin.json`, with `hooks` pointing to
`./hooks/hooks.json`. Its nested `SessionStart` command was:

```text
powershell.exe -NoProfile -NonInteractive -File "${CLAUDE_PLUGIN_ROOT}/hooks/probe.ps1"
```

It was registered through `chat.pluginLocations` in the workspace's active
OtakuRoom profile. The earlier default-profile registration did not load it.

## Observed Evidence

Source: local `GitHub Copilot Chat Hooks.log` under VS Code log session
`20260906T211415/window1/exthost/GitHub.copilot-chat/`, and the probe's
`events.jsonl`. User initiated a new chat with no tool calls requested.

- Session ID: `239412fb-bfcd-41f1-a38c-8bfa8da6e916`.
- At 2026-09-06 23:54:57 local time, the logged command already contained the
  absolute temporary plugin path instead of `${CLAUDE_PLUGIN_ROOT}`.
- The command's `env` explicitly contained `CLAUDE_PLUGIN_ROOT` with that path.
- The script recorded UTC time `2026-09-06T15:54:58.6303911Z`, event
  `SessionStart`, PowerShell `5.1.26100.9168`, and `rootMatches: true`.
- `PLUGIN_ROOT` and `COPILOT_CLI` were absent in that script's environment.
- At 23:54:58.851, the host recorded `Completed (Success) in 1071ms`.
- The two existing SmartKit SessionStart commands still failed before the probe.

## Conclusion and Limits

The Claude-format local plugin successfully launched a PowerShell script and
received the correct Claude root environment variable in this VS Code run.
PowerShell itself is not inherently incompatible with plugin-root delivery.
This probe used an explicit `powershell.exe -File` command, not SmartKit's exact
`powershell` field or its runtime scripts; those still need integration testing.

Copilot CLI 1.0.56 test invocations exited before producing probe logs or events.
CLI support remains inconclusive, not failed at the plugin boundary. No production
manifest migration is authorized by this result alone.

The temporary profile registration and probe files were removed after collecting
this evidence. Formal SmartKit plugin configuration and installation were unchanged.