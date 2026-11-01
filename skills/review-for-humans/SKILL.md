---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，默认跳过 PR 中已查看的文件，本地只审查未暂存改动。
disable-model-invocation: true
---

# Review for Humans

Help the human understand fixed changes, judge their reasonableness and elegance, and choose what happens next. Explain complete file groups before acting on their choices. Review authorizes evidence capture and link preparation; edits, workspace changes, delivery, and advancement follow the selected action.

This entry owns the complete review loop: establish context, inspect and judge, explain complete groups, then act on the user's choice and resume. Read [Preparation](references/preparation.md) for PR or remote-aligned branch evidence and workspace choices; ordinary local review uses the comparison and link rules below. Read [Delivery](references/delivery.md) before preparing or offering delivery, executing it, or recovering its effects. These are the two conditional guides; unavailable required guidance leaves dependent work incomplete.

## Establish the review context

| Request | Comparison |
| --- | --- |
| PR | Verify owning/source repositories and source branch, prepare the workspace, pin base/head, then apply the authenticated viewer's file-level Viewed filter. |
| Branch | Pin its tip and merge-base with a reliably established comparison base. Resolve an unknown base; do not assume `main`. |
| Local changes or no explicit scope | Compare index to worktree: unstaged changes only. |
| Selected files | Filter the applicable comparison to those paths. |

Explicit PR/branch comparisons exclude local uncommitted changes unless requested. Honor a selected historical version and preserve this scope when other review guidance has different defaults.

For local review, skip staged-only changes and assess only the unstaged part of partially staged files. A worktree reversal of staged content is still an unstaged change. Include untracked files as additions only when explicitly requested. An explicit alternative comparison overrides these defaults.

Exclude tests from ordinary main-review reports, modification counts, and progress; use relevant tests as evidence. Apply selected-file, Viewed, and local filters before counting. Delivery inventories and checks the complete contents, while its supplementary review excludes test files under the same classification and covers otherwise excluded non-test changes as defined by Delivery. Review filters never narrow what is committed or checked. Order files as GitHub's directory tree: recursively list changed files in subdirectories before direct files, using observed sibling order or otherwise sorting sibling directories and direct files by name. Thus `src/z/api.dart` precedes `src/a.dart`.

Retain pinned commits, fixed before/after content, the ordered file list, and PR viewer/filter evidence. For local review also retain the original index baseline, even if another before version was selected. State scope and exclusions before the first group. An empty comparison ends without a progress fraction or invented files.

Known files with incomplete evidence stay in the total. Name missing evidence for each affected judgment; pause dependent review rather than treating unknown content as clean. Assess defects introduced, triggered, or aggravated by the selected change, including evidence in unchanged code. Keep unrelated pre-existing issues separate as O observations.

### Bind filename links to that evidence

Resolve `local_web` from loaded SmartKit resources and follow its supported interface:

```text
python "<local_web>" --help
python "<local_web>" diff --input "<batch.json>"
```

For each reviewed file, supply its full repository-relative `path` with forward slashes and omit `title`, which defaults to that path. Use the returned Markdown unchanged for its filename link, associated through the returned ID; preserve its escaping and URL binding rather than shortening the label. Capture index-based local links with the snapshot. For a fixed comparison supply the verified before commit, existing blob, or genuine absence, plus rename paths. Preparation supplies PR context and verified display mode when applicable; ordinary local review needs neither PR metadata nor remote alignment.

Bind live links to the exact verified display workspace. Branch-only links use that workspace without PR context, including deliberately local branch review; verifying this binding does not require remote alignment. Disclose differing or dirty live contents; they change neither the reviewed version nor Viewed eligibility.

A link failure pauses the dependent report. Preserve comparison and selected mode while resolving it. A generated link does not prove editor display.

## Inspect outcomes and the structure that serves them

Give elegance more review effort than reasonableness. Inspect relevant surrounding implementation, affected callers, and nearby or comparable patterns, rather than only the diff. Use unit/integration evidence to focus behavioral checks while still assessing task outcomes, accepted scope, contracts, and operating costs/risks. Distinguish actual checks from author-reported results and retain material task/standards findings.

For a meaningful design choice, establish required user/caller outcomes from task, contracts, actual use, and lifetime before choosing a structure. An implemented capability is not automatically needed. Compare with a smaller sufficient design: preserve an existing interface or responsibility boundary, remove an unnecessary capability/layer, call directly, or use an existing owner instead of only rearranging the same functionality. Trace what each layer uniquely owns. Judge the benefit of the chosen structure separately from the behavior it enables or the tests it passes. Simpler designs still need owners for required feedback, logging, recovery, and lifecycle safeguards; a supported behavior/contract change is a scope decision, not behavior-preserving optimization.

Inspect every scoped added file and added or changed declaration or contract, including functions, types, members, and state in existing files. Tiny files and trivial forwarders add boundaries and cannot use the straightforward-edit exemption. New files require especially strong evidence for an independent responsibility/boundary and why an existing accurate owner or local placement would not serve. Increase scrutiny with actual exposure, caller dependence, lifetime, and change impact: interfaces exposed beyond their local owner, widely depended-on declarations, and shared or long-lived state need strong caller/contract evidence and concrete design comparisons; local helpers and members get proportionate scrutiny according to those same factors; ordinary local variables need no extra necessity rationale. Visibility keywords alone do not establish exposure.

Caller count, short bodies, uniform presentation, prospective reuse, and testing convenience alone do not justify a boundary. A real responsibility can justify one with one caller. Reasons can be evident in source, tasks, or contracts; require neither rationale comments nor a report item per addition.

### Assess every change and report two file-level judgments

Rigor follows the actual in-scope non-test changes, not the displayed M list. Assess every such change on both axes, including prose and translations, and inspect the file as a whole and necessary connected implementation to establish its effects. Grouping or omitting an explanatory item never removes its changes from review.

Give each file two independent, reasoned judgments using the verdicts below. Link reasons and findings to relevant M IDs: a good change cannot average away another change's defect or structural burden. Preserve explicit retained findings and material evidence gaps instead of turning them into a clean verdict.

Explain concrete before/after causes and user/caller consequences: say what operation is skipped, what state is duplicated, or what boundary has no responsibility. A label such as “meets contracts” or “clear structure” is not its own reason.

| Judgment | Evidence and consequence |
| --- | --- |
| ⚖️ **Reasonable** | Required task outcomes, accepted scope, supported behavior/contracts, and justified operating costs/risks. |
| ⚖️ **Unreasonable** | A material task, behavior, or contract defect, unnecessary scope, or unjustified operating cost/risk. Identify the findings and their severity, impact, and concrete correction. |
| 🎨 **Elegant** | Responsibilities, boundaries, and exposed interfaces earn their understanding/maintenance cost; expression is readable; abstraction, state, branching, repetition, and defense have concrete benefits. Interfaces and observed comparable patterns are consistent, with justified departures. |
| 🎨 **Needs improvement** | Material avoidable understanding/maintenance burden and a supported simpler or more consistent alternative worth its change cost. Disclose burden, remedy, and benefit; optimization plus re-review or explicit retention acceptance is required. |
| 🎨 **Optional improvement** | Structure already meets the bar, but a supported refinement offers a concrete benefit worth its limited cost. Keep it optional. |
| **Insufficient evidence**, for either dimension | State missing material evidence and how to resolve it. The other judgment can remain supported. |

Structural burden alone is an elegance issue, not a reasonableness defect. Incorrect behavior can have clear, economical structure; a behavioral defect alone does not prove poor structure. Both may fail with corresponding evidence. Missing need/ownership evidence proves neither elegance nor a structural defect. Omit personal preference and low-benefit polish; group remedies for one underlying burden.

Assess extra defensive checks/fallbacks by their structural benefit. Prefer established invariants and boundary guarantees over repeated validation or speculative recovery. Missing extra protection alone is not unreasonable without a credible trigger and potentially serious consequences; ordinary supported behavior and promised failure handling remain correctness obligations.

Assign severity only to unreasonable findings: P0 critical/immediate, P1 serious/prompt correction, P2 normal priority, P3 lower-impact but worth correcting. Use consequences and affected conditions. Required elegance is a substantive gate, not optional styling.

## Explain complete file groups

Before preparing an ordinary, supplementary, dedicated repair, or selected-O report, read [Report Format](references/report-format.md) in full and use its fixed structure. If the complete required format is unavailable, pause the dependent report. The review and disclosure obligations below still apply regardless of presentation detail.

Use continuous M IDs across files/groups and retain them for findings, selections, and re-review. Group implementation steps by the problem they solve; split independent changes that cannot share one simple explanation. A localization file is one modification. Minor accompanying edits without findings may stay in the overview or be omitted from the explanation, but are still reviewed.

Disclose every supported unreasonable finding and worthwhile required or optional improvement, even when its actual change was initially grouped or omitted. Give it explicit coverage through an existing M item or add an M item. Identify the problem, unreasonable severity or required/optional elegance status, relevant trigger, impact, and correction or benefit. A generic file verdict cannot substitute for an actionable finding. A defect in unchanged code introduced, triggered, or aggravated by the selected change is a main finding associated with the responsible M item; unrelated pre-existing issues found during necessary reading follow the O rules below. This is not an audit of unrelated file history or the repository.

End a group after the complete file that brings it to at least 10 modifications; never split a file. Show the final shorter group at scope end. Report cumulative displayed files out of eligible files, not implied completion or Viewed. Count each main-review file once.

Retain group membership, next position/M ID, evidence, judgments, findings/decisions, accepted trade-offs, suggestions, and verified effects across replies. Continue unseen files from retained evidence if a full-branch commit cleans the worktree. Change totals only for actual scope changes.

Close each group with conclusion/progress, actual checks/limits, pending unreasonable IDs/severity/impact, required elegance burdens/remedies/benefits, accepted trade-offs and optional suggestions, plus the separate O advice described below. Consult [Conversation Examples](examples/conversations.md) for concise decision and transition illustrations, not the format or policy.

### Keep incidental observations separate

Report an unrelated pre-existing issue only when necessary reading establishes the issue and that this change neither introduced, triggered, nor aggravated it. This is not a broader audit.

Use continuous O IDs. Initially report observations separately from main findings, with title, source location/link, evidence/impact, independence, and recommendation/benefit. O items add no main files, modifications, progress, or automatic Viewed eligibility. Unselected advice alone does not block progress or delivery. Once an O remedy is selected, its changes join delivery coverage and checks; failures or new unresolved findings in that work can block delivery. Bulk fix/optimize/ignore/accept excludes O items; an O repair needs separate selection, checks, and re-review unless the user explicitly expands main scope.

For an O repair, retain separate evidence and report two judgments for the selected O change and affected context, keyed by its O ID. Keep its findings and conclusions distinct from the main file review. It creates no main M ID or progress. Any Viewed eligibility still needs Delivery's whole-file coverage.

## Resolve the choice, act, and resume

These actions apply to PR, branch, and local review. Their availability depends on the evidence and selected workspace; a review of a snapshot does not itself provide an editable or deliverable checkout.

| Action | Meaning and completion |
| --- | --- |
| **Fix** | Repair the selected unreasonable findings, run required checks, and re-review affected content. |
| **Optimize** | Implement the selected required or optional elegance improvements, run required checks, and re-review affected content. |
| **Fix and optimize** | Explicitly combine both remedies, naming each set of findings; it does not change the meaning of bare Fix. |
| **Ignore** | Record the explicitly selected ignored defects, accepted structural burdens, or declined optional improvements without editing. Preserve their judgments and disclosed consequences. |
| **Pass** | Complete delivery, then advance to the next group or finish at scope end. |
| **Continue** / **Finish** | Advance to the next group, or end a fully displayed review, without delivery. |

Delivery names the applicable commit, publication, and Viewed effects in the delivery guide, not a separate routine menu option. Accept “only deliver”: complete those effects and stay at the current group. Pass includes advancement; do not ask again after its delivery succeeds. Neither action grants PR approval or merge authority.

An unambiguous current menu option supplies its disclosed scope to a natural-language action reply too: Optimize can select an option explicitly naming O1. With several Optimize alternatives, ask which IDs. Without a clear menu scope, bare Fix selects all displayed pending unreasonable M findings, and bare Optimize selects all displayed outstanding required and optional elegance M improvements, including earlier groups; these defaults exclude unrelated O observations. Ignore must name the defects, burdens, or optional improvements it proposes to leave unchanged and their consequences. Accept clear natural-language acceptance or decline too; if the intended items or kind of decision remain ambiguous, ask which IDs and decision. Ignoring does not waive required checks, erase judgments, or authorize advancement by itself. IDs alone select items, not an action. A retained item is no longer outstanding while its assessed content and effects remain unchanged.

Interpret letters case-insensitively against the latest applicable menu. Accept clear natural language, subsets, and compound requests for disclosed effects. A ready selected action proceeds without routine reconfirmation. A recommendation or sole available option does not select an action or broaden its authority. Menus omit Stop and Cancel choices. Questions and disagreements grant no write authority; an explicit change, pause, or stop takes precedence over a pending request. When the user pauses or stops, report completed and residual work; unresolved work remains incomplete.

### Resolve the current request before a new choice

First honor an existing request. Retain Pass versus only-deliver, any explicit compound request, selected workspace and disclosed effects, accepted trade-offs, group progress, and next position alongside Delivery's effect evidence. A pending request survives supplementary review, selected repairs, and interrupted writes. New unreasonable issues or required or optional improvements in required delivery coverage, including selected O work, suspend delivery; report them and use the remedy/Ignore choices below. A prior Pass neither accepts later discoveries nor authorizes their repair. Do not substitute Continue/Finish or ask for Pass again. Once findings are resolved or explicitly retained and all prerequisites hold, resume the original delivery and its original advancement choice.

Otherwise, complete authorized, derivable work before asking: inspect facts, prepare links, run checks, and re-review affected content. Ask directly for a genuinely user-owned missing fact, such as the comparison branch or an ambiguous item selection. A fact question is not an action menu. Report a verified external blocker when no supported remedy is selectable; do not invent Wait/Resolve choices or promise monitoring.

### Establish which choices are available

Missing or stale correctness/version evidence, failed or incomplete required review checks, and unfinished affected re-review block advancement. Missing elegance evidence alone does not. Pending unreasonable findings need repair or explicit ignoring; required elegance needs optimization or explicit retention, including earlier groups. Optional improvements remain optional, and unrelated O advice never blocks main review.

A delivery-only limitation does not block ordinary Continue/Finish when the review remains valid and no delivery is pending. Before offering Pass, complete Delivery's derivable preparation and disclose its actual remaining effects. Unknown or uninspected is not unavailable. When no delivery effect remains, offer advancement directly rather than an empty Pass.

### Recommend improvement before delivery

Use the first applicable row. Fill in IDs, consequences, and concrete effects; include every available choice in its listed order, then label consecutively with the recommendation at A.

| Current decision | Ordered choices |
| --- | --- |
| Pending delivery has unresolved findings | **Fix and optimize** when both kinds remain, otherwise **Fix** or **Optimize**; **Ignore** the named findings/burdens. Resume delivery after all findings are resolved or explicitly retained. |
| No pending delivery; unreasonable findings and any outstanding elegance improvements | **Fix and optimize**; **Ignore** the named defects and improvements. |
| No pending delivery; unreasonable findings only | **Fix**; **Ignore** the named defects. |
| No pending delivery; required elegance remains | **Optimize**, including outstanding optional improvements; **Ignore** the named burdens/improvements. |
| Only optional improvements remain | **Optimize**; **Pass** when available, explicitly retaining the named optional items; **Continue** or **Finish**. |
| No outstanding findings or improvements; delivery has remaining effects | **Pass** when available; **Continue** or **Finish**. |
| Final group with no finding, supported M/O improvement, effect, or decision remaining | Report verified completion without a menu. |
| Review can advance, but no delivery effect is needed or delivery is unavailable | **Continue**, or **Finish** at scope end. |

When an outstanding O observation has a supported optimization, include an explicit **Optimize O…** choice whenever constructing a genuine menu. If no necessary main issue or pending delivery takes precedence, recommend the supported optimization ahead of Pass/Continue, combining M and O remedies only with their IDs and effects explicitly named. With necessary main issues or findings suspending delivery, keep their remedy recommended and show O optimization as an additional choice after the main remedy and Ignore, stating what it leaves unresolved. O advice alone creates no advancement or delivery gate. For an already authorized ready delivery, disclose the O opportunity without manufacturing another menu or delaying the request.

A row never makes an unavailable action executable. If its recommended remedy needs an unresolved user fact, ask that fact; independently supported remedies can still be chosen with the remaining blocker stated. A subset may be requested in ordinary language without printing every possible combination. Explicit retention in a Pass description applies only to the named assessed items, never to later discoveries. Continue may defer optional advice; it does not mean that the user declined it.

Each menu option starts with a short bold action label followed by this occasion's effects. Describe fixes and optimizations by their IDs and result; describe Pass by the actual commit/push/Viewed effects and following advancement. Recommending an action never justifies omitting an applicable alternative. Preparation owns workspace actions and their recommendation criteria; it does not replace these review priorities.

### Execute the selected action

Limit fixes and optimizations to the selected items and necessary supporting changes. Optimization preserves supported behavior and contracts.

After any reviewed-content change or selected O repair, run required checks, refresh before/after evidence and links, then independently re-review changed and affected previously reviewed parts, including unexpected changes. Keep pinned remote PR evidence separate from checked unpublished local content. Show complete updated file blocks in a dedicated reply apart from unseen main-review files, using the inspection standards above and required Report Format; selected-O reports retain their separate IDs and conclusions. Preserve existing IDs and groups and do not recount files. Mark a repair or optimization complete only after checks and re-review confirm it; explicit retention remains a recorded trade-off, not an optimization.

Without a pending delivery or explicit compound request, a single Fix, Optimize, or Ignore ends at the updated decision. With one, complete the required dedicated re-review and resume the remaining authorized effects without another permission round. An explicit instruction such as “only optimize, do not deliver yet” changes that intent. New findings, changed delivery effects, or failed checks pause dependent work; changed effects outside existing authority need a concrete decision before execution, while successful effects remain recorded.

Use Delivery to execute or reconcile physical effects. Only after every applicable effect and required readback succeeds does Pass resume the saved next group or finish; only-deliver stays at the current group. Preserve main progress and undisplayed fixed evidence even when committing cleans the worktree. If delivery remains incomplete, retain its pending intent and report confirmed, unknown, and remaining effects. Follow the fact/blocker rules above rather than inventing a waiting menu, monitoring promise, or polling loop.
