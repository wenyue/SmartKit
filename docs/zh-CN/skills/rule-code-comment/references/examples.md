# 注释判断样例

这些对照草稿展示信息取舍和作者口吻。各样例的事实来自所述背景；这些背景不是目标实现的证据，样例也不是用户已认可的风格。根据目标的契约、注释语法、文档语言和格式要求调整判断。样例用英文演示，并不构成跨项目的语言要求。代码片段省略导入和外围声明，相关契约由各自的背景说明。

## 简单接口或组件

背景：父组件管理当前选中的标签页。这个组件显示该选择并报告点击，不持有选择状态。类似组件有简短的文档注释。

```dart
/// Supplies the current selection and receives requests to select another tab.
class TabStripProps {
  const TabStripProps(this.tabs, this.selectedId, this.onSelect);

  final List<Tab> tabs;
  final String selectedId;
  final void Function(String) onSelect;
}
```

注释说明了面向父组件的边界，并区分接收请求与改变选择。重复各属性名称或称赞组件的灵活性，都没有多少信息增量。如果目标要求逐一记录属性，仍应提供这些文档。

## 复杂调用契约

背景：这个接口跨越存储边界，目前只有一个调用者。已接受的契约要求批次具有原子性，网络操作结果不确定时，只有复用同一键和同一组条目才能重试。同一键搭配不同条目会报错。

```go
type Ledger interface {
	// Apply records all entries atomically. Repeating a key with identical entries
	// returns the original receipt; reusing it with different entries fails.
	// After a timeout, retry with the same key and entries: the first attempt
	// may already have committed.
	Apply(ctx context.Context, key string, entries []Entry) (Receipt, error)
}
```

即使只有一个调用者，契约也很重要。原子性和超时的后果提供了签名之外、指导正确使用的信息。以方法名开头符合本地文档惯例；内部锁或数据库细节应放在实现处，除非它们影响这个契约。

## 失败也是调用者契约的一部分

这些样例描述已经成立的失败契约。注释告诉调用者什么失败了、如何识别，以及留下了什么状态，并不选择新的错误设计。

### 抛出和有意传播的失败

背景：这个方法属于只读配置读取器，其 `file` 是一个 `File`。已接受的契约要求内容为 UTF-8 编码的 JSON 对象。调用者使用既有的 `FormatException` 和 `FileSystemException` 类别，区分内容无效与访问失败。读取器既不修复文件，也不保存默认值。

```dart
/// Loads configuration from a UTF-8 JSON object.
///
/// Throws [FormatException] for invalid UTF-8, invalid JSON, or a non-object root.
/// Propagates [FileSystemException] when the file cannot be read.
/// Failure leaves stored bytes untouched; no defaults are written.
Map<String, dynamic> load() {
  final value = jsonDecode(utf8.decode(file.readAsBytesSync()));
  if (value is! Map<String, dynamic>) {
    throw const FormatException('Expected a JSON object');
  }
  return value;
}
```

这些类别让调用者能够区分需要纠正内容还是解决访问问题。即使方法有意让读取失败向上传播，这类失败也应写进注释。关于残留状态的说明，可以避免调用者误以为失败时已经修复或替换了配置。列出解码器内部细节或偶发的运行时失败，无助于这些调用决策。

### 具有稳定识别方式的返回失败

背景：这个资源 API 从文件系统读取内容，不改变已存储的内容。已接受的契约保留文件系统的错误标识，包括资源缺失时的 `fs.ErrNotExist`；即使底层读取已经产生部分字节，失败时也不返回数据。

```go
// LoadResource reads name without modifying stored content.
// If name is absent, errors.Is(err, fs.ErrNotExist) is true.
// Other read errors retain their identities. On error, data is nil.
func LoadResource(fsys fs.FS, name string) ([]byte, error) {
	data, err := fs.ReadFile(fsys, name)
	if err != nil {
		return nil, fmt.Errorf("load resource %q: %w", name, err)
	}
	return data, nil
}
```

资源缺失条件和匹配操作，让调用者能够决定是否选择其他资源。其他读取失败在传播时带有上下文，并保留已经承诺的识别方式。不返回数据的承诺，避免部分读取结果被误当成可用结果；只读承诺则说明了存储中的残留状态。列出文件系统的实现细节或逐条错误消息字符串，不会增加稳定的调用者契约。

## 生命周期

背景：这个辅助函数订阅一个 tick 流。数据源可能需要异步清理。所有者的 `onClose` 钩子接收返回 `Future<void>` 的清理回调，等待它们完成，并暴露清理失败。注册语句在所有者的初始化方法中执行。

```dart
/// Delivers ticks until the caller cancels the returned subscription.
/// Cancellation stops delivery immediately; await it to finish source cleanup.
StreamSubscription<int> subscribeToTicks(
  Stream<int> ticks,
  void Function(int) onTick,
) {
  return ticks.listen(onTick);
}

final subscription = subscribeToTicks(ticks, refresh);
owner.onClose(subscription.cancel);
```

注释说明调用者的生命周期义务，并区分停止事件与完成清理。注册的取消方法将其 future 返回给已经明确的所有者，因此清理是否完成以及是否失败仍然可见。再加一条复述注册过程的注释，信息增量很小。如果生命周期钩子不能等待清理，就需要另行说明责任如何归属。

## 局部原因

背景：回调可能从可变监听器集合中取消自身订阅。直接遍历集合时，如果集合大小改变，遍历就会失败；初始快照中的回调仍必须收到本次派发。

```dart
// Snapshot the listeners so callbacks can unsubscribe during dispatch.
for (final listener in listeners.toList()) {
  listener(event);
}
```

注释解释为什么需要快照，而不是复述转换为列表的操作。派发契约负责定义投递保证，这条局部说明无需重复。在较长的函数中，`// Publish notifications` 这样的简短标题即使不增加隐藏的原因，也能帮助读者找到一个完整的逻辑段落。

## 必要的较长解释

背景：只追加日志存储带校验和的记录。其恢复契约允许丢弃崩溃后最后一条不完整记录，但拒绝校验和无效的完整记录，即使它位于末尾也一样。读取器仅在记录之间返回 `io.EOF`，仅在最后一条记录不完整时返回 `io.ErrUnexpectedEOF`。片段运行在返回 `error` 的恢复方法内；`truncateToLastRecord` 只删除该不完整尾部，其他辅助函数不执行截断。

```go
// A crash can leave the last record incomplete, so recovery may discard that
// trailing fragment. A complete record with a bad checksum is different: it
// indicates corruption, and discarding it could silently lose committed data.
// Check completeness before validating the checksum so only an interrupted
// append takes the truncation path.
for {
	record, err := readRecord(input)
	if errors.Is(err, io.EOF) {
		return nil
	}
	if errors.Is(err, io.ErrUnexpectedEOF) {
		if err := truncateToLastRecord(); err != nil {
			return fmt.Errorf("discard incomplete log tail: %w", err)
		}
		return nil
	}
	if err != nil {
		return fmt.Errorf("read log record: %w", err)
	}
	if err := verifyChecksum(record); err != nil {
		return fmt.Errorf("verify log record checksum: %w", err)
	}
	if err := replay(record); err != nil {
		return fmt.Errorf("replay log record: %w", err)
	}
}
```

崩溃恢复、数据损坏和处理顺序之间的关系值得用这些篇幅解释。压缩成“处理不完整记录”会丢失两条路径为何不同的原因。返回的错误让读取、校验和验证、重放和截断失败保持可见，而不会把它们都当成允许截断的条件。注释无需复述完整的格式规范或其历史。

## 有意省略

背景：这个局部集合包装器没有额外的校验、单位、副作用或调用义务。类似辅助方法中，有的带简短而有用的注释，有的代码直白、没有注释；没有适用的明确文档要求。

```dart
bool get isEmpty => items.isEmpty;
```

保持不加注释。名称和函数体已经提供了有用的说明，“返回 items 是否为空”只会重复。这一选择综合考虑了辅助方法的用途、简单程度、信息价值和局部背景；附近没有注释或 public 可见性，都不能单独决定结果。
