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

**M1** · **<ONE_LINE_CHANGE>**

---

📄 **[<PATH_2>](<URL_2>)** · `+9 / −4`

**M2** · **<TITLE_2>**

> ⏪ <PRIOR_BEHAVIOR_2>
>
> ⏩ <CHANGED_BEHAVIOR_2>
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

Choose depth for each modification after assessing it on both axes. Two changes in one file can warrant different treatment. Use the full walkthrough as the reference and keep only the parts the reader needs at each shorter depth.

- **At a glance.** For a tiny change you can confidently judge reasonable and elegant, state what changed on the ID and title line alone.
- **Comparison.** For the remaining changes with no defect, worthwhile optional improvement, or material uncertainty to report, show ⏪ what happened before and why it mattered, then ⏩ what happens after and how it meets the need. Include a consequential mechanism or a guarantee callers still depend on when it explains the choice.
- **Issue detail.** When a modification has a defect, keep ⏪ and ⏩ brief to leave room for what goes wrong in the assessed version. Open a behavior finding with its concrete trigger and what the user or caller sees, in everyday words. For a structural defect, identify the obligation it violates and the concrete consequence for callers or maintainers. Explain the cause and give an actionable remedy. Give a worthwhile optional improvement or material uncertainty comparable attention under its own judgment. For an improvement, explain the burden and the benefit of the proposed change. For uncertainty, explain what is known, what is at stake, and what evidence would settle it.
- **Requested walkthrough.** Use the full explanation only when the user explicitly asks you to explain a particular file or modification, regardless of its verdict. Walk a concrete case through ⏪ the original behavior and ⏩ the assessed change. Follow the changed path far enough to answer the user's question, including any remaining issue and how its remedy would work. When code helps, show enough of the proposed implementation for the reader to follow the fix. A request to review a file or a general question uses the ordinary depths.

Put the bold ID and bold title on one unindented line, separated by a plain middle dot. For items with a body, keep the comparison and any judgments together in one Markdown blockquote. Start the prose immediately after ⏪ and ⏩. Separate items with ordinary paragraph spacing. For repairs and optimizations, compare the pre-repair and repaired contents.

Give each item enough context to stand on its own. In a before/after explanation, illustrate an old bug that motivated the change with a simple trigger and outcome in ⏪. Where they make the case easier to grasp, favor concise excerpts of the actual before and after code, a diagram tracing paths or states, or suggested code illustrating a fix. Use plain prose when it is clearer or an excerpt would bury the point. Preserve relevant state, error, and lifecycle context in excerpts and label illustrative simplifications or proposed code. Define unfamiliar terms where they first appear. Quote UI text as displayed in the assessed version and leave paraphrases unquoted.

After ⏩, show only defects, worthwhile optional improvements, or material uncertainty as judgments. Explain each issue once under the relevant axis. Prefix defects with ❌ ⚖️ or ❌ 🎨 and show their severity. A structural defect shown as ❌ 🎨 **Needs improvement** retains its classification as an unreasonable finding under the entry. Use 🎨 **Optional improvement** for a worthwhile optional remedy and ⚠️ ⚖️ or ⚠️ 🎨 for an **Uncertain** judgment. Prefix a concrete remedy or the evidence needed to resolve an uncertainty with 💡 alone.

## Preserve identities and visible coverage

Show every changed non-test file in a repair report, including supporting files. Tests appear with verification evidence under the repository's classification. Compact presentation does not narrow complete repair or affected-context assessment.

Keep an existing item's ID and explain it once under its responsible file. Separately explained supporting modifications take the next unused M IDs from the entry's continuous sequence; connect them to the original repair in the introduction. For example, a repair after M1–M10 can contain M2, M11, and M12 across three files without changing main progress. References to M2 explain the relationship rather than creating another numbered item. Accompanying changes without a separate item can use a short file overview.

In selected-O work, keep the selected O IDs and use file overviews for supporting changes; they create neither new O observations nor M items. Choose depth for each selected item's modification and surface any resulting finding under the responsible selected item.

Place incidental O items after M items under their source file. A file containing only O items has the same heading with a verified source link and follows the main file blocks. If no single-file attribution is useful, put the observations after the file blocks with a horizontal rule before them and before the closing. Include the entry's required evidence, impact, independence, and recommendation or benefit; any judgment lines follow the same icon and severity conventions. Placement changes neither main progress nor delivery or Viewed eligibility.

## Close with the result and the next decision

Keep these four parts in order and omit empty categories:

1. **Result and decisions.** State the group conclusion or the repair's actual completion status. Name pending unreasonable IDs with severity and impact, retained trade-offs, and outstanding optional remedies and benefits. Summarize material uncertainty separately with ⚠️, the corresponding item IDs, observed risks, and unresolved context.
2. **Evidence and limits.** State the checks actually performed, results, and material gaps. When reporting a test coverage gap, check the existing cases and their setup paths. Name the specific condition or sequence left untested. For a repair, identify coverage of all changed non-test files and affected previously reviewed context, with verification records and available logs. Distinguish successful edits from unavailable required checks or incomplete re-review, which leave the dependent remedy incomplete. Tests remain evidence, and author-reported checks remain distinguishable from executed checks.
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

Confirm the first group places the standalone Change Overview section after verified scope and workspace context and before the horizontal rule that introduces the first file block. Check that the overview explains why the change is needed. Read each item on its own, then read each finding's first sentence by itself from the perspective of a reader new to the project. If understanding a behavior finding's trigger or outcome requires knowing an internal state name, storage operation, or project-specific term, rewrite the opening. Describe the concrete action or situation in everyday words and state what the user or caller observes. Put the exact technical condition and cause in the following explanation and briefly define unfamiliar terms there. Verify that quoted UI text matches the displayed wording.

Check that file counts and link destinations match the assessed versions. Check that every required file has a usable link and that each screen, caller, or owner named from another file is linked at its mention. Check stable IDs, one standalone appearance per item, and judgments after the comparison with each issue explained once. Check O placement, accurate repair status and checks, unchanged main progress for additional coverage, visible uncertainty warnings, and the menu's punctuation, scope, recommendation, and effects.
