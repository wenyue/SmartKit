# 包含缺陷与独立观察的一组审查

这份虚构报告展示了 PR 审查的首个主分组，也是唯一一组。

编辑器在保存前弹窗询问是否继续，保存成功后才显示结果消息。用户要知道保存了哪份草稿，也要能关掉弹窗后再次尝试保存。这次 PR 希望在结果里说明保存的是哪份草稿，即使它没有名字，并让保存结束后的清理过程更容易看懂。固定 PR 比较排除测试和此前标记为 Viewed 的文件后，共有两个符合审查范围的文件。

---

📄 **[src/editor/labels.dart](http://127.0.0.1:47821/diff?example=labels)** · `+1 / −0`

**M1** · **让其他地方也能用现有的草稿名称**

> ⏪ [草稿列表](https://example.test/repo/blob/0123456/src/editor/draft_list.dart) 使用这里为未命名草稿提供的默认名称，格式化逻辑只在当前文件内可用。
>
> ⏩ 新增公开的 `draftLabel` 函数，沿用原来的格式化逻辑，让 [保存结果消息](http://127.0.0.1:47821/diff?example=complete-report) 可以显示用户在列表里看到的同一个名称。

---

📄 **[src/editor/save_controller.dart](http://127.0.0.1:47821/diff?example=complete-report)** · `+5 / −3`

**M2** · **在保存结果中写明草稿名称**

> ⏪ 结果消息只说保存成功，用户得自己记得刚才保存的是哪份草稿。
>
> ⏩ 结果消息用 [共用的标签格式化逻辑](http://127.0.0.1:47821/diff?example=labels) 显示草稿名称。

**M3** · **将清理移到各结果分支**

> ⏪ 每次保存尝试结束时，同一段清理代码会清除「正在保存」的标记。要看成功或失败时编辑器怎样恢复可用，得找到这段清理代码。
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
> ⏩ 将清除标记的代码分别放到成功和失败的处理逻辑里，希望让每种结果更好追踪。
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
>
> ❌ ⚖️ **不合理** · **P2** · 关掉保存前的确认框后再点保存，编辑器会忽略这次请求。取消时跳过了清除「正在保存」标记的代码，编辑器因此仍以为保存尚未结束。
>
> 💡 恢复统一的清理代码。设置标记后，无论从哪里退出，包括取消，都清除标记。

**O1** · **使用既有草稿排序策略**

> 🎨 **可选改进** · `recentDrafts` 和 `pinnedDrafts` 各自实现了 [草稿列表](https://example.test/repo/blob/0123456/src/editor/draft_list.dart) 的排序逻辑。两个 getter 及调用方在固定的 base 和 head 版本中一样。保存和保存前的弹窗都用不到它们。
>
> 💡 共用草稿列表里的比较器，保留现有顺序，以后修改排序只需要改一处。

---

📄 **[src/editor/draft_menu.dart](https://example.test/repo/blob/0123456/src/editor/draft_menu.dart#L25)**

**O2** · **使用既有未命名草稿标签**

> 🎨 **可选改进** · `renameAction` 和 `copyAction` 各自为未命名草稿提供默认名称。两个动作及 [标签格式化器里的默认名称](http://127.0.0.1:47821/diff?example=labels) 在固定的 base 和 head 版本中都一样。[保存结果消息](http://127.0.0.1:47821/diff?example=complete-report) 是共用标签函数的新调用方。
>
> 💡 两个菜单动作共用同一个格式化方法，未命名草稿的显示名称集中在一处维护。

---

M3 仍为 P2 不合理项，因为取消保存可能导致下一次保存不可用。O1 和 O2 分别建议复用比较器和格式化器，让两种策略各有一个维护位置。

关闭保存前的确认框时，处理函数返回 `false`。源码检查追踪了这个结果如何触发提前退出，并使下一次保存被入口拦下。尚未运行修复检查。

📊 **已审查 2 / 2 个文件，共 3 项修改。**

- A． **修复** （推荐）：恢复 M3 的统一清理，运行必要检查，并展示专门的复审报告。
- B． **优化** ：实施 O1 和 O2，复用比较器和标签格式化器，然后检查并复审这些改动。
- C． **忽略** ：接受 M3 中取消保存可能导致下一次保存不可用的后果。

## M3 待处理时选择优化

选择 B 授权处理两项已列明的观察。完成它们的检查和复审后，M3 仍待处理，主进度仍为 2 / 2 个文件、3 项修改。
