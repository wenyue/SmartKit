# 包含缺陷与独立观察的一组审查

这份虚构报告展示了 PR 审查的最后一个主分组。

本组覆盖固定 PR 比较中的两个合格非测试文件；统计前已排除测试及此前标记为 Viewed 的文件。

---

📄 **[src/editor/labels.dart](http://127.0.0.1:47821/diff?example=labels)**

M1 · 保存确认使用既有草稿标签格式化器，让未命名草稿显示与草稿列表一致的兜底标签。

---

📄 **[src/editor/save_controller.dart](http://127.0.0.1:47821/diff?example=complete-report)**

该控制器保存草稿并报告进度。此次改动在确认消息中标明已保存草稿，并移动进行中状态的清理逻辑。

M2 · 保存确认标明草稿名称，让用户知道保存了哪份草稿。

**M3** · **将清理移到各结果分支**

> ⚖️ ❌ **不合理** · **P2** · 关闭确认框后 `pending` 仍为真，保存入口因此拒绝同一编辑会话里的下一次保存。\
> 🎨 ❌ **需要改进** · 各结果分支遗漏了取消时的清理，应恢复统一的完成块，覆盖设置 `pending` 后的每条退出路径。
>
> ⏪ 完成块在每次保存尝试后清除进行中状态。
>
> ```dart
> if (pending) return;
> pending = true;
> try {
>   if (await confirmSave() == false) return;
>   await persistDraft(draft);
> } finally {
>   pending = false;
> }
> ```
>
> ⏩ 成功和失败在取消检查之后分别清理状态。
>
> ```dart
> if (pending) return;
> pending = true;
> if (await confirmSave() == false) return;
> try {
>   await persistDraft(draft);
>   pending = false;
> } catch (_) {
>   pending = false;
>   rethrow;
> }
> ```

**O1** · **使用既有草稿排序策略**

> 🎨 **可选改进** · 未修改的 `recentDrafts` 和 `pinnedDrafts` getter 重复实现了草稿列表拥有的比较器；使用既有比较器，可以让三个视图遵循同一排序策略。

两个 getter 及其调用方在固定的 base 和 head 中都相同。保存和确认路径都不使用这两个 getter。复用比较器会保留现有顺序，并让以后的排序调整只需改一处。

---

📄 **[src/editor/draft_menu.dart](https://example.test/repo/blob/0123456/src/editor/draft_menu.dart#L25)**

**O2** · **使用既有未命名草稿标签**

> 🎨 **可选改进** · 未修改的 `renameAction` 和 `copyAction` 重复实现了标签格式化器的兜底逻辑；调用该格式化器，可以让菜单与保存确认遵循同一标签策略。

两个菜单动作及格式化器的兜底逻辑在固定的 base 和 head 中都相同。保存确认是格式化器唯一新增的调用方，菜单动作仍各自计算兜底标签。

---

M3 仍为 P2 不合理项，因为取消保存可能导致下一次保存不可用。O1 和 O2 分别建议复用比较器和格式化器，让两种策略各有一个维护位置。

关闭确认框时，确认处理函数返回 `false`。源码检查追踪了这个结果如何触发提前退出，并使下一次保存被入口拦下。尚未运行修复检查。

📊 **已审查 2 / 2 个文件，共 3 项修改。**

- A． **修复** （推荐）：恢复 M3 的统一清理，运行必要检查，并展示专门的复审报告。
- B． **优化** ：实施 O1 和 O2，复用比较器和标签格式化器，然后检查并复审这些改动。
- C． **忽略** ：接受 M3 中取消保存可能导致下一次保存不可用的后果。

## M3 待处理时选择优化

选择 B 授权处理两项已列明的观察。完成它们的检查和复审后，M3 仍待处理，主进度仍为 2 / 2 个文件、3 项修改。
