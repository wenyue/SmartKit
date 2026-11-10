---
name: review-for-humans
description: 按文件解释 PR、分支和本地改动，判断合理性与优雅性，协助用户选择后续行动。
disable-model-invocation: true
---

# Review for Humans

Make fixed changes understandable enough for the human to judge them and choose what happens next. Establish why the behavior is needed before judging how it is implemented. Review authorizes evidence capture and link preparation. Explain complete file groups before acting on selected review remedies, delivery, or advancement.

This entry owns review scope, assessment, findings, progress, and user decisions. Load [Preparation](references/preparation.md) for PR or remote-aligned branch evidence and workspace selection. Read [Report Format](references/report-format.md) in full before every ordinary, supplementary, repair, or selected-O report and before presenting an action menu. Load [Delivery](references/delivery.md) when offering Pass, preparing or carrying out selected delivery, or determining whole-file Viewed eligibility when a repair touches a PR file not yet fully reviewed. An unavailable required guide leaves dependent work incomplete. [Conversation Examples](examples/conversations.md) illustrate difficult choices without adding policy.

## Fix the comparison and reading order

| Request | Comparison and initial evidence |
| --- | --- |
| PR | Preparation verifies source identity and workspace, pins base/head, and obtains the authenticated viewer's complete file-level Viewed filter. |
| Branch | Pin the tip and merge-base with a reliably established comparison base. Ask for an unknown base instead of assuming `main`. |
| Local changes or no stated scope | Compare index to worktree: unstaged changes only. |
| Selected files | Restrict the applicable comparison to those paths. |

Honor explicit alternative comparisons and historical versions. PR and branch comparisons exclude local uncommitted changes unless requested. For local review, exclude staged-only files, assess only the unstaged part of partially staged files, and recognize a worktree reversal of staged content as an unstaged change. Include untracked additions only when explicitly requested. These defaults prevail over different defaults in other review guidance.

Use the repository's test classification to skip semantic review of test code, including unit, integration, and end-to-end tests, in main review, supplementary review, and repair re-review. Consult relevant tests as evidence. Apply the test exclusion and the selected-file, Viewed, and local filters before counting files, modifications, or progress. The delivery guide separately accounts for the complete submitted and outgoing scope. Review filters never narrow a commit or its required checks.

Read-only review uses source, test definitions, and existing valid results. Finishing a file group or review, or recording Viewed alone, does not trigger UT or complete change-set verification. Changes made during this review follow the repaired-result checks below; an explicit verification request retains its stated scope. Missing execution evidence limits the judgments that depend on it: identify those limits and continue independently supported assessment.

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

For supported behavior, compare the chosen design with a smaller sufficient alternative: keep an existing interface, use an accurate existing owner, call directly, or remove a layer with no unique responsibility. A justified safeguard may cover a slightly broader range of cases if that simplifies the implementation and the effects on normal use are acceptable. Required feedback, logging, recovery, and lifecycle protection still need owners. A proposal to change supported behavior or contracts is a scope decision, not behavior-preserving optimization.

Scrutinize every added file and added or changed declaration or contract, including functions, types, members, and state in existing files. A tiny file or trivial forwarder still introduces a boundary. New files need especially strong evidence for a distinct responsibility and why an existing owner or local placement would not suffice. Scale further scrutiny by actual exposure, caller dependence, lifetime, and change impact: shared interfaces and long-lived state need stronger evidence and concrete alternatives than local helpers. Ordinary local variables need no separate necessity rationale; visibility keywords do not establish actual exposure.

Short bodies, caller counts, uniform presentation, speculative reuse, and testing convenience alone justify no boundary. A real responsibility can justify one with a single caller. Source, tasks, and contracts can supply the reason without rationale comments or one report item per declaration.

### Judge each modification on both axes

| Judgment | Basis |
| --- | --- |
| ⚖️ **Reasonable** | Required outcomes, accepted scope, supported behavior/contracts, and justified operating costs and risks. |
| ⚖️ **Unreasonable** | A material task, behavior, or contract defect, including a violated structural obligation, unnecessary scope, or unjustified operating cost or risk. Identify severity, affected conditions, impact, and correction. |
| 🎨 **Elegant** | Responsibilities, boundaries, and interfaces earn their understanding and maintenance cost. Expression is readable; abstraction, state, branching, repetition, and defense have concrete benefits. Comparable patterns and interfaces are consistent, with justified departures. |
| 🎨 **Needs improvement** | A structural defect violates a supported obligation. Explain the obligation, concrete consequence, and necessary correction; record the same item as an unreasonable finding for Fix. |
| 🎨 **Optional improvement** | The structure meets supported obligations, but a simpler or more consistent alternative offers enough benefit for its change cost. Explain the burden, remedy, and benefit; optimization remains optional. |
| **Insufficient evidence** on either axis | Name the missing material evidence and how to obtain it. Keep any supported judgment on the other axis. |

Attach judgments to the responsible modification and explain concrete causes and user or caller consequences. Assess both axes even when Report Format allows a compact explanation. One good change cannot cancel another change's defect, burden, or evidence gap. Explicit retention preserves the judgment and consequences.

Keep the axes independent. An avoidable structural burden alone supports an optional improvement. A behavioral defect alone does not prove poor structure. A structural requirement violation also needs a correctness finding, with one modification ID and one Fix remedy across both judgments. Missing need or ownership evidence establishes neither elegance nor a structural defect. Omit preference and low-benefit polish, and combine remedies for the same underlying problem.

Assign severity only to unreasonable findings: P0 critical/immediate, P1 serious/prompt correction, P2 normal priority, P3 lower-impact but worth correcting. Optimization is always optional. A correction necessary to meet a supported obligation is Fix, even when the defect is structural.

## Explain complete groups and preserve their identity

Use Report Format for the applicable report kind. Assign continuous M IDs across files and groups, grouping implementation steps by the problem they solve and separating independent changes that cannot share one explanation. One localization file is one modification. Minor accompanying edits without findings may stay in the overview or be omitted from explanation; they remain within assessment coverage.

Keep an existing item's ID through supplementary review and repair. Additional separately explained supporting modifications receive the next unused M IDs and retain their relationship to the original finding. Present each item once in a report; a supporting file does not repeat the original item as another numbered item. Repair and supplementary IDs share the continuous sequence but add no main progress. Selected-O work retains the separate identity below.

Every supported unreasonable finding and worthwhile optional improvement needs an actionable M item, using an existing item or adding one. Its judgments explain the concrete problem, severity when applicable, trigger, impact, and correction or benefit. Defects in unchanged code belong here when this change introduces, triggers, or aggravates them. Associate each with the responsible M item.

Internally size each main group by review units: a simple modification meeting Report Format's compact criteria counts as 1 unit; a normal modification requiring its detailed form counts as 2. End the group after the complete file that brings its total to at least 20 units, never midway through a file. Reset the unit count for the next group, and show the shorter remainder at scope end. Keep this unit accounting internal.

Report progress using cumulative displayed main files out of eligible files, each once, and the actual cumulative number of displayed main modifications only. Supplementary items, repairs, and incidental observations add neither main-group units nor main progress. Progress implies neither successful delivery nor Viewed recording.

Close the group with its conclusion and progress, actual checks and limits, pending unreasonable IDs with severity and impact, accepted trade-offs, and optional suggestions with remedies and benefits. Retain evidence, judgments, findings and decisions, group membership, next position, and next M ID across replies. Change totals only when scope changes; a commit that cleans the worktree does not erase undisplayed fixed evidence.

### Separate incidental observations

Necessary reading may reveal an unrelated pre-existing issue. Establish both its evidence and that the selected change neither introduced, triggered, nor aggravated it; this is not an audit of unrelated history or the repository.

Give it a continuous O ID, title, source link or location, evidence and impact, independence, and recommendation or benefit. Report Format places it with its source file when attributable. It adds no main file, modification, progress, or automatic Viewed eligibility. Unselected O advice creates no main-review or delivery gate.

Bulk Fix, Optimize, Ignore, and acceptance exclude O items unless the user explicitly expands scope or selects them. A selected O repair receives separate evidence, checks, and re-review of its change and affected context, using O IDs and two judgments without new main M IDs or progress. Its changes enter delivery coverage; resulting failures or unresolved findings can block delivery. Delivery determines any whole-file Viewed eligibility.

## Turn the findings into a real choice

### Interpret actions and their authority

| Action | Selected effect |
| --- | --- |
| **Fix** | Repair unreasonable findings, check, and re-review. |
| **Optimize** | Implement selected optional improvements, preserving supported behavior and contracts, then check and re-review. |
| **Fix and optimize** | A compound request combining both explicitly named remedy sets, rather than a separate routine menu option. Bare Fix keeps its narrower meaning. |
| **Ignore** | Leave explicitly selected defects, burdens, or optional improvements unchanged, recording their consequences and the user's acceptance or decline. |
| **Pass** | Prepare and complete applicable delivery, including supplementary review and required checks; advance or finish under Delivery's concurrency and completion rules. |
| **Continue** / **Finish** | Advance or end the fully displayed review without delivery. |

Delivery determines the applicable commit, publication, and Viewed effects. Accept explicit “deliver” or “only deliver” requests as the same delivery while keeping the current review position; advance only when the user selects Pass or explicitly requests continuation. Delivery alone is not a separate routine menu option. Neither delivery action grants PR approval or merge authority.

Interpret letters case-insensitively against the latest applicable menu. Clear natural language, subsets, and compound requests can select disclosed effects. An unambiguous menu option supplies its stated scope: “Optimize” can select an option explicitly naming O1. With several matching alternatives, ask which IDs. Without a clear menu scope, bare Fix selects all displayed pending unreasonable M findings, and bare Optimize selects all displayed outstanding optional M improvements, including earlier groups.

Ignore must identify the items and consequences to be retained or declined; clear natural-language acceptance or decline suffices. Ask when either the items or decision is ambiguous. IDs alone identify items, not an action. Retained items cease to be outstanding while their assessed content and effects stay unchanged. Ignoring neither waives checks nor advances the review.

A ready selected action proceeds without routine reconfirmation. Recommendations, sole options, questions, and disagreement grant no additional authority. An explicit change of request, pause, or stop takes precedence; report completed and residual work when stopping. Menus omit Stop and Cancel without limiting the user's ability to request them.

### Apply the decision principles

Offer choices for the user's remaining decisions after completing the current report and any required repair checks and affected re-review. Resolve derivable facts needed to describe a choice; ask directly for a genuinely user-owned missing fact or scope/preservation decision. Fact questions are not action menus. A verified external blocker with no supported selectable remedy needs an explanation, not an invented Wait/Resolve choice.

Pass and Continue/Finish share the reviewed-group prerequisites: current correctness/version evidence, successful applicable repair or explicitly requested verification checks, completed affected re-review, and resolution or explicit retention of pending unreasonable findings, including earlier groups. Missing elegance evidence alone does not block advancement. Optional improvements and unselected O advice remain optional.

Offer Pass proactively alongside Continue/Finish when applicable delivery effects remain. A prior delivery request and finished delivery preparation are not prerequisites for offering it. Describe the selected workspace, applicable full-workspace commit/outgoing publication/Viewed effects, and subsequent advancement. Unreviewed local or staged changes, uncovered outgoing commits, and remaining delivery checks are work that selecting Pass starts. They do not by themselves remove the choice. Verified limitations and user-owned unresolved scope decisions still constrain the effects that can be offered; use these principles for cases outside the common tables.

Selecting Pass starts Delivery's inventory, supplementary review, and checks; explicit preparation requests can start that work without authorizing writes. Disclose the resulting concrete plan before executing its effects, reusing the selection's authority while scope, destination, and effects remain within it. If supplementary review has no new actionable finding or optional improvement, complete the prerequisites and deliver without a second Pass question. New items require the supplementary-review decision below. Pass explicitly retains only the assessed optional items named in its choice; Continue can defer them without declining them.

Use one option per action type. Offer Optimize when at least one concrete, outstanding optional improvement has been disclosed for selection. State the default selected IDs and effects inside that option. Subsets and compound requests remain available in natural language. Consolidate supported M and O remedies under the same Fix or Optimize label, while distinguishing the default M scope from O items requiring explicit selection. An option can explicitly select named O items when that is its disclosed scope. Merely mentioning O alternatives does not add them to a bulk M action. Unselected O advice does not delay an already authorized delivery.

The four stage tables specify common situations, with a fixed recommendation and choice order. Apply the principles to other situations rather than extending the tables with exhaustive combinations. Use the applicable row, label its choices consecutively with the recommended choice at A, and include each applicable action once. Describe concrete IDs, consequences, and effects. A recommendation or sole option never selects itself.

Render these choices using Report Format. Use Continue with its purpose and next position in the description, and Finish at scope end. Preparation supplies the first table, for workspace choices before review. The remaining tables below govern group results, repairs, and supplementary review during delivery.

### After a review group

Include still-outstanding items from earlier groups. The improvement rows also cover selectable O improvements under their separate scope rules; unselected O defects do not create a main-review gate.

| Current situation | Recommended action | Choices, in order |
| --- | --- | --- |
| Unreasonable findings remain; no optional improvement is offered | **Fix** | **Fix**; **Ignore** |
| Unreasonable findings remain; optional improvements are also offered | **Fix** | **Fix**; **Optimize**; **Ignore** |
| Only optional improvements are offered | **Optimize** | **Optimize**; **Pass**; **Continue** |
| No outstanding finding or improvement is offered | **Pass** | **Pass**; **Continue** |

### After repair or optimization

Show the dedicated repair report first. With no pending delivery or other compound request, use the resulting state below; a completed remedy does not itself advance or deliver. With delivery pending, retain that request and use the supplementary-review table for remaining decisions.

| Current situation | Recommended action | Choices, in order |
| --- | --- | --- |
| Re-review leaves unreasonable findings; no optional improvement is offered | **Fix** | **Fix**; **Ignore** |
| Re-review leaves unreasonable findings and optional improvements | **Fix** | **Fix**; **Optimize**; **Ignore** |
| Required checks and re-review pass; only optional improvements are offered | **Optimize** | **Optimize**; **Pass**; **Continue** |
| Required checks and re-review pass; no outstanding finding or improvement is offered | **Pass** | **Pass**; **Continue** |

### During supplementary review for selected delivery

Pause delivery writes for new actionable findings or worthwhile optional improvements in required delivery coverage. Present the applicable choices below without adding Pass or Continue: delivery is already selected. Previously retained items stay resolved while their assessed content and effects remain valid; unselected O advice stays outside the gate.

| Current situation | Recommended action | Choices, in order |
| --- | --- | --- |
| Supplementary review finds unreasonable findings only | **Fix** | **Fix**; **Ignore** |
| Supplementary review finds unreasonable findings and optional improvements | **Fix** | **Fix**; **Optimize**; **Ignore** |
| Supplementary review finds optional improvements only | **Optimize** | **Optimize**; **Ignore** |
| Required coverage has no unresolved finding or improvement | Complete the selected delivery | No new choice; finish prerequisites and resume automatically |

Fix or Optimize can leave other items unresolved. After the selected remedy and its checks and re-review, resolve those remaining decisions through this table. Ignore records explicit retention without waiving checks. Once the required coverage and prerequisites are satisfied, execute the original Pass or only-deliver request without asking for delivery again.

## Execute, re-review, and resume the selected request

### Carry the review forward

Keep the fixed comparison, selected workspace, item and group identities, and saved review position. Carry the selected findings and their supporting paths and context, accepted trade-offs, and disclosed effects into the repair. Retain any pending compound request, including the distinction between Pass and only-deliver, through supplementary review, repairs, and interruptions.

Reuse complete applicable guidance and supported verification procedures, and reuse evidence only while it remains valid for the exact contents, dependencies, and effects being assessed. Keep its supporting records, including full logs where available. Pinned PR evidence continues to describe the fixed comparison; verification of unpublished repairs must establish the repaired contents separately.

### Establish the repaired result

Limit edits to selected remedies and necessary supporting changes. After reviewed content changes, including selected O work, run required checks through the project's supported verification methods and refresh before/after evidence and links. Reusing evidence never waives a check required on the repaired contents. Independently re-review every changed non-test file, including necessary supporting and unexpected changes, and affected previously reviewed parts. Tests retain their evidence and required-check role under the repository's classification. Failed or unavailable required checks leave dependent work incomplete.

Report the repair in a dedicated reply apart from unseen main files using Report Format's common file layout. Cover every changed non-test file and retain existing IDs and groups without recounting main progress. A repair or optimization is complete only when checks and re-review confirm it; retained burdens remain trade-offs.

### Resume the remaining authorized work

Without pending delivery or an explicit compound request, a single Fix, Optimize, or Ignore ends at the updated decision. With a pending request, complete the dedicated re-review and continue its remaining authorized effects. Delivery pauses for unresolved unreasonable findings or newly disclosed optional improvements awaiting a decision in its required coverage, including selected O work. Resolve these through an authorized remedy or explicit retention; an earlier Pass neither accepts later findings nor authorizes unselected repairs. Once the findings and prerequisites are resolved, resume the original request without asking for Pass again or substituting Continue/Finish.

Use Delivery for execution, concurrent Viewed recording, and recovery. Changed effects outside existing authority need a concrete decision; preserve confirmed effects while unresolved work remains pending. Pass may start the saved next group read-only once only Viewed remains; only-deliver stays unless continuation was selected. Report confirmed, unknown, and remaining effects, retaining incomplete delivery and its intent for supported resume.
