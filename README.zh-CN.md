# WenYue SmartKit

[English](README.md) | 简体中文

WenYue SmartKit 是适用于 Codex、Cursor、GitHub Copilot 和 Qoder 的插件，提供可复用的 AI 编程工作流和
统一的项目规范，帮助团队配置和维护编程助手。支持 Windows 和 Linux。

## 安装插件

先安装你使用的编程助手，再按对应步骤安装插件。

### Codex

```sh
codex plugin marketplace add wenyue/SmartKit
codex plugin add smartkit@wenyue
```

安装后，打开 Codex CLI 会话，运行 `/hooks`，审查并信任 SmartKit 的 Hooks，然后开启新会话或运行
`/clear`。也可以通过 `/plugins` 从已添加的市场中安装。参见 [Codex 插件指南](https://learn.chatgpt.com/docs/plugins)。

### Cursor

将插件克隆到 Cursor 的本地插件目录：

```sh
git clone https://github.com/wenyue/SmartKit.git "$HOME/.cursor/plugins/local/smartkit"
```

重启 Cursor 或运行 `Developer: Reload Window`，然后打开 Customize，确认插件已加载。
所在组织需允许导入本地插件。通过团队市场安装的方法，参见 [Cursor 插件指南](https://cursor.com/docs/plugins)。

### GitHub Copilot CLI

```sh
copilot plugin marketplace add wenyue/SmartKit
copilot plugin install smartkit@wenyue
```

参见 [Copilot 插件安装指南](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing)。

### Qoder

```sh
qoder plugin marketplace add wenyue/SmartKit
qoder plugin install smartkit@wenyue
```

这些命令需要 Qoder 已启用插件市场功能。参见 [Qoder 插件指南](https://docs.qoder.com/cli/plugins)。
