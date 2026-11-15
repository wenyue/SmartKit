# Report Format

The [Skill entry](../SKILL.md) owns assessment, findings, identities, progress, action labels, and decisions. This reference owns how to present them: scope, file blocks, explanation depth, closing, and menus. Ordinary, supplementary, repair, and selected-O reports share this layout. The entry's scenario examples illustrate its use; their fictional paths, source, checks, and results establish no execution evidence.

## Establish the report's scope

Identify what the reader is about to assess. Open the first ordinary group with the purpose of the reviewed change, the prior situation that prompted it, and what users or callers should be able to do when it works. Give enough context for a reader new to the project. Put the summary of review findings in the closing. Later ordinary introductions identify the group. A supplementary introduction identifies the additional delivery coverage. A repair introduction names the selected original M/O items and connects their supporting changes. Keep supplementary and repair coverage separate from unseen main groups.

Use one file block per assessed file, with a single horizontal rule before the first block, between blocks, and before the closing. For an assessed diff, start the heading with 📄 and the bold, full repository-relative filename link returned by `local_web`, unchanged. For text files, append a middle dot and `+N / −N`, the verified added and deleted line counts for the assessed versions. Binary diff and source-only headings omit the counts. A short overview may explain the file's role or accompanying changes. When describing another file or behavior it owns, link to its verified diff or source. A file-level link is enough when the explanation spans the file or a flow across files.

Fill the placeholders in the report language. The [worked review group](../examples/review-group.md) shows the wording for titles, verdicts, and progress.

````markdown
<PURPOSE_AND_SCOPE>

---

📄 **[<PATH_1>](<URL_1>)** · `+1 / −1`

**M1** · **<TITLE_1>**

> ⏪ <PRIOR_BEHAVIOR_1>
>
> ⏩ <CHANGED_BEHAVIOR_1>

---

📄 **[<PATH_2>](<URL_2>)** · `+9 / −4`

**M2** · **<TITLE_2>**

> ⏪ <PRIOR_BEHAVIOR_2>
>
> ```<LANGUAGE>
> <PRIOR_CODE>
> ```
>
> ⏩ <CHANGED_BEHAVIOR_2>
>
> ```<LANGUAGE>
> <CHANGED_CODE>
> ```
>
> ❌ ⚖️ **<VERDICT>** · **P2** · <FINDING>
>
> 💡 <REMEDY>

---

<RESULT_AND_DECISIONS>

<EVIDENCE_AND_LIMITS>

📊 **<MAIN_PROGRESS>**

<CHOICES_OR_AUTHORIZED_WORK>
````

The progress line shown here belongs to an ordinary main group. Supplementary and repair reports state their own coverage and, when useful, that saved main progress is unchanged; they add no reviewed main files or modifications.

## Explain modifications at the needed depth

Put the bold ID and bold title on one unindented line, separated by a plain middle dot. In one Markdown blockquote below it, start with ⏪ and describe the prior behavior and the concrete problem or limitation that motivated the change. Then use ⏩ to explain what changed and how it addresses that need. Start the prose immediately after each icon. Use plain language a reader without project context can follow. When the old behavior already depends on a necessary guarantee, explain that guarantee and what prompted the proposed change.

For a straightforward modification without an actionable finding, worthwhile optional improvement, or material uncertainty, one natural sentence after each icon is enough. Use more detail for those findings and for consequential mechanisms the reader needs to understand. When code helps explain the behavior, show concise actual snippets beside the relevant explanation, retaining the error, state, or lifecycle context. Label illustrative simplifications. For a repair, compare the pre-repair and repaired contents. Separate items with ordinary paragraph spacing.

After ⏩, show only actionable findings, worthwhile optional improvements, or material uncertainty. Write each issue once under the relevant axis, explaining the concrete cause and observable effect or trade-off. Use an example when it makes a trigger or consequence easier to understand. Prefix actual defects with ❌ ⚖️ or ❌ 🎨 and show their severity. A structural defect shown as ❌ 🎨 **Needs improvement** retains its classification as an unreasonable finding under the entry. Prefix a concrete remedy or the evidence needed to resolve an uncertainty with 💡 alone. Keep these paragraphs in the same blockquote.

Use the same item layout after repair or optimization. Keep any remaining actionable findings, material uncertainty, or consequential design choice visible.

## Preserve identities and visible coverage

Show every changed non-test file in a repair report, including supporting files. Tests appear with verification evidence under the repository's classification. Compact presentation does not narrow complete repair or affected-context assessment.

Keep an existing item's ID and explain it once under its responsible file. Separately explained supporting modifications take the next unused M IDs from the entry's continuous sequence; connect them to the original repair in the introduction. For example, a repair after M1–M10 can contain M2, M11, and M12 across three files without changing main progress. References to M2 explain the relationship rather than creating another numbered item. Accompanying changes without a separate item can use a short file overview.

In selected-O work, keep the selected O IDs and use file overviews for supporting changes; they create neither new O observations nor M items. Use the same before/after layout and surface any resulting finding under the responsible selected item.

Place incidental O items after M items under their source file. A file containing only O items has the same heading with a verified source link and follows the main file blocks. If no single-file attribution is useful, put the observations after the file blocks with a horizontal rule before them and before the closing. Include the entry's required evidence, impact, independence, and recommendation or benefit; any judgment lines follow the same icon and severity conventions. Placement changes neither main progress nor delivery or Viewed eligibility.

## Close with the result and the next decision

Keep these four parts in order and omit empty categories:

1. **Result and decisions.** State the group conclusion or the repair's actual completion status. Name pending unreasonable IDs with severity and impact, retained trade-offs, and outstanding optional remedies and benefits. Summarize material uncertainty separately with ⚠️, the corresponding item IDs, observed risks, and unresolved context.
2. **Evidence and limits.** State the checks actually performed, results, and material gaps. For a repair, identify coverage of all changed non-test files and affected previously reviewed context, with verification records and available logs. Distinguish successful edits from unavailable required checks or incomplete re-review, which leave the dependent remedy incomplete. Tests remain evidence, and author-reported checks remain distinguishable from executed checks.
3. **Progress or coverage.** For a main group, show only the cumulative reviewed-file fraction and actual main-modification count in the report language. For supplementary, repair, or selected-O work, state its coverage separately and preserve the saved main total and position.
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

Confirm the first group's purpose explains why the change is needed. Check that file counts and links match the assessed versions and that every required file and cross-file reference is linked. Check stable IDs, one standalone appearance per item, and judgments after the comparison with each issue explained once. Check O placement, accurate repair status and checks, unchanged main progress for additional coverage, visible uncertainty warnings, and the menu's punctuation, scope, recommendation, and effects.
