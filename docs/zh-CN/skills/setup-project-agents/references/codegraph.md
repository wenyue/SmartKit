# CodeGraph 准备

本公开参考向获授权调用方提供 Setup 的限定 CodeGraph 准备命令。阅读本参考并使用命令，不会调用仅限用户调用的 Setup 工作流，也不要求配置会话。调用方负责判断何时值得准备、相应权限，以及 CodeGraph 不可用对自身任务的影响。

## 准备选定工作树

将 `<skill-root>` 解析为已加载的 `setup-project-agents` 目录，将 `<target-root>` 解析为选定工作树的物理根目录。运行前，确定缺失时安装 CodeGraph、建立目标本地索引和启动服务的权限：

```text
python "<skill-root>/scripts/workflow.py" setup-codegraph --help
python "<skill-root>/scripts/workflow.py" setup-codegraph --target "<target-root>" --harness "<active-harness>" --approved
```

`--approved` 记录已有权限，既不授予权限，也不要求重复确认。命令会安装缺失的可执行程序、初始化缺失的本地索引、同步可用索引中的待处理变更，并按需启动运行时。健康的索引和服务会被复用。使用此限定路径，而非可能重写独立所有者宿主配置的 CodeGraph 通用宿主安装器。

每棵工作树的索引保留在其自身的 `.codegraph` 目录内。复制或链接另一棵树的可变数据库，不属于准备。就绪检查要求本地数据库、匹配的项目及工作树身份、完整且已同步的索引，以及能响应的运行时。查询必须通过 `projectPath` 指明目标树；父树的响应不能证明当前树已就绪。

## 解读结果

成功要求退出码为 0，并包含 `phase: setup-codegraph` 和 `ready: true`。它证明当前 CodeGraph 已就绪，而非配置 setup 完成或项目健康。之后再次进入时复用本地索引；仅在当前证据表明就绪状态缺失或过时时刷新。CodeGraph 负责自动同步；工作树的生命周期所有者在清理时处理其本地资源和服务。

失败时，保留现有数据、部分输出和诊断。现有索引若不完整、过时或身份不匹配，需要单独修复；此命令不会替换它。重试前先解决工具不可用、权限或运行时前提问题。报告缺口，并在调用方任务允许时通过直接检查源码继续独立工作；不要把另一棵树的索引当作当前树的证据。要求 CodeGraph 的调用方仍未完成。Hook 检查仍是只读提醒，不授权任何准备操作。
