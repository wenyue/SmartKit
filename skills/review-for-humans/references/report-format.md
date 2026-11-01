# Report Format

Use this fixed presentation for ordinary, supplementary, dedicated repair, and selected-O reports. The [Skill entry](../SKILL.md) owns inspection standards, required findings and conclusions, M/O identity, grouping, progress, and decisions. This reference owns their presentation; examples illustrate it without defining another format.

## Arrange complete file blocks

Any group introduction precedes the first separator. Repeat the file block from its leading separator for each file, then add one separator before the group closing. Thus every file, including the first, has a separator before it; adjacent files share one boundary.

````markdown
---

📄 **[<full/repository-relative/path>](<returned-url>)**

<responsibility and change overview>

⚖️ **<verdict>** — <reasons and item-keyed findings>

🎨 **<verdict>** — <reasons and item-keyed findings>

**M1 — <change title>**

> ⏪ <sentence describing the earlier implementation>
>
> ```<language>
> <relevant earlier code>
> ```
>
> ⏩ <sentence describing the changed implementation>
>
> ```<language>
> <relevant changed code>
> ```

---

<group conclusion, cumulative main progress, checks and limits, pending decisions>

<separate O observations when present>

<applicable lettered choices when a decision remains>
````

The title is its own paragraph: 📄 followed by the bold returned filename link showing the full repository-relative path, never a basename or shortened path. Put the responsibility/change overview in the next paragraph. The two leading judgments use only their icon and verdict, without dimension or file-level prefixes. Keep the title, overview, judgments, and modification items separate; put no horizontal rule inside a file.

## Present judgments and implementation comparisons

Multiple findings may use separate paragraphs or a short list within the appropriate judgment; do not repeat the verdict for every item. Make consequential design comparisons visible in the existing elegance reasons: name the concrete alternative and the deciding trade-off, at the depth required by the entry. A brief explanation can suffice for localized low-impact changes; use prose suited to the decision rather than a per-declaration checklist or fixed questionnaire.

Repeat the modification portion as needed, using the entry's assigned IDs. A separate selected-O report uses its O IDs in titles and judgments instead of M IDs. Make the whole ID and title bold without a modification icon, adding an unreasonable finding's severity, for example `**M2 — <title> (P1)**`. Keep intrinsic path/code punctuation. The leading judgments own all problems, triggers, impacts, remedies, and benefits; modification bodies show only the implementation before and after, without repeating finding explanations.

Each before/after pair stays in one Markdown blockquote. The ⏪ and ⏩ icons each lead a natural descriptive sentence, with no Before/After labels. Replace the code placeholders with concise actual snippets that preserve the error, state, and lifecycle context needed to understand the change. A simple prose or text change may use inline code in those sentences instead of fenced snippets. Label faithful illustrative simplifications and never present invented snippets as source evidence.

Choose comparison detail by understanding difficulty and consequences, not line count. A straightforward item needs only a compact pair; difficult mechanisms, contracts, lifetimes, risks, or evidence gaps need enough implementation context and supporting evidence to make the cause clear. Keep the corresponding finding's explanation in the judgment block. A one-line change may need full explanation, while a large mechanical edit may be concise.

Keep rare machinery in the internal analysis unless it changes the user's choice.

## Check the report before sending

Before sending, check the first-file, between-file, and closing separators; full-path title on its own; separate overview; two leading judgments; bold item titles; and paired quoted comparisons. Confirm conditional findings, evidence gaps, and decisions are present where needed. Keep the fixed structure and use friendly, direct language within it.
