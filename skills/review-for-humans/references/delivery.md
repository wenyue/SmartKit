# Delivery

Read before preparing or offering delivery, executing it, or recovering its effects. This guide owns the complete delivery scope, review coverage, readiness, writes, readbacks, and physical recovery. The Skill entry owns action selection, pending user intent, and advancement; return delivery facts to that loop.

## Define delivery for the selected workspace

Delivery completes the applicable effects for all outstanding changes in the selected, disclosed review workspace, regardless of who made them or in which conversation. “Current workspace” means that exact path, not the Agent process's incidental working directory.

| Review context | Applicable effects, in order |
| --- | --- |
| PR | Commit all outstanding workspace changes, publish the complete outgoing scope to the verified PR source, then record all eligible files reviewed in this conversation as Viewed and verify the result. |
| Local or branch | Commit all outstanding workspace changes. Push only when the user selected a disclosed publication destination and effect; without a PR there is no Viewed recording. Do not create a PR implicitly. |

Reuse already completed, still-valid effects. A clean workspace needs no empty commit; a current source ref needs no redundant push. Viewed-only is possible when no commit or publication effect remains, not a way to leave unrelated outstanding workspace changes out of a selected delivery. A snapshot review first needs a selected deliverable workspace before any local or publication effects can be promised.

Selecting delivery covers the complete disclosed workspace and outgoing scope, including changes from outside this conversation. Their origin calls for inventory and the applicable review, not a separate inclusion question. Explicit user exclusions or conflicting preservation requirements must be resolved before delivery; do not silently make a smaller commit. Delivery grants neither unrelated history changes, PR approval, nor merging.

## Keep scope and review coverage distinct

| Scope | Required coverage |
| --- | --- |
| Main review and progress | The fixed comparison and filters selected for ordinary file groups. |
| Commit and publication | Inventory and required checks cover every actual submitted delta and outgoing commit, including tests, documentation, generated/supporting files, staged-only changes, nonignored untracked files, and work outside the main comparison. Semantic review covers all of their non-test changes. |
| Viewed | Every current PR file whose complete intended PR delta has been reviewed in this conversation, including earlier groups advanced without recording and supplementary review. |

Before any delivery write, establish current-conversation review of every non-test change in the complete proposed commit and publication scope. Test files are excluded from both ordinary main review and delivery supplementary review, using the same repository/main-review classification. Production files do not become test files merely because tests use them. Tests remain in the full commit/publication inventory and required checks. Earlier Fix or Optimize may already provide it; authorship, passing tests, a filename's appearance in a report, and another conversation's review do not prove it. Reuse assessments only while their exact content, dependencies, and effects remain valid. An amended commit also needs coverage of the non-test content it retains. Existing unpublished commits are included in publication coverage; unchanged content already at the destination is not newly published merely because it is an ancestor.

For every uncovered non-test change, apply the entry's full inspection standards, including the necessary file and connected context. Before reporting the supplementary review, read [Report Format](report-format.md) and use its fixed presentation. Show it with fixed before/after evidence and links, apart from unseen main-review groups. Reuse existing IDs for affected items and allocate new continuous M IDs to new supplementary modifications, explicitly distinguishing them from main progress. Concise or omitted explanation never establishes coverage of an unreviewed change. Otherwise excluded non-test files still receive this review; test files do not. Supplementary coverage does not change the main file total, advance its saved position, or remove unseen files through refreshed Viewed filtering.

Supplementary review is required preparation. Return new findings and evidence gaps to the entry before writing; its pending-request rules govern the resulting decision and resumption. Explicitly retained judgments remain recorded.

Passing tests or including test files in a commit does not make those unreviewed files eligible for Viewed. A reviewed repair fragment is not whole-file PR coverage. Build the Viewed set from complete per-file PR deltas and current-conversation assessments. Supplement uncovered portions of a file intended for recording; leave other partially reviewed files unmarked and disclose that distinction. Once the intended set is fixed, a missing check or failed readback keeps delivery incomplete; never drop a selected path merely to finish. An O observation alone supplies no whole-file coverage, although its repaired file can qualify after complete supplementary review.

## Prepare the exact effects

Identify repository, selected workspace, branch, intended final contents, and all outgoing ancestry when publishing. Inventory staged, unstaged, untracked, conflicted, and submodule state. Retain the original index, tip, worktree, and applicable untracked recovery evidence. For partial staging, establish coherent final worktree content and disclose which staged version it supersedes. Resolve ignored, sensitive, disposable, or independently owned content through its governing restrictions rather than automatically adding or silently excluding it. Conflicts block delivery.

Run required checks over the complete intended commit/publication and establish the review coverage above. Finish derivable read-only preparation and available supplementary review before reporting readiness. Unknown inventory, interfaces, or coverage is not proof of unavailability. Distinguish a limitation affecting delivery alone from one invalidating review; the entry owns the resulting choices.

For PR effects, verify owning/source repositories, source branch and remote, authenticated viewer, base/head, and usable write/readback interfaces. For local/branch publication, establish the selected destination and exact outgoing scope; do not invent an upstream or infer push authority from a commit request. Disclose actual remaining writes, full contents and outgoing commits, Viewed set, and checks/limits so the entry can describe the concrete action. Include amendment and exact-lease publication when applicable; do not hide those effects behind an action label.

Keep publication and Viewed coverage separately inspectable. The main report's selected-file and Viewed filters do not reduce delivery review. A larger full-workspace scope does not authorize recording a partially reviewed PR file.

## Execute the checked plan

Resolve `<skill-root>` from the actual loaded Skill, independently of the target working directory. Read the helper's supported capabilities and interface before choosing it:

```text
python "<skill-root>/scripts/complete_review.py" --help
```

The helper freezes and executes supported PR effects; the Agent supplies semantic coverage, successful checks, scope, and authority. Its help owns request fields, commands, evidence/state storage, outputs, and retry mechanics. Helper preparation may preserve private evidence and Git objects while leaving the real index, branch, and files unchanged. Use the manual sequence below when the actual plan falls outside those capabilities; never change or omit required effects merely to fit the tool. Helper unavailability waives no prerequisite.

Use this manual sequence for local/branch delivery or unsupported helper cases. It also states the required outcomes of helper execution, not a second implementation to run afterward.

1. Revalidate the intended contents, tip/index/worktree, affected dependencies, and relevant destination/PR version and outgoing ancestry. Changed content needs fresh inventory, affected review, and checks before reusing authority. Resolve changed destinations, methods, or explicit scope restrictions with the user; origin alone does not require another inclusion decision. An expected new head needs content/version verification, not repetition of unchanged valid review.
2. When needed, stage the full disclosed final content and verify the intended index tree. Use `git commit --amend` when recorded actions establish HEAD as this review's fix/optimization commit and both the current branch and any push target are neither `master` nor `main`; otherwise create a new commit. Run normal hooks, then verify commit, parent, full tree, index, and remaining worktree. Hook changes require checks and affected review; leave no unexplained residue.
3. When selected publication is needed, revalidate outgoing ancestry after hooks. Replacing an already-published review commit uses `--force-with-lease=<ref>:<verified-old-remote-SHA>` to the verified source ref; otherwise push normally. Stop on drift or rejection. Read back the destination and complete published delta; for a PR also read base/head. Confirm the expected commit, checked content, and valid assessments. No automatic rebase, commit exclusion, tag publication, or submodule publication is included.
4. For PR recording, verify viewer, both commit IDs, and full-file coverage on the actual published version. Mark every eligible path in the prepared Viewed set still awaiting recording. Read back every selected path, including reused markings, and base/head. All selected paths must be `VIEWED` with unchanged base/head throughout recording.
5. When all applicable effects and readbacks succeed, report verified delivery and the actual resulting workspace and remote state. Return this result to the entry; execution does not itself advance the review.

## Reconcile incomplete effects

Retain selected workspace, inventory, fixed evidence and assessments, accepted trade-offs, publication/Viewed sets, viewer/version, and completed/failed/unknown steps. On an interruption or uncertain response, inspect actual local/remote results before retrying. Reuse confirmed effects and perform only missing steps; do not roll back automatically. The entry retains the user's pending request and review position separately.

If content, dependencies, destinations, or effects changed, return to the relevant inventory, coverage, and checks before proceeding. Report resulting findings or authority changes to the entry. Preserve successful effects and recovery evidence while the user's decision is pending.

Every required readback must succeed. If an interface is unavailable or a result is uncertain, report confirmed, unknown, and pending effects; delivery remains incomplete. At a supported later opportunity, inspect actual state and resume within unchanged authority. An explicit stop preserves recovery evidence and reports residual effects as incomplete.