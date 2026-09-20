# WenYue SmartKit

English | [简体中文](README.zh-CN.md)

WenYue SmartKit is a plugin for Codex, Cursor, GitHub Copilot, and Qoder. It provides reusable
AI coding workflows and shared project guidelines to help teams set up and maintain their coding
assistants. It supports Windows and Linux.

## Install the plugin

Install your preferred coding assistant first, then follow its instructions below.

### Codex

```sh
codex plugin marketplace add wenyue/SmartKit
codex plugin add smartkit@wenyue
```

After installation, open a Codex CLI session and run `/hooks` to review and trust SmartKit's
Hooks. Then start a new session or run `/clear`. You can also install from the added marketplace
through `/plugins`. See the [Codex plugin guide](https://learn.chatgpt.com/docs/plugins).

### Cursor

Clone the plugin into Cursor's local plugin directory:

```sh
git clone https://github.com/wenyue/SmartKit.git "$HOME/.cursor/plugins/local/smartkit"
```

Restart Cursor or run `Developer: Reload Window`, then open Customize to confirm the plugin is
loaded. Your organization must allow local plugin imports. For team marketplace installation,
see the [Cursor plugin guide](https://cursor.com/docs/plugins).

### GitHub Copilot CLI

```sh
copilot plugin marketplace add wenyue/SmartKit
copilot plugin install smartkit@wenyue
```

See the [Copilot plugin installation guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing).

### Qoder

```sh
qoder plugin marketplace add wenyue/SmartKit
qoder plugin install smartkit@wenyue
```

These commands require plugin marketplace support to be enabled in Qoder. See the
[Qoder plugin guide](https://docs.qoder.com/cli/plugins).
