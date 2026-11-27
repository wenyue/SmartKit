# 包含缺陷与独立观察的一组审查

这份虚构报告展示了 PR 审阅的首个主分组，也是唯一一组。文件路径、链接、代码片段和证据均来自一个虚构的文件上传应用。

PR #42 的审阅版本为 `0123456` → `89abcde`。排除测试和已标为 Viewed 的文件后，共有两个生产文件纳入审阅。一个有改动的 [测试文件](https://example.test/repo/blob/89abcde/tests/uploads/upload_controller.test.ts) 为逐文件显示结果和重试单个失败文件提供证据。所选工作区 `/projects/uploader/.worktrees/pr-42` 已安装项目依赖，Git 状态干净。原检出目录的分支、索引和本地改动均与创建工作区前一致。

## 改动概览

假设你一次上传三份文件，其中一份失败。以前，应用只会告诉你这批文件上传失败。点重试会把三份文件都再传一遍，包括已经传成功的两份。

这次 PR 想让你看清哪些文件上传成功、哪些失败，并能只重试失败的文件。已经传成功的文件应当继续显示在结果里，无需再次上传。

---

📄 **[src/uploads/batch_upload.ts](http://127.0.0.1:47821/diff?example=upload-results)** · `+9 / −1`

**M1** · 修改｜返回每个文件的上传结果

> ⏪ 一次上传多个文件时，程序只返回整批是否成功，因此 [上传页面](http://127.0.0.1:47821/diff?example=upload-controller) 无法告诉用户哪些文件需要重试。
>
> ⏩ `uploadFiles` 为每个文件返回一项结果，记录文件及其 `uploaded` 或 `failed` 状态，让页面区分已成功上传和需要重试的文件。

---

📄 **[src/uploads/upload_controller.ts](http://127.0.0.1:47821/diff?example=upload-controller)** · `+16 / −6`

**M2** · 修改｜显示每个文件的上传结果

> 页面把原先的整批失败提示改成了每份文件各自的状态。`runUploads` 根据[每个文件的上传结果](http://127.0.0.1:47821/diff?example=upload-results)更新本次尝试涉及的行。用户重试时，先前上传成功的文件仍然可见。

**M3** · 修改｜只重试失败的文件

> ❌ ⚖️ **不合理** · **P2** · 如果两份文件上传失败，点重试会漏掉第二份。页面提供的是重试所有失败文件的操作，处理函数却用 `find` 查找，找到第一项失败就停了。
>
> 💡 找出所有失败结果，把对应的文件一起交给 `runUploads`。用同一批有两份文件失败的用例验证重试行为。

**M4** · 新增｜给文件选择器加上标签，让使用屏幕阅读器的人能识别它

**M5** · 删除｜移除整批重新上传的快捷键

> 移除这个快捷键可以避免重发已经传成功的文件。使用键盘时，可以用 Tab 键移到重试按钮，再按回车重发失败的文件。多份文件同时失败时的限制见 M3。

**O1** · 沿用上传历史的排序规则

> 🎨 **可选改进** · `recentUploads` 和 `pinnedUploads` 各自实现了 [上传历史](https://example.test/repo/blob/0123456/src/uploads/upload_history.ts) 的排序规则。两个 getter 及其调用方在固定的 base 和 head 版本中都一样。显示结果和重试时都用不到这两个 getter。
>
> 💡 共用上传历史的比较器，保留现有顺序，以后调整排序只需改一处。

---

📄 **[src/uploads/upload_history.ts](https://example.test/repo/blob/0123456/src/uploads/upload_history.ts#L25)**

**O2** · 复用现有的文件大小格式化函数

> 🎨 **可选改进** · `formatRecentSize` 和 `formatArchivedSize` 各自实现了 [现有格式化函数](https://example.test/repo/blob/0123456/src/files/format_size.ts) 的显示规则。两个函数、各自的调用方和共用的格式化函数在固定的 base 和 head 版本中都一样。逐文件显示上传结果和重试时都用不到历史记录里的文件大小文案。
>
> 💡 两处都用同一个格式化函数，以后调整文件大小的单位或舍入规则只需改一处。

---

M3 仍是 P2 不合理项。多份文件上传失败时，点一次重试会漏掉其中一些。O1 和 O2 分别建议共用比较器和文件大小格式化函数，让两种显示规则各有一处维护。

我检查了重试处理函数和改动中的测试。测试设置了三份文件，其中一份上传失败，并检查重试只发送这一份，同时保留之前成功的记录。它没有覆盖同一批有两份或更多文件失败的情况。本次只读审阅未运行测试或修复检查。

📊 **已审查 2 / 2 个文件，共 5 项改动。**

- A． **修复** （推荐）：让 M3 重试所有失败文件，运行必要检查并覆盖多份文件失败的情况，然后展示专门的复审报告。
- B． **优化** ：实施 O1 和 O2，共用比较器和文件大小格式化函数，然后检查并复审这些改动。
- C． **忽略** ：接受 M3 中点一次重试可能漏掉其他失败文件的后果。

## M3 待处理时选择优化

选择 B 授权处理两项已列明的观察。完成检查和复审后，M3 仍待处理，主进度仍为 2 / 2 个文件、5 项改动。

## 用户要求解释 M3 时

**用户** · 展开讲讲 M3。改动前后点重试分别会发送哪些文件？要怎么修？

**M3** · 修改｜只重试失败的文件

> ⏪ 假设你选了 `cover.jpg`、`map.png` 和 `notes.txt`，只有 `cover.jpg` 上传成功。此时点重试，旧的处理函数会按最初的选择，把三份文件都再传一遍。
>
> ```typescript
> async function retryUploads() {
>   await runUploads(selectedFiles);
> }
> ```
>
> ⏩ [改后的处理函数](http://127.0.0.1:47821/diff?example=upload-controller) 能读到[每个文件的上传结果](http://127.0.0.1:47821/diff?example=upload-results)。选择要重试的文件时，它会跳过已经传成功的 `cover.jpg`。
>
> ```typescript
> async function retryUploads() {
>   const firstFailed = results.find(result => result.status === "failed");
>   if (firstFailed) await runUploads([firstFailed.file]);
> }
> ```
>
> ❌ ⚖️ **不合理** · **P2** · 当 `map.png` 和 `notes.txt` 都失败时，点重试只会发送 `map.png`。`find` 找到第一项失败就停止查找，这次重试根本没有把 `notes.txt` 交给 `runUploads`。
>
> 💡 建议先收集所有失败的文件，只要列表中有文件，就一次交给上传函数。
>
> ```typescript
> async function retryUploads() {
>   const failedFiles = results
>     .filter(result => result.status === "failed")
>     .map(result => result.file);
>
>   if (failedFiles.length > 0) {
>     await runUploads(failedFiles);
>   }
> }
> ```
>
> 针对这一批文件，回归测试应验证只发起一次上传，里面有 `map.png` 和 `notes.txt`，而 `cover.jpg` 仍显示为已上传。

## 用户问起已移除的快捷键时

**用户** · 我以前用快捷键重新发送整批文件。现在用 Tab 键移到重试按钮再按回车，还会发整批吗？

**M5** · 删除｜移除整批重新上传的快捷键

> 不会。按回车会触发重试，跳过上传成功的文件。如果 `cover.jpg` 传成功了而 `map.png` 失败，这时按回车只会发送 `map.png`。如果有多份文件失败，由于 M3 的缺陷，这次只会重发第一份失败的文件。
