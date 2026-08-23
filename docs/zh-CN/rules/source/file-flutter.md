# Dart 与 Flutter 指引

强度：`Default`

适用范围：Dart 与 Flutter 的归属、数据形态、状态、生命周期、UI、路由、模型、生成和
分析边界。

## 基础库适用性

- 将 `flutter_hooks`、`riverpod`、`go_router` 和 `freezed` 视为 Flutter 的标准基础库。
- 根据对应依赖或生成表面是否存在，分别应用每个库的段落；添加或迁移该依赖的任务适用
  库存在时的分支。

## 公共接口与归属

- 所有者内部行为默认使用实例成员。
- 顶层函数只用于框架入口、文件级声明、共享算法，或确实没有明确所有者的逻辑。

## 数据形态

- record 只用于小型局部元组返回；如果命名类型能提高清晰度，就使用命名类型。

## Flutter Hooks

- 使用 hooks 时，组件局部的 hook 生命周期使用 `HookWidget`；同一组件还使用 `riverpod` 时，
  使用 `HookConsumerWidget`。
- 标准 Flutter controller 和生命周期优先使用内置 hook；同一个非简单生命周期需要复用时，
  引入所有者内部的自定义 hook。
- 只能在 `build()` 或其他自定义 hook 的顶层以稳定顺序、无条件调用 hook。hook 的 keys 应是
  发生变化时必须重建所负责状态或资源的值。
- 通过 `useMemoized` 创建的可释放资源，应在 `useEffect` 中配对清理；也可以在同一个自定义
  `HookState` 中同时负责创建和释放。
- 未使用 hooks 时，在 `State.dispose()` 中释放所负责的 controller、subscription 和 listener。

## `riverpod`

- 跨越一个组件共享的状态，或既有功能或服务所有者是 provider 的状态使用 `riverpod`。组件
  生命周期内的状态和可释放 UI 资源留在负责它们的组件或 hook 中，即使其生命周期并不简单。
- 配置了 provider 生成时，使用项目的 `riverpod` annotation 和生成 provider 模式声明新的
  provider。
- build 期间观察响应式状态和依赖，事件处理程序中读取它们，只用监听处理副作用。只关心状态
  对象的一部分时，将 `select` 与 `ref.watch` 或 `ref.listen` 配合使用。
- provider 的 `build()` 是响应式的，依赖变化时可能再次运行。
- 创建每个可释放的 provider 资源后立即注册对应的 `onDispose` 回调，并且必须在任何 `await`
  之前完成。该回调只释放已经捕获的资源；state 赋值、provider 读取和 `Ref` 访问都留在回调
  之外。
- 默认让页面范围和参数化 provider 随其消费者释放。生命周期不应依赖单个页面的服务和仓库
  使用 `keepAlive: true`。
- 经过异步间隔后，使用受生命周期约束的状态前，应确认 provider 仍处于 mounted 状态。稳定
  依赖应在间隔前解析；会变化的 provider 状态应在 mounted 检查之后读取。
- 未使用 `riverpod` 时，保留应用已经建立的状态所有者。局部状态留在组件中，并使用既有的共享
  状态机制，而不是引入第二套机制。

## GoRouter

- 使用 `go_router` 时，页面导航使用它。配置了 typed route 生成时，应声明 typed route，
  并通过生成的路由对象导航，而不是使用原始路径字符串。
- 直接调用底层 router API 前，先复用应用已经建立的导航 facade、mounted context 解析、
  guard、redirect 和失败报告能力。
- 替换当前位置时使用 `go`；添加可能返回结果的页面时使用 `push`。
- authentication、access、leave admission 和导航反馈决策留在既有路由所有者中，不在调用方
  重复实现。
- 由 Navigator 管理的对话框、底部面板和浮层使用 `Navigator.of(context).pop(result)`。
- 未使用 `go_router` 时，使用应用已经建立的 Router 或 Navigator API，不为单个页面引入
  一套并行路由系统。

## `freezed`

- 使用 `freezed` 时，需要结构相等、`copyWith`、序列化支持或 sealed variant 的不可变值、领域
  和状态类型使用它。
- 一个产品状态使用一个不可变 data case；variant 具有不同数据或行为时使用 sealed union。
  只有存在真实 JSON 序列化边界时才添加 JSON 生成。
- `freezed` 声明支持私有构造函数时，将派生属性和领域行为保留在源类型上。
- 如果存储细节、可变性或 schema 兼容性不同，应将持久化模型与领域模型分开，并在 repository
  边界转换。
- 框架所有的类型、controller、具有 identity 的可变对象，以及由其他 schema 或 generator
  所有的类型，保留其原生表示。
- 未使用 `freezed` 时，使用不可变 Dart class 和 sealed type，或应用已经建立的模型 generator。
  只有调用方需要时才实现相等、复制和序列化。

## 异步边界

- 经过异步间隔后，使用捕获的 `BuildContext` 前，应确认它仍处于 mounted 状态。
- 稳定的组件依赖应在间隔前解析，会变化的状态只在 mounted 检查之后读取。

## 生成源文件

- 将生成的 provider、route、serialization、`*.g.dart` 和 `*.freezed.dart` 文件视为输出。
  修改其源声明，并运行项目拥有的 generator。
