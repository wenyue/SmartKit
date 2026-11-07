# Report Format

The [Skill entry](../SKILL.md) owns inspection, findings, M/O identity, grouping, progress, action labels, and decisions. This reference owns the common report layout, explanation depth, and menu rendering. Ordinary, supplementary, repair, and selected-O reports use the same file blocks and closing order.

## Use one report skeleton

Give the scope needed to understand this report, the file blocks, and the closing. An ordinary introduction identifies the group; a supplementary introduction identifies the additional delivery coverage; a repair introduction names the selected original M/O items and connects their supporting changes. Keep repair and supplementary coverage separate from unseen main groups.

Use a single horizontal rule before the first file, between file blocks, and before the closing. Each file heading is 📄 followed by the bold, full repository-relative filename link returned by `local_web`, unchanged. A short file overview is optional. Use the filename as the diff link; add other links only for distinct evidence the reader needs.

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

<result, unresolved findings or decisions, and accepted trade-offs>

<checks, re-review coverage when applicable, and evidence limits>

📊 **Reviewed 7 / 42 files, with 10 modifications.**

<state-appropriate choices, when a decision remains>
````

The progress line above belongs to an ordinary main group. Supplementary and repair closings state their own coverage and, when useful, that the saved main progress is unchanged; they do not add reviewed main files or modifications.

## Keep files and item identities clear

Show each changed non-test file in a repair report, including supporting files. Test changes appear with verification evidence under the repository's classification, rather than as semantic review items. The entry's complete repair and affected-context assessment still applies to compact explanations.

Use the entry's continuous M sequence. Keep the original ID for an existing item, place that item once under the file that owns its explanation, and use the next unused M IDs for additional separately explained modifications. State their relationship to the repaired finding in the introduction. For example, after M1–M10 have been assigned, a repair of M2 can contain M2, M11, and M12 in three files; all three belong to the repair, and main progress stays unchanged. References to M2 explain correspondence rather than introducing another M2 item.

Accompanying changes without a separate item may use a short file overview. In selected-O work, keep the selected O IDs and describe supporting-file changes in their file overviews; supporting edits do not create new incidental observations or M items. Retain both judgments and disclose any resulting finding under the responsible selected item.

Place incidental O items after M items under their source file. A file containing only O items uses the same heading with a verified source link and follows the main file blocks. Put O items without useful single-file attribution in a separate observations section after the files, with a horizontal rule before it and before the closing. Their placement changes neither main progress nor delivery or Viewed eligibility.

## Choose compact or detailed items

Use the compact form for a straightforward change without an actionable issue, worthwhile optional improvement, or material evidence gap. Put the plain ID, a middle dot, and one natural sentence on the same line: `M1 · <change and purpose>`. Omit a separate title, bold, blockquote, judgment icons, and code block. A file with one such item contains just its heading and that sentence; the same compact form can appear beside detailed items in a mixed file. Both axes still receive full assessment.

Use the detailed form for an actionable finding, worthwhile optional improvement, material evidence gap, or consequential mechanism the reader needs to understand. Put the bold ID and bold title on one unindented line, separated by a plain middle dot. Below it, keep both judgment lines and the before/after evidence in one aligned Markdown blockquote. Separate items with ordinary paragraph spacing.

Give each axis its icon, verdict, and one sentence explaining the cause and consequence or trade-off. Join the two judgment lines with a Markdown hard break. Add ❌ immediately after the axis icon only for an actual defect, and put severity on the unreasonable line. For a structural defect, the reasonableness line explains the user or caller effect and the elegance line explains the design problem, using one item and one Fix remedy. Name a concrete alternative when it decides the judgment.

Use concise actual before/after snippets that preserve the error, state, or lifecycle context needed to understand the change. Align the ⏪ and ⏩ sentences and their code fences with the judgments inside the same blockquote. Inline code may serve as evidence for a short change. Label illustrative simplifications. Repair evidence compares the pre-repair and repaired contents; it does not silently substitute the original pinned PR comparison.

Apply the same depth choice after a repair or optimization: resolved straightforward changes can be compact; a material design choice, contract change, introduced or newly revealed risk, or requested explanation needs detail. State the selected items' current reasonableness and elegance judgments in their detailed items or in one closing sentence for compact items with the same judgments. Explain changed reasons and retain unresolved decisions.

Detailed selected-O items use the same presentation with O IDs. Incidental observations include the entry's source evidence, impact, independence, and recommendation or benefit; any judgment lines follow the same icon and severity conventions.

## Close in a fixed order

Keep the closing short, in this order:

1. **Result and decisions.** State the group conclusion or the repair's actual completion status. Name pending unreasonable IDs with severity and impact, retained trade-offs, and outstanding optional remedies and benefits. Give compact repair items their current judgments here when those are not already displayed. Omit empty categories.
2. **Evidence and limits.** State the checks actually performed, results, and material gaps. For a repair, identify coverage of all changed non-test files and affected previously reviewed context, with verification records and available logs. Distinguish successful code changes from unavailable required checks or incomplete re-review; those limits keep the dependent remedy incomplete. Tests are evidence, and author-reported checks remain distinguishable from executed checks.
3. **Progress or coverage.** For a main group, show only the cumulative reviewed-file fraction and actual main-modification count in the report language, as in the skeleton. For supplementary, repair, or selected-O work, state that coverage separately; preserve the saved main total and position.
4. **Choices or remaining authorized work.** Render the applicable menu from the entry, with concrete IDs, effects, and next position. If delivery is already selected, preserve that pending intent and use its decision table; when no new decision remains, state and continue the authorized next work instead of asking for Pass again. For an unavailable prerequisite without a selectable remedy, explain the actual limitation.

## Render the selected choices

Selection, labels, recommendation, ordering, and scope come from the entry and its stage tables. Render the choices as a Markdown unordered list with one option per list item, consecutive uppercase letters, and no blank lines between items. Begin each item with `- `, then the letter, short bold action label, optional recommendation outside the bold span, colon, and concrete effects. Bold only the action label.

Use these literal punctuation and spacing patterns; the descriptions below are illustrative, not a choice of actions for the current state:

```markdown
- A. **Pass** (recommended): Prepare and complete applicable delivery, then review the next group.
- B. **Continue**: Review the next group without delivery.
```

For Chinese, use full-width `．` and `：`, spaces on both sides of the bold label, and `（推荐）` outside it. Pass renders as `通过`, Continue as `继续`, and Finish as `结束`; other action labels retain their corresponding meanings.

```markdown
- A． **通过** （推荐）：准备并完成适用的交付，然后审阅下一组。
- B． **继续** ：从下一组开始只读审阅。
```

Use the same rendering for workspace menus. At scope end use Finish rather than Continue, following the entry's action semantics.

## Check the report before sending

Confirm full-path links match the assessed version, and every required file is covered. Check that item IDs are stable and appear as standalone items only once, compact items contain no redundant title or quote, and detailed items align both judgments and actual before/after evidence. Confirm O placement, accurate repair status and checks, unchanged main progress for additional coverage, and the exact menu punctuation, scope, recommendation, and effects.
