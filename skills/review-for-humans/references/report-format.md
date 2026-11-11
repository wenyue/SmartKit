# Report Format

The [Skill entry](../SKILL.md) owns assessment, findings, identities, progress, action labels, and decisions. This reference owns how to present them: scope, file blocks, explanation depth, closing, and menus. Ordinary, supplementary, repair, and selected-O reports share this layout. The entry's scenario examples illustrate its use; their fictional paths, source, checks, and results establish no execution evidence.

## Establish the report's scope

Identify what the reader is about to assess. An ordinary introduction identifies the group. A supplementary introduction identifies the additional delivery coverage. A repair introduction names the selected original M/O items and connects their supporting changes. Keep supplementary and repair coverage separate from unseen main groups.

Use one file block per assessed file, with a single horizontal rule before the first block, between blocks, and before the closing. The file heading is 📄 followed by the bold, full repository-relative filename link returned by `local_web`, unchanged. A short overview may explain the file's role or accompanying changes. Use the filename as the diff link; add other links only for distinct evidence the reader needs.

````markdown
<report scope and original-item relationship, when needed>

---

📄 **[<full/repository-relative/path>](<returned-url>)**

M1 · <one natural sentence explaining the change and why it matters>

---

📄 **[<another/full/path>](<returned-url>)**

**M2** · **<detailed change title>**

> ⚖️ ❌ **Unreasonable** · **P2** · <defect and user or caller consequence>\
> 🎨 ❌ **Needs improvement** · <design problem and remedy>
>
> ⏪ <earlier implementation>
>
> ```<language>
> <relevant actual earlier code>
> ```
>
> ⏩ <changed implementation>
>
> ```<language>
> <relevant actual changed code>
> ```

---

<result, unresolved decisions, warnings, and accepted trade-offs>

<actual checks, re-review coverage, and evidence limits>

📊 **Reviewed 7 / 42 files, with 10 modifications.**

<state-appropriate choices or remaining authorized work>
````

The progress line shown here belongs to an ordinary main group. Supplementary and repair reports state their own coverage and, when useful, that saved main progress is unchanged; they add no reviewed main files or modifications.

## Explain modifications at the needed depth

Use the compact form for a straightforward change without an actionable issue, worthwhile optional improvement, or material uncertainty: `M1 · <change and purpose>`. Keep the plain ID, middle dot, and natural sentence on one line, without a separate title, bold, blockquote, judgment icons, or code block. A single such change needs only its file heading and that sentence. Compact and detailed items can share a file; both receive complete assessment on both axes.

Use the detailed form for an actionable finding, worthwhile optional improvement, material uncertainty, or consequential mechanism the reader needs to understand. Put the bold ID and bold title on one unindented line, separated by a plain middle dot. Below it, align both judgments and the before/after evidence in one Markdown blockquote, as in the skeleton. Separate items with ordinary paragraph spacing.

Each judgment has its axis icon, verdict, and one sentence explaining the cause and consequence or trade-off. Join the two judgment lines with a Markdown hard break. Add ❌ immediately after the axis icon only for an actual defect, and place severity on the unreasonable line. For a structural defect, explain the user or caller effect on the reasonableness line and the design problem on the elegance line, using one item and one Fix remedy. Name a concrete alternative when it decides the judgment.

Use concise actual before/after snippets that retain the error, state, or lifecycle context needed to understand the change. Keep the ⏪ and ⏩ explanations and code fences inside the same blockquote as the judgments. Inline code can supply evidence for a short change. Label illustrative simplifications. Repair evidence compares pre-repair and repaired contents; it does not substitute the original pinned PR comparison.

After repair or optimization, resolved straightforward changes can become compact. A material design choice, contract change, introduced or newly revealed risk, or requested explanation still needs detail. State the selected items' current judgments in their detailed items, or in one closing sentence for compact items sharing the same judgments. Explain changed reasons and retain unresolved decisions.

## Preserve identities and visible coverage

Show every changed non-test file in a repair report, including supporting files. Tests appear with verification evidence under the repository's classification. Compact presentation does not narrow complete repair or affected-context assessment.

Keep an existing item's ID and explain it once under its responsible file. Separately explained supporting modifications take the next unused M IDs from the entry's continuous sequence; connect them to the original repair in the introduction. For example, a repair after M1–M10 can contain M2, M11, and M12 across three files without changing main progress. References to M2 explain the relationship rather than creating another numbered item. Accompanying changes without a separate item can use a short file overview.

In selected-O work, keep the selected O IDs and use file overviews for supporting changes; they create neither new O observations nor M items. Detailed selected-O items use the same two judgments and evidence layout. Report any resulting finding under the responsible selected item.

Place incidental O items after M items under their source file. A file containing only O items has the same heading with a verified source link and follows the main file blocks. If no single-file attribution is useful, put the observations after the file blocks with a horizontal rule before them and before the closing. Include the entry's required evidence, impact, independence, and recommendation or benefit; any judgment lines follow the same icon and severity conventions. Placement changes neither main progress nor delivery or Viewed eligibility.

## Close with the result and the next decision

Keep these four parts in order and omit empty categories:

1. **Result and decisions.** State the group conclusion or the repair's actual completion status. Name pending unreasonable IDs with severity and impact, retained trade-offs, and outstanding optional remedies and benefits. Give compact repair items their current judgments when those are not already displayed. Summarize material uncertainty separately with ⚠️, the corresponding item IDs, observed risks, and unresolved context. A lack of actionable findings does not establish that every change is elegant or free of uncertainty.
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

Confirm full-path links match the assessed version and every required file is visible. Check stable IDs, one standalone appearance per item, compact items without redundant titles or quotes, and detailed items with aligned judgments and actual evidence. Check O placement, accurate repair status and checks, unchanged main progress for additional coverage, visible uncertainty warnings, and the menu's punctuation, scope, recommendation, and effects.
