# 同时修改查找逻辑及其调用者的修复

在这个虚构 PR 审查中，用户选择在 `/work/catalog` 修复 M2，未选择交付。当时的主进度是 4 / 9 个文件，已展示 M1–M10。

M2 将类别列表查找从使用翻译名称改为使用稳定 ID。M11 和 M12 更新两个调用者，都是同一次修复的配套改动。

---

📄 **[src/catalog/category_index.ts](http://127.0.0.1:47821/diff?example=repair-index)**

**M2** · **按稳定身份查找类别列表**

> ⚖️ **合理** · 修改类别的翻译名称后，仍可通过已存类别 ID 找到原有列表。\
> 🎨 **优雅** · 单一查找所有者为两个调用者使用既有身份契约，不增加按名称兜底或第二份索引。
>
> ⏪ 查找匹配调用者传入的展示名称。
>
> ```typescript
> function itemsFor(name: string) {
>   return lists.find(list => list.name === name)?.items ?? [];
> }
> ```
>
> ⏩ 修复后的查找匹配各列表已有的稳定 ID。
>
> ```typescript
> function itemsFor(categoryId: string) {
>   return lists.find(list => list.categoryId === categoryId)?.items ?? [];
> }
> ```

---

📄 **[src/catalog/editor_controller.ts](http://127.0.0.1:47821/diff?example=repair-editor)**

M11 · 类别选择向查找传入类别 ID，使编辑展示名称后仍选中同一列表。

---

📄 **[src/catalog/gallery_controller.ts](http://127.0.0.1:47821/diff?example=repair-gallery)**

M12 · 初始化及服务更新均使用类别 ID，使翻译名称变化后仍能找到原列表。

---

M2 修复完成，没有新增发现或待处理的可选改进。M11 和 M12 均合理且优雅：两个调用者都直接使用已确认的身份契约。

必要项目检查已针对修复后内容通过。独立复审覆盖全部三个已改非测试文件，以及此前已审查且受影响的类别选择路径。修改的 `tests/catalog/category_lookup.test.ts` 为类别改名和缺失情形提供证据。[验证证据](http://127.0.0.1:47821/evidence?example=repair-checks)记录过程、结果和可用日志。

修复覆盖三个非测试文件；主进度仍为 4 / 9 个文件、10 项修改。尚未提交、发布或记录 Viewed。

- A． **通过** （推荐）：准备并提交 `/work/catalog` 中待交付的改动，将完整待发布范围发布到 PR 源，并记录符合条件的 Viewed 路径。只剩 Viewed 时，按交付指南只读审查下一组。
- B． **继续** ：保留本地修复，不交付，审查下一组。

## 必要检查无法运行

如果三个文件都已复审，但必要的应用检查无法执行，保留三个文件块，并报告 M2 修复未完成。在证据段指出缺少哪项检查及其运行器不可用。没有可选的替代方案时，在结尾说明需要恢复运行器才能完成修复。

## 选定条目是独立观察

如果优化 O1 涉及 `draft_menu.ts`、`draft_toolbar.ts` 和一项标签测试，在菜单文件下展示一次 O1，并在工具栏文件的概览中说明配套改动。将测试放在验证证据中，保持主审查计数不变。
