# 注释判断示例

每个示例都交代了自己的事实背景。用它们判断读者需要什么信息，以及会在哪里找这些信息。代码片段展示可用的英文写法。实际契约、语言和格式以目标项目为准。

## 移动代码时保留决定

用户接受在预览列表显示缓存标题，这样打开列表就不需要发起网络请求。缓存标题最多可滞后一分钟。打开单个条目时会获取其当前标题。维护者看到列表代码时，可能会以为漏做了刷新。

```dart
// Use cached titles so opening the list needs no network request. Titles may
// be up to one minute old. Opening an item fetches its current title.
final previews = previewCache.readWithin(const Duration(minutes: 1));
```

假设重构后，由预览仓库负责决定如何加载预览标题。维护者今后可能在这个仓库里通过加网络请求改变原决定，所以使用缓存的理由和有效期上限也应移到那里。如果调用者会根据标题的新鲜程度在预览和详情 API 之间选择，就在这两个 API 分别说明可观察的差异。读者能在新的位置看到这些解释后，就可以删掉列表中的旧注释。

审查时，落后四十秒的标题符合已接受的行为。列表继续显示超过一分钟的缓存标题，则超出了接受范围。打开条目时未获取当前标题，会违反详情 API 的独立契约。已有决定可以帮助分别判断这些情况。

## 调用者在重试前需要知道什么

账本以原子方式提交每批条目。超时可能发生在提交之后。如果第一次尝试未提交，用相同的键和条目重试会提交该批次。如果第一次已经提交，重试会返回已有回执。使用已提交的键搭配不同条目会失败。即使只有一个调用者，签名也不足以让其知道如何选择重试参数。

```go
// Apply records the batch atomically. A timeout can leave the commit outcome
// unknown. Retry with the same key and entries. If the batch already
// committed, the retry returns its receipt without applying it again.
// Reusing a committed key with different entries fails.
Apply(ctx context.Context, key string, entries []Entry) (Receipt, error)
```

说明应放在接口上，调用者会在那里决定重试用的键。描述锁或事务原语会把解释绑在实现细节上，调用者仍然不知道应该用哪个键。

## 两种识别失败的方式

一个只读的 Dart 配置读取器接收 UTF-8 编码的 JSON 对象。调用者需要区分内容无效和文件系统访问失败，也需要知道加载失败时是否写入了默认值。

```dart
/// Loads the configuration from a UTF-8 JSON object.
///
/// Throws [FormatException] for invalid UTF-8, invalid JSON, or a non-object
/// root. Propagates [FileSystemException] when the file cannot be read.
/// On failure the stored bytes are unchanged.
Map<String, dynamic> load() {
  final value = jsonDecode(utf8.decode(file.readAsBytesSync()));
  if (value is! Map<String, dynamic>) {
    throw const FormatException('Expected a JSON object');
  }
  return value;
}
```

一个 Go 资源加载器则包装并返回文件系统错误，同时丢弃部分数据。契约保留错误标识，因此调用者可以使用语言原生的匹配方式。

```go
// LoadResource reads name without changing stored content. For a missing
// resource, errors.Is(err, fs.ErrNotExist) is true. Other read errors retain
// their identities. Every failure returns nil data.
func LoadResource(fsys fs.FS, name string) ([]byte, error) {
	data, err := fs.ReadFile(fsys, name)
	if err != nil {
		return nil, fmt.Errorf("load resource %q: %w", name, err)
	}
	return data, nil
}
```

两处注释都写明了失败条件、API 承诺的识别方式以及失败后与调用者有关的状态。调用者据此判断，无需匹配偶发的错误消息。

## 调用者义务和局部实现理由

流订阅可以在数据源完成清理之前停止投递事件。取消订阅的人需要知道何时已经释放资源。

```dart
/// Delivers ticks until the caller cancels the returned subscription.
/// Cancellation stops delivery immediately. Await it to finish source cleanup.
StreamSubscription<int> subscribeToTicks(
  Stream<int> ticks,
  void Function(int) onTick,
) {
  return ticks.listen(onTick);
}
```

调用者可以把取消方法传给会等待其结果的关闭钩子。订阅文档解释了调用者的义务，无需假设所有调用者都使用同一个钩子。

在另一个分发器中，监听器可能在接收事件时取消自己的订阅。维护者可能会把快照当成多余的分配而删掉。这一理由应该写在维护者会改动的那行代码旁。

```dart
// Snapshot the listeners so callbacks can unsubscribe during dispatch.
for (final listener in listeners.toList()) {
  listener(event);
}
```

## 需要多少说明

一个组件显示当前选中的标签页，并把点击报告给父组件。属性已经表明哪个值是当前标签页，哪个是回调。简短的接口注释可以用一句话说明由谁管理选中状态。

```dart
/// Supplies the parent’s selected tab and receives requests to change it.
class TabStripProps {
  const TabStripProps(this.selectedId, this.onSelect);

  final String selectedId;
  final void Function(String) onSelect;
}
```

如果一个局部集合包装器没有额外校验、单位、副作用或调用义务，需要的说明可能更少。没有明确覆盖要求时，声明本身就可以说明行为。

```dart
bool get isEmpty => items.isEmpty;
```

恢复程序则可能在崩溃后截断最后一条未写完整的日志记录。完整记录的校验和有误，即使出现在日志末尾，也是数据损坏的表现。把这两种情况都当作写入中断，可能会悄悄丢掉已经提交的数据。决定是否截断的代码旁值得用几句解释这层关系。

```go
// A crash can leave the final record incomplete. Only that trailing fragment
// may be discarded. Check completeness before validating the checksum so a
// corrupt but complete record is reported without truncating committed data.
```
