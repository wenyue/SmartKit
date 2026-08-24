# Acceptance Standard 变更

候选项变更公共编写 Skill、Reviewer 规则或 Acceptance Standard 时，不得通过依据其自身已削弱的候选
文本为自己评分来获得资格。

使用以下基础：

```text
Qualification Basis = Previous Accepted Standard + Accepted Standard Change
```

## 在候选项审查前接受变更

1. 根据已接受对话、Issue 或 Spec，形成一个内容冻结的 Proposed Standard Change。说明其来源、
   显式变更、保留义务和非目标。不得从候选项推断允许的变更。
2. 顶层 Soft-Isolation Probe 通过后，向一个独立的无工具 Reviewer 提供一份 Context Packet，其中
   只包含 Previous Accepted Standard、已接受用户目标、Proposed Standard Change 和显式选定的
   共享 Rules。它判断完整性、一致性、可验证性，以及每项未变更义务是否得到保留。
3. 得到 `PASS` 后，把经过审查的确切内容作为 Accepted Standard Change 保留在控制器上下文中。得到
   `FAIL` 时，修正提案并使用新的 Soft-isolated Reviewer；该提案尚未成为 Standard 的一部分。
4. 根据 Previous Accepted Standard 加上该 Accepted Standard Change 评估实际候选项。只有完全
   合格的规范 Candidate Revision 才成为最新的 accepted Standard。

独立的变更审查检验新要求是否合理；后续候选项审查检验实现是否满足该要求。不得仅为资格认定而持久化提案、
packet、摘要 manifest 或审查报告。最终 Standard 和 ADR 保留持久结果。
