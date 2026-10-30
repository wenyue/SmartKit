---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，默认跳过 PR 中已查看的文件，本地只审查未暂存改动。
disable-model-invocation: true
---

# Review for Humans

Help the human understand selected changes and judge both their reasonableness and elegance. Establish fixed evidence, inspect connected implementation, and explain complete file groups before carrying out selected actions. Review authorizes evidence capture and link preparation, not changes to reviewed files, the real index, branches, publication, or Viewed state.

Keep ordinary review and conversation here. Read [Workspace](references/workspace.md) before PR or remote-aligned branch workspace preparation or links. Read [Completion](references/completion.md) before preparing/offering completion effects, executing them, or recovering unfinished completion. These guides own their conditional decisions and verification. Missing required guidance leaves dependent work incomplete.

## Choose the useful response

Do authorized, derivable work before asking: inspect accessible facts, prepare links, run checks, and re-review affected content. With clear scope, state it briefly and start; do not ask whether to obtain evidence you can obtain yourself.

When only the user knows a needed fact, ask that fact directly: “Which branch should I compare against?” If a selection lacks IDs, ask “M2, M5, or all?” rather than presenting an information/Cancel/Stop menu. Apply documented defaults before asking; IDs can complete an already clear pending action but do not choose an action by themselves. Clarify only the unresolved part and preserve the group, earlier authorization, and any unfinished completion. Withdrawing that request does not cancel earlier selected work.

Offer a menu only for a real choice about effects or a trade-off. State the concrete situation first. Put the recommended choice at A; each option starts with a short bold action word, then this occasion's effects.

- A. **Pass** (recommended): Mark these four files Viewed, verify them and the PR version, then show the next group.

Put commit/push/Viewed effects in the description, never behind a bare “Pass” or inside an entire bold operation sentence.

Interpret letters case-insensitively against the latest applicable menu. Accept clear natural language and compound requests for disclosed effects. M/O IDs select items, not actions. Questions and disagreements grant no write authority. A ready selected action proceeds without routine reconfirmation. An explicit stop/pause is always allowed and reports residual work honestly.

Report results or a concrete blocker when no actionable choice remains. Say what succeeded, what failed or is unknown, and what remains. Do not invent a waiting/permission menu or imply monitoring. For unfinished completion follow Completion before any further action.

## Fix the comparison and evidence

| Request | Comparison |
| --- | --- |
| PR | Verify owning/source repositories and source branch, prepare the workspace, pin base/head, then apply the authenticated viewer's file-level Viewed filter. |
| Branch | Pin its tip and merge-base with a reliably established comparison base. Resolve an unknown base; do not assume `main`. |
| Local changes or no explicit scope | Compare index to worktree: unstaged changes only. |
| Selected files | Filter the applicable comparison to those paths. |

Explicit PR/branch comparisons exclude local uncommitted changes unless requested. Honor a selected historical version and preserve this scope when other review guidance has different defaults.

For local review, skip staged-only changes and assess only the unstaged part of partially staged files. A worktree reversal of staged content is still an unstaged change. Include untracked files as additions only when explicitly requested. An explicit alternative comparison overrides these defaults.

For a PR, acquire complete file states for the current authenticated viewer, including all pages, while verifying unchanged base/head. Exclude `VIEWED`; include `UNVIEWED` and `DISMISSED`. Approval, comments, earlier chat display, and current states for a historical snapshot do not establish the required filter. A request to include viewed files overrides it.

If complete Viewed filtering remains unavailable after authorized acquisition, first ask directly for any genuinely needed user fact. Otherwise, when fixed comparison evidence is ready, the real choice is A **All** (recommended): review all otherwise eligible files without filtering, or B **Stop**. Never fabricate historical or current Viewed states.

Exclude tests from file reports, modification counts, and progress; use relevant tests as evidence. Apply selected-file, Viewed, and local filters before counting. These filters do not narrow a later full-branch commit or its checks. Order files as GitHub's directory tree: recursively list changed files in subdirectories before direct files, using observed sibling order or otherwise sorting sibling directories and direct files by name. Thus `src/z/api.dart` precedes `src/a.dart`.

Retain pinned commits, fixed before/after content, the ordered file list, and PR viewer/filter evidence. For local review also retain the original index baseline, even if another before version was selected. State scope and exclusions before the first group. An empty comparison ends without a progress fraction or invented files.

Known files with incomplete evidence stay in the total. Name missing evidence for each affected judgment; pause dependent review rather than treating unknown content as clean. Assess defects introduced, triggered, or aggravated by the selected change, including evidence in unchanged code. Keep unrelated pre-existing issues separate as O observations.

### Bind filename links to that evidence

Resolve `local_web` from loaded SmartKit resources and follow its supported interface:

```text
python "<local_web>" --help
python "<local_web>" diff --input "<batch.json>"
```

Use returned Markdown for every reviewed filename link, associated through returned IDs. Capture index-based local links with the snapshot; for PR/branch links supply the fixed before commit, existing blob, or genuine absence, plus rename paths and pinned PR context as required.

For historical PRs, selected fixed comparisons, or unavailable source identity, use `view="snapshot"` with verified fixed evidence. For PR live links use `view="worktree"` and bind `repo` to the exact workspace verified by Workspace, including a verified local alias. Branch-only links use their verified display workspace without PR context. Disclose differing or dirty live contents; they change neither the reviewed version nor Viewed eligibility.

A link failure pauses the dependent report. Preserve comparison and selected mode while resolving it. A generated link does not prove editor display.

## Inspect outcomes and the structure that serves them

Give elegance more review effort than reasonableness. Inspect relevant surrounding implementation, affected callers, and nearby or comparable patterns, rather than only the diff. Use unit/integration evidence to focus behavioral checks while still assessing task outcomes, accepted scope, contracts, and operating costs/risks. Distinguish actual checks from author-reported results and retain material task/standards findings.

For a meaningful design choice, establish required user/caller outcomes from task, contracts, actual use, and lifetime before choosing a structure. An implemented capability is not automatically needed. Compare with a smaller sufficient design: remove an unnecessary capability/layer, call directly, or use an existing owner instead of only rearranging the same functionality. Trace what each layer uniquely owns. Simpler designs still need owners for required feedback, logging, recovery, and lifecycle safeguards; a supported behavior/contract change is a scope decision, not behavior-preserving optimization.

Inspect every scoped added file and declaration, including functions, types, members, and state added to existing files. Tiny files and trivial forwarders add boundaries and cannot use the straightforward-edit exemption. New files require especially strong evidence for an independent responsibility/boundary and why an existing accurate owner or local placement would not serve. Increase scrutiny with actual reach and lifetime: public types/functions/members and top-level state need strong caller/contract justification; private helpers/members get proportionate scrutiny; ordinary local variables need no extra necessity rationale. Visibility keywords alone do not establish exposure.

Caller count, short bodies, uniform presentation, prospective reuse, and testing convenience alone do not justify a boundary. A real responsibility can justify one with one caller. Reasons can be evident in source, tasks, or contracts; require neither rationale comments nor a report item per addition.

### Make two independent judgments

Every modification receives both an explicit conclusion and its reason, including prose and translations.

| Judgment | Evidence and consequence |
| --- | --- |
| ⚖️ **Reasonable** | Required task outcomes, accepted scope, supported behavior/contracts, and justified operating costs/risks. |
| ⚖️ **Unreasonable** (P0–P3) | A material task, behavior, or contract defect, unnecessary scope, or unjustified operating cost/risk. Explain impact and a concrete correction. |
| 🎨 **Elegant** | Responsibilities, boundaries, and exposed interfaces earn their understanding/maintenance cost; expression is readable; abstraction, state, branching, repetition, and defense have concrete benefits. Interfaces and observed comparable patterns are consistent, with justified departures. |
| 🎨 **Needs improvement** | Material avoidable understanding/maintenance burden and a supported simpler or more consistent alternative worth its change cost. Disclose burden, remedy, and benefit; optimization plus re-review or explicit retention acceptance is required. |
| 🎨 **Optional improvement** | Structure already meets the bar, but a supported refinement offers a concrete benefit worth its limited cost. Keep it optional. |
| **Insufficient evidence**, for either dimension | State missing material evidence and how to resolve it. The other judgment can remain supported. |

Structural burden alone is an elegance issue, not a reasonableness defect. Incorrect behavior can have clear, economical structure; a behavioral defect alone does not prove poor structure. Both may fail with corresponding evidence. Missing need/ownership evidence proves neither elegance nor a structural defect. Omit personal preference and low-benefit polish; group remedies for one underlying burden.

Assess extra defensive checks/fallbacks by their structural benefit. Prefer established invariants and boundary guarantees over repeated validation or speculative recovery. Missing extra protection alone is not unreasonable without a credible trigger and potentially serious consequences; ordinary supported behavior and promised failure handling remain correctness obligations.

Assign severity only to unreasonable findings: P0 critical/immediate, P1 serious/prompt correction, P2 normal priority, P3 lower-impact but worth correcting. Use consequences and affected conditions. Required elegance is a substantive gate, not optional styling.

## Explain complete file groups

Give each file a linked filename and brief responsibility/change overview. Group implementation steps by the problem they solve; split independent changes that cannot share one simple explanation. A localization file is one modification. Minor accompanying edits can stay in the overview or be omitted.

Use continuous M IDs across files/groups and retain them for findings, selections, and re-review. A useful label is `🔧 **M1** - **<title>**`. Keep intrinsic path/code punctuation. Separate reasoned paragraphs, commonly ⚖️ and 🎨, distinguish the judgments.

Straightforward behavior with clear scope and no material trade-off usually needs one short before/after paragraph and both judgments. Mechanisms, contracts, findings, or gaps benefit from expanded explanation and the smallest useful actual before/after snippets. Preserve error/state/lifecycle conditions; label illustrative simplifications and keep their behavior faithful. A one-line diff can need deep scrutiny; deeper scrutiny need not produce a longer report.

End a group after the complete file that brings it to at least 10 modifications; never split a file. Show the final shorter group at scope end. Report cumulative displayed files out of eligible files, not implied completion or Viewed. Count each main-review file once.

Retain group membership, next position/M ID, evidence, judgments, findings/decisions, accepted trade-offs, suggestions, and verified effects across replies. Continue unseen files from retained evidence if a full-branch commit cleans the worktree. Change totals only for actual scope changes.

### Keep incidental observations separate

Report an unrelated pre-existing issue only when necessary reading establishes the issue and that this change neither introduced, triggered, nor aggravated it. This is not a broader audit.

Use continuous O IDs. Initially place observations in a separate out-of-scope closing section, with title, source location/link, evidence/impact, independence, and recommendation/benefit. O items add no main files, modifications, progress, or Viewed eligibility. Advice alone does not block progress. Bulk fix/optimize/ignore/accept excludes O items; an O repair needs separate selection, checks, and re-review unless the user explicitly expands main scope.

Close each group with conclusion/progress, actual checks/limits, pending unreasonable IDs/severity/impact, required elegance burdens/remedies/benefits, accepted trade-offs and optional suggestions, plus separate O advice. Explain concrete before/after causes and user/caller consequences: say what operation is skipped, what state is duplicated, or what boundary has no responsibility. A label such as “meets contracts” or “clear structure” is not its own reason. Keep rare machinery in the internal analysis unless it changes the user's choice. Consult [Report Examples](references/report-examples.md) for complete dialogue illustrations, not policy.

## Offer the next real choice

First complete derivable preparation and distinguish what blocks review from what blocks only a proposed write. Missing/stale correctness or version evidence, failed/incomplete required review checks, and unfinished affected re-review block advancement. Missing elegance evidence alone does not. Pending unreasonable findings need repair or explicit ignoring; required elegance needs optimization/re-review or explicit retention acceptance, including earlier groups. O advice alone never blocks.

If a missing user fact blocks progress, ask it directly. If an external condition has no actionable remedy, report the blocker rather than offering an action you cannot perform. Independent supported repairs can still be selected; their explanation must say what will remain blocked.

Use these fixed group choices, with IDs and actual effects filled in:

| Situation | Ordered choices |
| --- | --- |
| Pending unreasonable findings only | A **Fix** (recommended): repair the named findings, check and re-review; B **Keep**: explicitly ignore those findings with severity/impact retained; C **Stop**: end with them unresolved. |
| Pending required elegance only | A **Optimize** (recommended): implement the named remedies, check and re-review; B **Keep**: explicitly accept their disclosed burdens; C **Stop**. |
| Both kinds of necessary issue | A **Address** (recommended): explicitly propose repairing the named unreasonable findings **and** optimizing the named required elegance issues, then checks/re-review; B **Keep**: explicitly propose ignoring the named findings **and** accepting the named structural burdens; C **Stop**. |
| Review and completion ready, with remaining disclosed effects and no separate inclusion decision | A **Pass** (recommended): execute the actual prepared commit/push/Viewed effects and then advance/end; B **Continue**: advance without those writes, or **Finish** at the final group; C **Optimize** only when optional suggestions remain. |
| Review can advance but no completion effects are ready/needed | A **Continue** (recommended), or **Finish** at the final group; B **Optimize** only when optional suggestions remain; finally **Stop** for a non-final group. |
| Final group, no gate, optional suggestion, effect, or decision remains | Report verified completion; no menu. |

Optional advice never displaces the main recommendation or adds options to necessary-issue menus. State that subsets and other valid actions can be requested by IDs in ordinary language; there is no need to print every internal operation. Address executes the mixed remedy explicitly described in the current proposal. It is not an alias that changes the bare Fix default.

Bare **Fix** selects all displayed pending unreasonable M findings; bare **Optimize** selects all displayed outstanding required/optional elegance M improvements, including earlier groups. Neither includes O advice. **Ignore** and **Accept** apply only to selected unreasonable findings or required elegance burdens; with several candidates ask directly which IDs unless all were explicitly chosen. Keep accepted judgments/trade-offs, not an “optimized” label. **Keep** must state which of these decisions it proposes; it edits nothing. Ignore does not accept elegance, and acceptance does not ignore unreasonable findings.

Continue/Finish never stages, commits, pushes, or records Viewed. Pass has only its disclosed effects and grants neither PR approval nor merge authority. A completion-only gap does not block Continue/Finish unless it invalidates review or a selected completion is unfinished. Before offering write effects or extra-content inclusion, use Completion; its conditional choices replace the ordinary ready menu for that decision.

## Repair selected items and re-review

Limit fixes/optimizations to selected items and necessary supporting changes. Optimization preserves supported behavior/contracts.

After any reviewed-content change or selected O repair, run required checks, refresh before/after evidence and links, then independently re-review changed/affected previously reviewed parts, including unexpected changes. Keep pinned remote PR evidence and checked unpublished local content separately. Show complete updated file blocks with both judgments in a dedicated reply apart from unseen files.

For O repair, retain separate evidence and give its own location, before/after explanation, and two judgments. It creates no M ID, main progress, or Viewed eligibility. Preserve original M/O IDs/groups; do not recount files. Mark repair/optimization complete only after checks/re-review confirm it. Retention acceptance remains valid only for the same assessed content/effects.

A single repair, ignore, optimization, or acceptance ends at an updated decision without advancement. A clear compound request authorizes ordered effects, including checks and dedicated re-review before completion/advancement. Continue authorized work when ready; changed effects, new findings, failed checks, or new extra content pause dependent steps without inventing new permission.
