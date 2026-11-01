# Delivery

Prepare and verify the physical effects selected through the [Skill entry](../SKILL.md). This guide owns the complete delivery inventory, semantic coverage, checks, writes, readbacks, and recovery evidence. Return readiness, findings, and actual effects to the entry, which owns menus, pending intent, and advancement.

## Establish the complete effect set

“Selected workspace” means the exact disclosed review path, not the Agent process's incidental working directory. Delivery covers all outstanding changes there, regardless of author or conversation.

| Review context | Applicable effects, in order |
| --- | --- |
| PR | Commit outstanding workspace changes, publish the complete outgoing scope to the verified PR source, and mark every eligible file reviewed in this conversation Viewed, with readback. |
| Local or branch | Commit outstanding workspace changes. Push only to a destination and with an effect the user selected; neither PR creation nor Viewed recording is implied. |

Reuse effects that are already complete and still valid: no empty commit for a clean workspace or redundant push to a current source ref. Viewed-only delivery applies when no commit or publication remains; it cannot leave outstanding workspace changes out of a selected delivery. Snapshot review needs a selected deliverable workspace before local or publication effects can be promised.

Selection covers the complete disclosed workspace and outgoing scope, including work from outside this conversation. Origin alone needs no extra inclusion question. Resolve explicit exclusions and conflicting preservation requirements before delivery instead of silently shrinking the commit. Authority excludes unrelated history changes, PR approval, and merging.

Inventory staged, unstaged, nonignored untracked, conflicted, and submodule state; identify the repository, branch, intended final contents, and complete outgoing ancestry. Retain the original index, tip, worktree, and applicable untracked recovery evidence. For partially staged files, establish coherent final worktree content and disclose the staged version it supersedes. Resolve ignored, sensitive, disposable, or independently owned content through its governing restrictions. Conflicts block delivery.

## Establish coverage for those effects

Three scopes answer different questions:

| Scope | Coverage |
| --- | --- |
| Main report and progress | The entry's fixed comparison, filters, and displayed file groups. |
| Commit and publication | Inventory and required checks cover every submitted delta and outgoing commit, including tests, documentation, generated/supporting files, staged-only and untracked changes, and work outside the main comparison. Current-conversation semantic review covers every non-test change in that set. |
| Viewed | Complete intended deltas of current PR files reviewed in this conversation, including earlier groups advanced without recording and supplementary review. |

For commit/publication coverage, reuse an assessment only while its exact content, dependencies, and effects remain valid. Authorship, passing tests, a filename appearing in a report, and review in another conversation do not establish that coverage. An amended commit includes retained non-test content; publication includes existing unpublished commits. Content already at the destination is not newly published merely because it is an ancestor.

Tests use the same repository classification as the main review and are excluded from supplementary semantic review as well. Production code used by tests remains production code. All tests still belong in the inventory and required checks.

For uncovered non-test content, apply the entry's complete inspection standards to the changes and necessary file/caller context. Present supplementary review in the required fixed format with before/after evidence and links, separately from unseen main groups. Reuse IDs for affected items and allocate continuous M IDs for new supplementary modifications. Distinguish these from main progress: supplementary coverage neither changes the main total and saved position nor removes unseen files through a refreshed Viewed filter. O-selected work retains its separate identity under the entry.

Return findings and evidence gaps before any delivery write. Concise presentation or omitted explanations cannot supply missing assessment; explicitly retained judgments remain recorded.

### Derive Viewed from whole-file PR review

Build the recording set from current-conversation assessments of complete per-file PR deltas. A repaired fragment, O observation, passing checks, or inclusion in a commit does not suffice. Supplement uncovered portions of a file intended for recording; leave other partially reviewed files unmarked and disclose why. Unreviewed tests remain ineligible.

Once the intended set is fixed, a missing check or failed readback leaves delivery incomplete; do not drop a selected path to finish. The report's original filters do not narrow eligible recording or delivery coverage, and a larger delivery scope does not justify marking partly reviewed files.

## Make readiness concrete

Run required checks over the complete intended commit/publication scope and finish available supplementary review. Complete derivable read-only preparation before reporting readiness; unknown inventory, interfaces, or coverage is not proof that delivery is unavailable. Identify whether a verified limitation affects delivery alone or invalidates review, then return that distinction to the entry.

For PR effects, verify owning/source repositories, source branch and remote, authenticated viewer, base/head, and usable write/readback interfaces. For local/branch publication, establish the selected destination and exact outgoing scope; a commit request supplies neither an upstream nor push authority.

Disclose the remaining writes, full contents, outgoing commits, Viewed set, and checks/limits. Include amendment and exact-lease publication where applicable. Keep publication and Viewed coverage separately inspectable so the user can authorize the actual plan.

## Choose the execution path

Resolve `<skill-root>` from the actual loaded Skill, independently of the target working directory, and read the helper's supported interface:

```text
python "<skill-root>/scripts/complete_review.py" --help
```

The helper freezes and executes supported PR effects. The Agent supplies semantic coverage, successful checks, disclosed scope, and authority; hashes and plans do not establish them. CLI help owns request fields, commands, private evidence/state, outputs, and retries. Preparation may preserve private evidence and Git objects while leaving the real index, branch, and files unchanged.

Use the manual sequence below for local/branch delivery and plans outside the helper's capabilities. Helper unavailability waives no prerequisite, and unsupported effects must not be omitted or altered to fit it. The sequence also states the outcomes to verify when using the helper; do not repeat writes afterward.

1. **Revalidate.** Check intended contents, tip/index/worktree, affected dependencies, destination or PR version, and outgoing ancestry. Changed content needs refreshed inventory, affected review, and checks before authority can be reused. Resolve changed destinations, methods, or explicit scope restrictions with the user. An expected new head needs content/version verification, not repetition of unchanged valid assessments.
2. **Commit when needed.** Stage the full disclosed final content and verify the intended index tree. Use `git commit --amend` when recorded actions establish HEAD as this review's fix/optimization commit and both the current branch and any push target are neither `master` nor `main`; otherwise create a new commit. Run normal hooks, then verify commit, parent, complete tree, index, and remaining worktree. Hook changes require checks and affected review; explain all residue.
3. **Publish when selected and needed.** Revalidate outgoing ancestry after hooks. Replacing an already-published review commit uses `--force-with-lease=<ref>:<verified-old-remote-SHA>` to the verified source ref; otherwise push normally. Stop on drift or rejection. Read back the destination and complete published delta, plus PR base/head when applicable; confirm the expected commit, checked content, and valid assessments. No automatic rebase, commit exclusion, tag publication, or submodule publication is included.
4. **Record PR Viewed.** Verify viewer, both commit IDs, and whole-file coverage against the actual published version. Mark every prepared eligible path still awaiting recording, then read back every selected path, including reused markings, and base/head. All must be `VIEWED`, with unchanged base/head throughout recording.
5. **Return verified effects.** Only successful completion of every applicable effect and readback establishes delivery. Report resulting workspace and remote state to the entry.

## Reconcile uncertainty before retrying

Retain inventory, fixed evidence and assessments, accepted trade-offs, selected workspace, publication/Viewed sets, viewer/version, and completed, failed, or unknown steps. After interruption or an uncertain response, inspect actual local/remote results and reuse confirmed effects, performing only missing work. Do not roll back automatically.

Changed content, dependencies, destinations, or effects require the corresponding inventory, coverage, and checks before proceeding. Return resulting findings or authority changes to the entry while preserving successful effects and recovery evidence.

An unavailable interface or uncertain result leaves delivery incomplete. Report confirmed, unknown, and pending effects; at a supported later opportunity inspect actual state and resume within unchanged authority. An explicit stop preserves recovery evidence and reports residual effects.
