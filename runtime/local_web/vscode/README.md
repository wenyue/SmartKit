# SmartKit Diff Bridge

使用 VS Code 查看 SmartKit diff 需要安装 SmartKit Diff Bridge（`wenyue.smartkit-diff-bridge`）。扩展负责当前窗口内的比较选择：

- 请求对应的仓库已注册，且历史基线可以读取：在该窗口直接打开 Git 基线与当前文件的比较。
- 仓库未注册、只注册了父仓库或历史读取失败：通知 SmartKit 使用已核实 blob 的临时基线。
- 编辑器打开请求的结果未知：不自动重复打开，保留网页比较入口。

扩展不打开仓库、不修改项目设置，也不安装或更新 SmartKit。

## 本地启用

SmartKit 在会话启动时检查 VS Code 默认配置中的扩展。打开 diff 时，如果扩展尚未安装，浏览器会在页面中央显示安装表单并等待。核对配置名后点击「安装并打开 Diff」，SmartKit 会安装随包附带的 VSIX，核对该配置中的安装版本，然后自动继续打开原 diff。

也可以运行已安装 SmartKit 的 `local_web ensure`，打开返回的 `apps.editor` 本机设置页。填入仓库窗口正在使用的 VS Code 配置名称，点击「安装或更新 Diff Bridge」。默认配置填 `Default`。如果窗口还没加载扩展，重载仓库窗口后可重新打开 diff，验证能否直接读取 Git 历史。

## 打包

Git 分发的 SmartKit 安装包携带 `runtime/local_web/smartkit-diff-bridge.vsix`。
修改扩展后先更新 `package.json` 中的扩展版本，再从本目录生成随包交付的文件。

```sh
npx --yes --package=@vscode/vsce@4.1.0 -- vsce package --no-dependencies --allow-missing-repository --skip-license --out ../smartkit-diff-bridge.vsix
```

CI 核对 VSIX 中的扩展源码和清单与当前源码一致。

## 窗口与连接

最近获得焦点且启用此扩展的 VS Code 窗口发布一个本机回环地址和随机访问令牌。
检测仓库、读取历史基线及打开原生比较都在收到请求的同一窗口完成。
只注册父仓库不会被当作目标 worktree 已注册。
连接需要令牌，拒绝带 Origin 的浏览器请求；不监听外部网络。
窗口关闭时仅清理仍属于自己的描述文件，避免删除另一个窗口的连接信息。

## 验证

从 SmartKit 仓库根目录运行：

```text
python -B -m unittest discover -s tests -p test_editor_bridge.py
python -B -m unittest discover -s tests -p test_review_diff.py
```

窗口端测试需要 Node.js，并由 Python 测试入口自动运行。
这些回归使用隔离状态和真实本机 HTTP 连接，不安装扩展或操作用户现有窗口。
