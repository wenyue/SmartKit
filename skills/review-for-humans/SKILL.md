---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，判断合理性与优雅性，协助用户选择后续行动。
disable-model-invocation: true
---

# Review for Humans

Make fixed changes understandable enough for the human to judge them and choose what happens next. Establish why the behavior is needed before judging how it is implemented. Review authorizes evidence capture and link preparation. Explain complete file groups before acting on selected review remedies, delivery, or advancement.

This entry owns review scope, assessment, findings, progress, and user decisions. Load [Preparation](references/preparation.md) for PR or remote-aligned branch evidence and workspace selection. Read [Report Format](references/report-format.md) in full before every ordinary, supplementary, repair, or selected-O report. Load [Delivery](references/delivery.md) for an explicit delivery request or pending delivery, or to determine whole-file Viewed eligibility when a repair touches a PR file not yet fully reviewed. An unavailable required guide leaves dependent work incomplete. [Conversation Examples](examples/conversations.md) illustrate difficult choices without adding policy.

## Fix the comparison and reading order

| Request | Comparison and initial evidence |
| --- | --- |
| PR | Preparation verifies source identity and workspace, pins base/head, and obtains the authenticated viewer's complete file-level Viewed filter. |
| Branch | Pin the tip and merge-base with a reliably established comparison base. Ask for an unknown base instead of assuming `main`. |
| Local changes or no stated scope | Compare index to worktree: unstaged changes only. |
| Selected files | Restrict the applicable comparison to those paths. |

Honor explicit alternative comparisons and historical versions. PR and branch comparisons exclude local uncommitted changes unless requested. For local review, exclude staged-only files, assess only the unstaged part of partially staged files, and recognize a worktree reversal of staged content as an unstaged change. Include untracked additions only when explicitly requested. These defaults prevail over different defaults in other review guidance.

Apply selected-file, Viewed, and local filters before counting. Exclude tests from ordinary reports, modification counts, and progress; use relevant tests as evidence. The delivery guide separately accounts for the complete submitted and outgoing scope. Report filters never narrow a commit or its required checks.

Order files like GitHub's directory tree: recursively list changed files in subdirectories before direct files, preserving observed sibling order or otherwise sorting sibling directories and direct files by name. Thus `src/z/api.dart` precedes `src/a.dart`. Retain the ordered eligible list, pinned commits, complete before/after content, and PR viewer/filter evidence. For local review retain the original index baseline even when another before version is selected.

State the comparison and exclusions before the first group. Empty scope ends without a progress fraction. Known files with incomplete evidence remain in the total; identify what is missing and pause the affected assessment instead of treating unseen content as clean.

### Provide links to the assessed version

Resolve `local_web` from loaded SmartKit resources and read its supported interface:

```text
python "<local_web>" --help
python "<local_web>" diff --input "<batch.json>"
```

Supply each file's full repository-relative `path` with forward slashes and omit `title`. Associate the returned Markdown by ID and use it unchanged as the filename link, preserving its full label, escaping, and URL binding. Capture index-based local links with the snapshot. Fixed comparisons supply the verified before commit, existing blob, or genuine absence and rename paths.

Preparation supplies PR metadata and verified display mode. Local and deliberately local branch reviews need no remote alignment; branch-only links bind to the exact verified display workspace without PR context. Bind every live link to its verified workspace and disclose dirty or differing live contents without changing the assessment or Viewed eligibility. A generated link does not prove editor display. If link generation fails, preserve the comparison and chosen mode while resolving it; the dependent report waits.

## Judge the need, then the implementation

Inspect the whole scoped change and its necessary context: affected callers, existing owners, comparable patterns, contracts, and lifetimes. Give elegance more effort than reasonableness. Review every non-test change on both axes, including documentation and translations, whether or not it gets a displayed modification item. Distinguish checks actually performed from author-reported results and retain material task or standards findings.

For a meaningful design choice, establish the required user or caller outcome from the task, supported contracts, and actual use. Verify existing behavior and framework or library guarantees. First consider retaining that behavior or removing the added capability; only then compare mechanisms for a capability that is needed. A passing test demonstrates behavior under its assumptions, not the necessity of the policy it exercises.

Judge validation, recovery, and other protection by the requirement, credible trigger, and consequential impact they address. Supported requirements and trust-boundary risks can justify protection before any production incident; established invariants can make repeated checks unnecessary. Missing extra protection is not itself a defect without a credible trigger and potentially serious consequence, while ordinary supported behavior and promised failure handling remain correctness obligations. If material evidence for the need is missing, use **Insufficient evidence** for the affected judgment rather than approving the implementation or presuming the capability is a defect.

For supported behavior, compare the chosen design with a smaller sufficient alternative: keep an existing interface, use an accurate existing owner, call directly, or remove a layer with no unique responsibility. Required feedback, logging, recovery, and lifecycle protection still need owners. A proposal to change supported behavior or contracts is a scope decision, not behavior-preserving optimization.

Scrutinize every added file and added or changed declaration or contract, including functions, types, members, and state in existing files. A tiny file or trivial forwarder still introduces a boundary. New files need especially strong evidence for a distinct responsibility and why an existing owner or local placement would not suffice. Scale further scrutiny by actual exposure, caller dependence, lifetime, and change impact: shared interfaces and long-lived state need stronger evidence and concrete alternatives than local helpers. Ordinary local variables need no separate necessity rationale; visibility keywords do not establish actual exposure.

Short bodies, caller counts, uniform presentation, speculative reuse, and testing convenience alone justify no boundary. A real responsibility can justify one with a single caller. Source, tasks, and contracts can supply the reason without rationale comments or one report item per declaration.

### Give two independent judgments per file

| Judgment | Basis |
| --- | --- |
| ⚖️ **Reasonable** | Required outcomes, accepted scope, supported behavior/contracts, and justified operating costs and risks. |
| ⚖️ **Unreasonable** | A material task, behavior, or contract defect, unnecessary scope, or unjustified operating cost or risk. Identify severity, affected conditions, impact, and correction. |
| 🎨 **Elegant** | Responsibilities, boundaries, and interfaces earn their understanding and maintenance cost. Expression is readable; abstraction, state, branching, repetition, and defense have concrete benefits. Comparable patterns and interfaces are consistent, with justified departures. |
| 🎨 **Needs improvement** | A material avoidable burden has a supported simpler or more consistent alternative worth its change cost. Explain the burden, remedy, and benefit; optimization or explicit retention is required. |
| 🎨 **Optional improvement** | The structure meets the bar, but a supported refinement offers enough benefit for its limited cost. It remains optional. |
| **Insufficient evidence** on either axis | Name the missing material evidence and how to obtain it. Keep any supported judgment on the other axis. |

Explain concrete causes and user or caller consequences, not labels such as “meets contracts” or “clear structure.” Tie findings to modification IDs. One good change cannot cancel another change's defect, burden, or evidence gap; explicit retention preserves the judgment and consequences.

Keep the axes independent. A structural burden alone is an elegance issue; a behavioral defect alone does not prove poor structure. Missing need or ownership evidence establishes neither elegance nor a structural defect. Omit preference and low-benefit polish, and combine remedies for the same underlying burden.

Assign severity only to unreasonable findings: P0 critical/immediate, P1 serious/prompt correction, P2 normal priority, P3 lower-impact but worth correcting. Required elegance is a substantive gate, not optional styling.

## Explain complete groups and preserve their identity

Use Report Format for the applicable report kind. Assign continuous M IDs across files and groups, grouping implementation steps by the problem they solve and separating independent changes that cannot share one explanation. One localization file is one modification. Minor accompanying edits without findings may stay in the overview or be omitted from explanation; they remain within assessment coverage.

Every supported unreasonable finding and worthwhile required or optional improvement needs an actionable M item, using an existing item or adding one. Its leading judgment explains the problem, unreasonable severity or elegance status, trigger, impact, correction or benefit. A generic verdict cannot replace the finding. Defects in unchanged code belong here when this change introduces, triggers, or aggravates them; associate each with the responsible M item.

End a group after the complete file that brings it to at least 10 modifications, never midway through a file. Show the shorter remainder at scope end. Progress counts cumulative displayed main files out of eligible files, each once; it implies neither successful delivery nor Viewed recording.

Close the group with its conclusion and progress, actual checks and limits, pending unreasonable IDs with severity and impact, required elegance burdens with remedies and benefits, accepted trade-offs, and optional suggestions. Retain evidence, judgments, findings and decisions, group membership, next position, and next M ID across replies. Change totals only when scope changes; a commit that cleans the worktree does not erase undisplayed fixed evidence.

### Separate incidental observations

Necessary reading may reveal an unrelated pre-existing issue. Establish both its evidence and that the selected change neither introduced, triggered, nor aggravated it; this is not an audit of unrelated history or the repository.

Report it separately with a continuous O ID, title, source link/location, evidence and impact, independence, and recommendation or benefit. It adds no main file, modification, progress, or automatic Viewed eligibility. Unselected O advice creates no main-review or delivery gate.

Bulk Fix, Optimize, Ignore, and acceptance exclude O items unless the user explicitly expands scope or selects them. A selected O repair receives separate evidence, checks, and re-review of its change and affected context, using O IDs and two judgments without new main M IDs or progress. Its changes enter delivery coverage; resulting failures or unresolved findings can block delivery. Delivery determines any whole-file Viewed eligibility.

## Turn the findings into a real choice

### Interpret actions and their authority

| Action | Selected effect |
| --- | --- |
| **Fix** | Repair unreasonable findings, check, and re-review. |
| **Optimize** | Implement required or optional elegance improvements, preserving supported behavior and contracts, then check and re-review. |
| **Fix and optimize** | Combine both explicitly named remedy sets. Bare Fix keeps its narrower meaning. |
| **Ignore** | Leave explicitly selected defects, burdens, or optional improvements unchanged, recording their consequences and the user's acceptance or decline. |
| **Pass** | Complete applicable delivery effects, then advance or finish at scope end. |
| **Continue** / **Finish** | Advance or end the fully displayed review without delivery. |

Delivery determines the applicable commit, publication, and Viewed effects. Accept “only deliver” as the same delivery without advancement; it is not a separate routine menu option. Neither delivery action grants PR approval or merge authority.

Interpret letters case-insensitively against the latest applicable menu. Clear natural language, subsets, and compound requests can select disclosed effects. An unambiguous menu option supplies its stated scope: “Optimize” can select an option explicitly naming O1. With several matching alternatives, ask which IDs. Without a clear menu scope, bare Fix selects all displayed pending unreasonable M findings, and bare Optimize selects all displayed outstanding required and optional elegance M improvements, including earlier groups.

Ignore must identify the items and consequences to be retained or declined; clear natural-language acceptance or decline suffices. Ask when either the items or decision is ambiguous. IDs alone identify items, not an action. Retained items cease to be outstanding while their assessed content and effects stay unchanged. Ignoring neither waives checks nor advances the review.

A ready selected action proceeds without routine reconfirmation. Recommendations, sole options, questions, and disagreement grant no additional authority. An explicit change of request, pause, or stop takes precedence; report completed and residual work when stopping. Menus omit Stop and Cancel without limiting the user's ability to request them.

### Establish readiness before offering effects

Resolve authorized, derivable work before asking: inspect facts, prepare links, run available required checks, and complete affected re-review. Ask directly for a genuinely user-owned missing fact or scope/preservation decision. Fact questions are not action menus. If no supported remedy is selectable for a verified external blocker, report it without inventing Wait/Resolve choices or promising monitoring.

Advancement requires current correctness/version evidence, successful required review checks, completed affected re-review, and resolution or explicit retention of pending unreasonable findings and required elegance burdens, including earlier groups. Missing elegance evidence alone does not block advancement. Optional improvements and unselected O advice remain optional.

Start delivery preparation when the user explicitly requests delivery or its preparation, or when delivery is already pending. Review, remedies, and advancement alone do not trigger that work. Before offering Pass for the requested delivery, complete Delivery's derivable inventory, supplementary review, and checks, including existing staged work. Honor explicit exclusions and preservation requirements, asking directly when their resolution belongs to the user. Unfinished preparation and unresolved decisions are not verified unavailability. A verified delivery-only limitation still permits ordinary Continue/Finish when review remains valid and no delivery is pending. If no delivery effect remains, offer advancement instead of empty delivery.

### Present every applicable alternative

Use the first matching row, include every available choice in its order, and label consecutively with the recommendation at A. Describe actual IDs, consequences, and effects. Check omitted applicable choices before sending and explain any verified reason for their unavailability.

| Current situation | Ordered choices |
| --- | --- |
| Pending delivery has unresolved findings | **Fix and optimize** if both kinds remain, otherwise **Fix** or **Optimize**; **Ignore** the named findings or burdens. |
| No pending delivery; unreasonable findings and any elegance improvements remain | **Fix and optimize**; **Ignore** the named defects and improvements. |
| No pending delivery; unreasonable findings only | **Fix**; **Ignore** the named defects. |
| No pending delivery; required elegance remains | **Optimize**, including outstanding optional improvements; **Ignore** the named burdens and improvements. |
| Only optional improvements remain | **Optimize**; **Pass** for requested, prepared delivery, explicitly retaining those named items; **Continue** or **Finish**. |
| No outstanding findings or improvements; requested delivery is prepared and effects remain | **Pass** when available; **Continue** or **Finish**. |
| Final group with no finding, supported M/O improvement, requested delivery effect, or decision left | Report verified completion without a menu. |
| Review can advance without requested delivery, or delivery has no effects or is unavailable | **Continue**, or **Finish** at scope end. |

When an outstanding O observation has a supported optimization, include an explicit **Optimize O…** in any genuine menu. With no necessary main issue or pending delivery taking priority, recommend that optimization ahead of Pass/Continue. Combine M and O remedies only with their IDs and effects named. Otherwise keep the necessary main remedy recommended and place O optimization after the main remedy and Ignore, stating what remains unresolved. For an already authorized ready delivery, disclose O advice without manufacturing another menu or delaying execution.

A row does not make an unavailable action executable. Ask for a user-owned fact needed by the recommended remedy; independently supported remedies can remain selectable with the blocker stated. Natural-language subsets need no exhaustive menu of combinations. Pass's explicit retention covers only the named assessed optional items. Continue can defer them without declining them.

Start each option with a short bold action label, then its concrete effects. In Chinese, Continue's label is exactly **继续**; put purpose and next position afterward. Pass states actual commit/push/Viewed effects and subsequent advancement. Preparation owns the separate workspace-choice priorities.

## Execute, re-review, and resume the selected request

Carry the existing repair context through implementation, checks, and affected re-review: selected items and findings, fixed comparison and workspace, necessary supporting paths and context, applicable evidence and logs, disclosed effects, accepted trade-offs, saved next position, and any pending compound request. Reuse complete applicable guidance, supported verification procedures, and still-valid results with their supporting records, including full logs where available, rather than reconstructing them for the report. Preserve Pass versus only-deliver through supplementary review, repairs, and interrupted writes.

Limit edits to selected remedies and necessary supporting changes. After reviewed content changes, including selected O work, run required checks and refresh before/after evidence and links. Independently re-review the changed and affected previously reviewed parts, including unexpected changes. Keep pinned remote PR evidence separate from checked unpublished content. Report the repair in a dedicated reply apart from unseen main files using Report Format; preserve IDs/groups without recounting progress. A repair or optimization is complete only when checks and re-review confirm it; retained burdens remain trade-offs.

Without pending delivery or an explicit compound request, a single Fix, Optimize, or Ignore ends at the updated decision. With a pending request, complete the dedicated re-review and continue its remaining authorized effects. Any unresolved unreasonable finding or outstanding required or optional improvement in required delivery coverage, including selected O work, suspends delivery for remedy or explicit retention. An earlier Pass accepts no later discovery and authorizes no unselected repair. Once those findings and prerequisites are resolved, resume the original request rather than asking for Pass again or substituting Continue/Finish.

Changed effects outside existing authority need a concrete decision; failed checks pause dependent work. Use Delivery for physical execution and recovery, preserving confirmed effects while unresolved work remains pending. After all applicable effects and readbacks succeed, Pass advances to the saved next group or finishes; only-deliver stays. If delivery is incomplete, report confirmed, unknown, and remaining effects and retain its intent for a supported later resume.
