# Report Format

The [Skill entry](../SKILL.md) owns assessment, findings, identities, progress, action labels, and decisions. This reference owns how to present them: scope, file blocks, explanation depth, closing, and menus. Ordinary, supplementary, repair, and selected-O reports share this layout. The entry's scenario examples illustrate its use; their fictional paths, source, checks, and results establish no execution evidence.

## Establish the report's scope

Open the first ordinary group with the review target, the comparison, the eligible file count, and applicable exclusions. Mention relevant test files as behavior evidence. Identify the selected workspace or fixed snapshot mode. Include relevant facts already verified about environment readiness and Git state, including preservation of the original checkout when a separate workspace was prepared.

Before the first file block, add a standalone level-two Markdown section titled “Change Overview” in the report language. Explain the concrete problem, what changes, and the intended result for users or callers so a reader new to the project can follow. Use everyday language and enough context to connect those points. Choose paragraphs, bulleted lists, or numbered lists according to what makes the explanation clearest. Put the summary of review findings in the closing.

Use this structure for the first group's `<REPORT_INTRODUCTION>`.

```markdown
<REVIEW_SCOPE_AND_WORKSPACE>

## <CHANGE_OVERVIEW_HEADING>

<CHANGE_OVERVIEW>
```

Later ordinary introductions identify the group. A supplementary introduction identifies the additional delivery coverage. A repair introduction names the selected original M/O items and connects their supporting changes. Keep supplementary and repair coverage separate from unseen main groups.

Use one file block per assessed file, with a single horizontal rule before the first block, between blocks, and before the closing. For an assessed diff, start the heading with 📄 and the bold, full repository-relative filename link. Preserve the `local_web` Markdown unchanged when using that route. For the fixed Snapshot alternative in the entry, keep the same full filename label and link to the verified fixed file comparison. For text files, append a middle dot and `+N / −N`, the verified added and deleted line counts for the assessed versions. Binary diff and source-only headings omit the counts. A short overview may explain the file's role or accompanying changes.

Place each cross-file link on the words that identify the other file, its symbol, or its behavior. Link to the verified diff or source. A file-level link is enough when discussing the file as a whole or a flow across files. Use link syntax the current viewer supports. For a Windows Markdown link to a local source file by path, start the destination immediately with the drive letter, as in `[label](D:/project/src/task.dart)`. Verify the file at the absolute path used in the link. Keep SmartKit diff targets exactly as generated.

Fill the placeholders in the report language. The [worked review group](../examples/review-group.md) shows the first group's opening, titles, verdicts, and progress.

````markdown
<REPORT_INTRODUCTION>

---

📄 **[<PATH_1>](<URL_1>)** · `+1 / −1`

**M1** · Add | <NEW_CAPABILITY_AND_PURPOSE>

---

📄 **[<PATH_2>](<URL_2>)** · `+9 / −4`

**M2** · Modify | <CHANGED_BEHAVIOR>

> ❌ ⚖️ **<VERDICT>** · **P2** · <TRIGGER_AND_IMPACT>
>
> 💡 <REMEDY>

**M3** · Delete | <REMOVED_ENTRY_POINT>

> <REASON_AND_CALLER_IMPACT>

---

<RESULT_AND_DECISIONS>

<EVIDENCE_AND_LIMITS>

📊 **<MAIN_PROGRESS>**

<CHOICES_OR_AUTHORIZED_WORK>
````

The progress line shown here belongs to an ordinary main group. Supplementary and repair reports state their own coverage and, when useful, that saved main progress is unchanged; they add no reviewed main files or change items.

## Explain each change in its own terms

In each item heading, bold only the stable ID. For a change item, follow it with the kind and a concrete summary in the report language. In Chinese, use 新增、修改、删除, as in “**M2** · 修改｜重试失败的上传”. Name the behavior, entry point, responsibility, or contract the item explains. Choose the kind by tracing what happened to it across the assessed versions, following callers to a counterpart at another path when needed. One file can contain several kinds. For a repair or optimization, compare the contents immediately before and after that work.

| Kind | What the reader needs |
| --- | --- |
| **Add** | Name what is newly available and the purpose it serves. Identify who uses it or the problem it solves. |
| **Modify** | Name the existing behavior or responsibility and what changed about it. Explain it directly, or use ⏪ for the specific prior behavior and ⏩ for its counterpart when pairing them makes the effect clearer. |
| **Delete** | Name what was removed, why, and the material effect on existing callers. If an alternative exists, explain which uses it covers and what affected callers still need to do. |

Explain additions and deletions directly. Ground the reason in requirements, callers, or the diff. When only the effect is established, report it. Call out missing rationale only when it affects a judgment. Keep any body and judgments together in one Markdown blockquote below the heading. When using arrows, start the prose immediately after each arrow. Separate items with ordinary paragraph spacing.

### Choose the depth the reader needs

Assess reasonableness and elegance before choosing how much to write. All four approaches apply to any kind. A request that only limits the review to a file uses ordinary review judgment.

- **At a glance.** Use the heading alone when the change is tiny, you can confidently judge it reasonable and elegant, and the heading conveys everything the reader needs for its kind. For example, “**M6** · Modify | Correct the size label from KB to KiB to match the displayed 1,024-byte units” is a complete item.
- **Ordinary explanation.** When the heading needs context, add the reason, mechanism, or consequence that helps the reader understand the change. Include a guarantee callers depend on when it explains the choice.
- **Issue detail.** Whenever the assessment yields a defect, worthwhile optional improvement, or material uncertainty, put it under the item's heading. Give only the change context needed to understand the finding. For a behavior defect, open with the trigger and what the user or caller observes, then explain the cause and remedy. For a structural defect, identify the violated obligation, the consequence for callers or maintainers, and the correction. For an optional improvement, explain the burden, the remedy, and its benefit. For material uncertainty, give the known facts, which judgment depends on the missing evidence, and what would settle it.
- **Requested walkthrough.** When the user explicitly asks to explain a particular file or item, answer their question directly. Trace a concrete case as far as needed. When expanding a reported change, keep its original heading, including the ID and kind, and carry forward any applicable finding. If the question concerns that finding, explain it once in the answer.

Give each item enough context to stand alone. If an old bug motivated a modification, a simple trigger and outcome can make the comparison clear. Where they help, use concise actual excerpts, a diagram of paths or states, or enough proposed code to follow a fix. Preserve relevant state, error, and lifecycle context and label illustrative simplifications or proposed code. Define unfamiliar terms where they first appear. Quote UI text as displayed in the assessed version and leave paraphrases unquoted.

Show only defects, worthwhile optional improvements, or material uncertainty as judgments. Explain each issue once under the relevant axis. Prefix defects with ❌ ⚖️ or ❌ 🎨 and show their severity. A structural defect shown as ❌ 🎨 **Needs improvement** retains its classification as an unreasonable finding under the entry. Use 🎨 **Optional improvement** for a worthwhile optional remedy and ⚠️ ⚖️ or ⚠️ 🎨 for an **Uncertain** judgment. Prefix a concrete remedy or the evidence needed to resolve an uncertainty with 💡 alone.

## Preserve identities and visible coverage

Show every changed non-test file in a repair report, including supporting files. Tests appear with verification evidence under the repository's classification. Compact presentation does not narrow complete repair or affected-context assessment.

Keep an existing item's ID and explain it once under its responsible file. Separately explained supporting changes take the next unused M IDs from the entry's continuous sequence; connect them to the original repair in the introduction. For example, a repair after M1–M10 can contain M2, M11, and M12 across three files without changing main progress. References to M2 explain the relationship rather than creating another numbered item. Accompanying changes without a separate item can use a short file overview.

In selected-O work, keep the selected O IDs and use file overviews for supporting changes; they create neither new O observations nor M items. Label and explain the implemented change under its selected O ID, with any resulting finding.

Keep the ID and title for an incidental O observation without a change label. Place these O items after M items under their source file. A file containing only O items has the same heading with a verified source link and follows the main file blocks. If no single-file attribution is useful, put the observations after the file blocks with a horizontal rule before them and before the closing. Include the entry's required evidence, impact, independence, and recommendation or benefit; any judgment lines follow the same icon and severity conventions. Placement changes neither main progress nor delivery or Viewed eligibility.

## Close with the result and the next decision

Keep these four parts in order and omit empty categories:

1. **Result and decisions.** State the group conclusion or the repair's actual completion status. Name pending unreasonable IDs with severity and impact, retained trade-offs, and outstanding optional remedies and benefits. Summarize material uncertainty separately with ⚠️, the corresponding item IDs, observed risks, and unresolved context.
2. **Evidence and limits.** State the checks actually performed, results, and material gaps. When reporting a test coverage gap, check the existing cases and their setup paths. Name the specific condition or sequence left untested. For a repair, identify coverage of all changed non-test files and affected previously reviewed context, with verification records and available logs. Distinguish successful edits from unavailable required checks or incomplete re-review, which leave the dependent remedy incomplete. Tests remain evidence, and author-reported checks remain distinguishable from executed checks.
3. **Progress or coverage.** For a main group, show only the cumulative reviewed-file fraction and number of displayed main change items in the report language. For supplementary, repair, or selected-O work, state its coverage separately and preserve the saved main total and position.
4. **Choices or remaining authorized work.** Render the entry's applicable menu with concrete IDs, effects, and next position. If delivery is already selected, retain its pending intent and use that decision table. When no new decision remains, state and continue the authorized work without asking for Pass again. Explain an unavailable prerequisite without a selectable remedy as a limitation, not an invented action choice.

## Render choices consistently

Selection, labels, recommendation, ordering, and scope come from the entry and its stage tables. Use a Markdown unordered list with one option per item, consecutive uppercase letters, and no blank lines between items. Start with `- `, the letter, a short bold action label, an optional recommendation outside the bold span, a colon, and the concrete effects. Bold only the action label.

These patterns illustrate punctuation and spacing, not the actions for a particular report:

```markdown
- A. **Pass** (recommended): Prepare and complete applicable delivery, then review the next group.
- B. **Continue**: Review the next group without delivery.
```

For Chinese, use full-width `．` and `：`, spaces on both sides of the bold label, and `（推荐）` outside it. Pass renders as `通过`, Continue as `继续`, and Finish as `结束`; other action labels retain their corresponding meanings.

```markdown
- A． **通过** （推荐）：准备并完成适用的交付，然后审阅下一组。
- B． **继续** ：从下一组开始只读审阅。
```

Use the same rendering for workspace menus. At scope end use Finish rather than Continue, under the entry's action semantics.

## Check the report before sending

Confirm the first group places the standalone Change Overview section after verified scope and workspace context and before the horizontal rule that introduces the first file block. Check that the overview explains why the change is needed. Read each item on its own, then read each finding's first sentence by itself from the perspective of a reader new to the project. If understanding a behavior finding's trigger or outcome requires knowing an internal state name, storage operation, or project-specific term, rewrite the opening. Describe the concrete action or situation in everyday words and state what the user or caller observes. Put the exact technical condition and cause in the following explanation and briefly define unfamiliar terms there. Verify that quoted UI text matches the displayed wording.

Check that file counts and link destinations match the assessed versions. Check that every required file has a usable link and that each screen, caller, or owner named from another file is linked at its mention. Check each item's ID and kind against the assessed change. Read additions and deletions for purpose and caller impact, and each before/after pair for a specific counterpart. Check that each item appears once with its judgments after the explanation. Check O placement, accurate repair status and checks, unchanged main progress for additional coverage, visible uncertainty warnings, and the menu's punctuation, scope, recommendation, and effects.
