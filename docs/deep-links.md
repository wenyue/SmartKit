# SmartKit 点击链接

SmartKit 使用用户级 `smartkit://` 协议打开本机的固定 diff 快照和生成的报告。
多个 Skill 共用同一个处理器；注册、链接生成和点击处理由脚本完成。
需要 Python 3.8 或更新版本及本机桌面环境。

## 首次启用

在 SmartKit 插件目录运行：

```sh
python runtime/deep-links/deep_links.py ensure --enable
```

Windows 和 Linux 的注册只影响当前用户，不需要管理员权限。机器已有其它
`smartkit://` 处理器时，脚本保留现状并报出冲突。没有桌面会话或在 CI 中时，
自动 Hook 跳过注册；明确执行首次启用时会说明不可用的原因。

程序安装位置：

| 操作系统 | 默认程序位置 |
| --- | --- |
| Windows | `%LOCALAPPDATA%\SmartKit\DeepLinks\deep-links.pyz` |
| Linux | `~/.local/share/smartkit/deep-links/deep-links.pyz`，尊重 `XDG_DATA_HOME` |
| macOS | `~/Library/Application Support/SmartKit/DeepLinks/deep-links.pyz` |

系统协议关联使用安装时找到的 Python 解释器绝对路径。Windows 优先使用同一
Python 安装中的 `pythonw.exe`；Linux 的 `.desktop` 入口不打开终端。
macOS 使用 `~/Applications/SmartKit Links.app` 接收 URL。

启用后，各宿主的会话启动 Hook 调用 `ensure --quiet`，检查和维护已启用的注册。
配置正确时不重新写入程序、不向 Agent 注入上下文。多个项目和宿主共用用户级锁，
旧版本 Hook 保留较新版本的安装。Hook 维护失败会留下诊断，但不阻止其它会话工作。

## 批量生成

输入是 JSON 数组，所有路径相对于该 JSON 文件所在目录解析：

```json
[
  {
    "id": "statistics",
    "action": "diff",
    "title": "statistics.dart",
    "before": "before/statistics.dart",
    "after": "after/statistics.dart",
    "viewer": "auto"
  },
  {
    "id": "report",
    "action": "artifact",
    "path": "report.html"
  }
]
```

```sh
python runtime/deep-links/deep_links.py create --input tasks.json > links.json
```

输出是同顺序的 JSON 数组，每项包含原始 `id`、`action`、实际 `url`、
本地预览 `web_url` 和可直接使用的 `markdown`。URL 使用随机任务 ID：

```text
smartkit://diff/<随机任务ID>
smartkit://artifact/<随机任务ID>
```

`create` 将前后文件复制为固定快照并生成 HTML diff。链接创建后继续编辑原文件，
以及退出 Agent 会话，都不改变链接展示的内容。新增或删除文件使用一侧为 `null`；
两侧同时为空会被拒绝。diff 文件需要是 UTF-8 文本。脚本不自行读取 Git，
调用方应先按需要的比较范围导出 before/after 文件，包括未提交改动。

`viewer` 支持 `auto`、`vscode`、`web`，默认为 `auto`；也可通过
`create --viewer web` 设置整个批次的默认值，任务中的设置优先。
自动模式优先向 VS Code 最近使用的已有窗口发送 `--reuse-window --diff` 请求；
找不到 VS Code 或启动明确失败时打开 HTML。显式选择 VS Code 后，失败会提供
网页查看入口并保留失败结果。启动进程成功表示请求已发送，仍需屏幕确认实际显示。

`artifact` 接收独立的 HTML、PDF、文本、Markdown 和常见图片报告，通过系统默认
查看器打开其副本。HTML 报告应自包含；相对路径引用的附属资源不会自动复制。

## 点击与网页备用入口

已注册协议且客户端允许自定义链接时，Markdown 点击直接交给 SmartKit 处理器，
VS Code 路径不经过中间网页，也不依赖 HTTP 服务。直接调用同一处理器的方法：

```sh
python runtime/deep-links/deep_links.py open 'smartkit://diff/<随机任务ID>'
```

客户端可能禁止自定义协议或要求允许打开本机程序。`web_url` 是本地文件 URL，
同样取决于客户端是否允许；需要 HTTP 备用链接时运行：

```sh
python runtime/deep-links/deep_links.py serve --input links.json
```

脚本绑定 `127.0.0.1`，输出这批任务实际可点击的 HTTP URL。保持该进程运行即可
查看网页；停止进程后这些 HTTP URL 不再可用，原生链接和快照仍然保留。
GET 和 HEAD 只返回预览，不启动 VS Code 或执行点击动作。原生链接仅适用于
保存快照的这台机器，不能直接分享给其它机器。

## 卸载与清理

```sh
python runtime/deep-links/deep_links.py uninstall
python runtime/deep-links/deep_links.py clean '<随机任务ID>'
```

`uninstall` 关闭自动注册并移除仍由 SmartKit 管理的协议关联，保留安装包和所有快照；
下一次 Hook 不会重新启用。`clean` 明确删除一个任务的快照，此任务的旧链接失效。
任务保存在安装目录的 `tasks/` 中，首版不自动删除，因此会占用持续增长的磁盘空间。

## 给调用方与维护者

各 Skill 的脚本准备同样的任务数组，调用 `create`，直接引用返回的 `markdown`。
调用方负责比较范围；Deep Link 模块负责固定快照和查看方式。URI 只携带已登记的
动作与随机任务 ID，不接受任意命令、脚本路径或远程任务数据。

源码位于 `runtime/deep-links/`：`deep_links.py` 管理协议解析、批量任务和安装包，
`registration.py` 管理操作系统适配，`actions.py` 管理各动作的参数校验、快照、
记录校验与打开行为。新增动作时在 `actions.py` 中实现这些行为并登记到固定动作表；
系统协议入口保持不变。程序更新只替换完整安装包，保留任务和用户启用状态。

Windows 注册表操作与路径转义可在测试替身上验证；平台桌面上的真实协议点击、
客户端放行和实际窗口复用需要在对应环境确认，不能仅用进程退出码判断完成。
