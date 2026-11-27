# 同时修改查找逻辑及其调用者的修复

在这个虚构 PR 审查中，用户选择在 `/work/catalog` 修复 M2，未选择交付。当时的主进度是 4 / 9 个文件，已展示 M1–M10。

M2 恢复了类别改名后查看原保存列表的能力。M11 和 M12 更新 [类别选择](http://127.0.0.1:47821/diff?example=repair-editor) 和 [刷新图库](http://127.0.0.1:47821/diff?example=repair-gallery) 两处调用，让它们传入同一个稳定的类别 ID。

---

📄 **[src/catalog/category_index.ts](http://127.0.0.1:47821/diff?example=repair-index)** · `+2 / −2`

**M2 · 修改｜按稳定身份查找类别列表**

> ⏪ 查找靠名称匹配。类别改名后，调用方传入的是新名称，已保存的列表还记着旧名称，所以查找会返回空列表，即使原来保存的内容还在。
>
> ```typescript
> function itemsFor(name: string) {
>   return lists.find(list => list.name === name)?.items ?? [];
> }
> ```
>
> ⏩ 根据列表里已经保存的稳定 ID 查找。类别改名后，依然能查出原来的内容。
>
> ```typescript
> function itemsFor(categoryId: string) {
>   return lists.find(list => list.categoryId === categoryId)?.items ?? [];
> }
> ```

---

📄 **[src/catalog/editor_controller.ts](http://127.0.0.1:47821/diff?example=repair-editor)** · `+1 / −1`

**M11 · 修改｜类别改名后继续选中原来的列表**

> 编辑器把类别 ID 传给 [查找方法](http://127.0.0.1:47821/diff?example=repair-index)，类别改名后仍选中原来的列表。

---

📄 **[src/catalog/gallery_controller.ts](http://127.0.0.1:47821/diff?example=repair-gallery)** · `+2 / −2`

**M12 · 修改｜打开或刷新图库时找到同一个列表**

> 打开和刷新图库时，都把类别 ID 传给 [查找方法](http://127.0.0.1:47821/diff?example=repair-index)，因此翻译变化后仍能找到原先保存的内容。

---

M2 修复完成，没有新增发现或待处理的可选改进。

必要项目检查已针对修复后内容通过。独立复审覆盖全部三个已改非测试文件，以及此前已审查且受影响的类别选择路径。[类别查找测试](https://example.test/repo/blob/0123456/tests/catalog/category_lookup.test.ts) 为类别改名和缺失情形提供证据。[验证证据](http://127.0.0.1:47821/evidence?example=repair-checks) 记录过程、结果和可用日志。

修复覆盖三个非测试文件。主进度仍为 4 / 9 个文件、10 项改动。尚未提交、发布或记录 Viewed。

- A． **通过** （推荐）：准备并提交 `/work/catalog` 中待交付的改动，将完整待发布范围发布到 PR 源，并记录符合条件的 Viewed 路径。只剩 Viewed 时，按交付指南只读审查下一组。
- B． **继续** ：保留本地修复，不交付，审查下一组。

## 必要检查无法运行

如果三个文件都已复审，但必要的应用检查无法执行，保留三个文件块，并报告 M2 修复未完成。在证据段指出缺少哪项检查及其运行器不可用。没有可选的替代方案时，在结尾说明需要恢复运行器才能完成修复。

## 选定条目是独立观察

如果优化 O1 是为了统一 `draft_menu.ts` 和 `draft_toolbar.ts` 中已有的菜单标签，就在菜单文件下展示一次 **O1 · 修改｜统一草稿操作的标签** 。在工具栏文件的概览中说明配套改动，标签测试则列在验证证据里。主审查计数沿用原值。
