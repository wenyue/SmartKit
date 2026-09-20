# 注释判断样例

这些对照草稿展示信息取舍和作者口吻。各样例的事实来自所述背景；这些背景不是目标实现的证据，样例也不是用户已认可的风格。根据目标的契约、注释语法、文档语言和格式要求调整判断。样例用英文演示，并不构成跨项目的语言要求。

## 简单接口或组件

背景：父组件管理当前选中的标签页。这个组件显示该选择并报告点击，不持有选择状态。类似组件有简短的文档注释。

```ts
/** Supplies the current selection and receives requests to select another tab. */
interface TabStripProps {
  tabs: readonly Tab[];
  selectedId: string;
  onSelect: (id: string) => void;
}
```

注释说明了面向父组件的边界，并区分接收请求与改变选择。重复各属性名称或称赞组件的灵活性，都没有多少信息增量。如果目标要求逐一记录属性，仍应提供这些文档。

## 复杂调用契约

背景：这个 Go 接口跨越存储边界，目前只有一个调用者。已接受的契约要求批次具有原子性，网络操作结果不确定时，只有复用同一键和同一组条目才能重试。同一键搭配不同条目会报错。

```go
type Ledger interface {
    // Apply records all entries atomically. Repeating a key with identical entries
    // returns the original receipt; reusing it with different entries fails.
    // After a timeout, retry with the same key and entries: the first attempt
    // may already have committed.
    Apply(ctx context.Context, key string, entries []Entry) (Receipt, error)
}
```

即使只有一个调用者，契约也很重要。原子性和超时的后果提供了签名之外、指导正确使用的信息。以方法名开头符合 Go 文档惯例；内部锁或数据库细节应放在实现处，除非它们影响这个契约。

## 生命周期

背景：这个 TypeScript 订阅会立即注册一个监听器。返回的函数会移除该监听器，重复调用也安全。视图所有者必须在释放视图时调用它。

```ts
/** Subscribes to ticks until the returned cleanup function is called. */
function subscribeToTicks(onTick: () => void): () => void {
  clock.addEventListener("tick", onTick);
  return () => clock.removeEventListener("tick", onTick);
}

const stopTicks = subscribeToTicks(refresh);
view.onDispose(stopTicks);
```

注释在可调用边界上说明生命周期义务。释放时的调用展示了这个调用者如何履行义务，因此无需再用注释复述注册或清理。如果释放后仍可能执行已排队的回调，就需要不同的证据和措辞。

## 局部原因

背景：Python 回调可能取消自身订阅。直接遍历集合时，如果集合大小改变，遍历就会失败；初始快照中的回调仍必须收到本次派发。

```python
# Snapshot the listeners so callbacks can unsubscribe during dispatch.
for listener in tuple(listeners):
    listener(event)
```

注释解释为什么需要快照，而不是复述转换为元组的操作。派发契约负责定义投递保证，这条局部说明无需重复。在较长的函数中，`# Publish notifications` 这样的简短标题即使不增加隐藏的原因，也能帮助读者找到一个完整的逻辑段落。

## 必要的较长解释

背景：只追加日志存储带校验和的记录。格式允许崩溃后最后一条记录不完整。恢复契约拒绝校验和无效的完整记录，即使它位于末尾也一样，因为这种情况表示数据损坏，而不是允许出现的追加中断。

```rust
// A crash can leave the last record incomplete, so recovery may discard that
// trailing fragment. A complete record with a bad checksum is different: it
// indicates corruption, and discarding it could silently lose committed data.
// Check completeness before validating the checksum so only an interrupted
// append takes the truncation path.
match read_record(input)? {
    RecordRead::IncompleteTail => {
        truncate_to_last_record()?;
        break;
    }
    RecordRead::Complete(record) => {
        verify_checksum(&record)?;
        replay(record)?;
    }
    RecordRead::End => break,
}
```

崩溃恢复、数据损坏和处理顺序之间的关系值得用这些篇幅解释。压缩成“处理不完整记录”会丢失两条路径为何不同的原因。片段假设外层有恢复循环；注释无需复述完整的格式规范或其历史。

## 有意省略

背景：这个 Python 局部辅助方法没有额外的校验、单位、副作用或调用义务。类似辅助方法中，有的带简短而有用的注释，有的代码直白、没有注释；没有适用的明确文档要求。

```python
def is_empty(self) -> bool:
    return not self.items
```

保持不加注释。名称和函数体已经提供了有用的说明，“返回 items 是否为空”只会重复。这一选择综合考虑了辅助方法的用途、简单程度、信息价值和局部背景；附近没有注释或 public 可见性，都不能单独决定结果。
