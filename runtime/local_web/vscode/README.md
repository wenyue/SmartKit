# SmartKit Diff Bridge

这个可选 VS Code 扩展只负责当前窗口内的比较选择：

- 请求对应的仓库已注册，且历史基线可以读取：在该窗口直接打开 Git 基线与当前文件的比较。
- 仓库未注册、只注册了父仓库或历史读取失败：通知 SmartKit 使用已核实 blob 的临时基线。
- 编辑器打开请求的结果未知：不自动重复打开，保留网页比较入口。

扩展不打开仓库、不修改项目设置，也不安装或更新 SmartKit。

## 本地启用

在提供此开发者入口的 VS Code 中运行命令面板的
`Developer: Install Extension from Location...`，选择本目录，随后重载窗口。
也可将本目录作为标准 VS Code 扩展打包后安装。
同时需要使用包含窗口桥接客户端的 SmartKit 版本；只安装扩展不会改变旧版客户端的启动逻辑。

安装不是普通比较操作的一部分。未安装桥接时，新的 SmartKit 客户端直接使用临时基线。

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
