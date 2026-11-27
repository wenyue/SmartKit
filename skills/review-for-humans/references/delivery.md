# Delivery

Complete the physical effects selected through the [Skill entry](../SKILL.md). The Agent establishes coverage and authority; the completion helper inventories, freezes, executes, and verifies supported PR effects. Return findings and actual results to the entry for decisions and advancement.

## Establish the effect set

For local or publication effects, use the exact disclosed delivery workspace. Cover all outstanding changes there and the complete outgoing scope, including work from outside this conversation.

| Review context | Applicable effects, in order |
| --- | --- |
| PR | Commit outstanding changes in the selected workspace and publish the complete outgoing scope to the verified PR source when applicable. Record every eligible file reviewed in this conversation as Viewed, with readback. |
| Local or branch | Commit outstanding workspace changes. Publish only to the destination and with the effect the user selected; PR creation and Viewed recording are not implied. |

Reuse complete, still-valid effects. A clean workspace needs no empty commit; a current source ref needs no redundant push. Viewed-only delivery applies only when no commit or publication remains. A Snapshot can use manual Viewed-only delivery through verified, authorized remote write and readback interfaces for its reviewed version, without a local workspace. Any selected local or publication effects from a Snapshot need a deliverable workspace. A different current base/head leaves Viewed for the reviewed version pending.

When a commit is needed, amend when recorded actions establish HEAD as this review's fix/optimization commit and both current and push-target branches are neither `master` nor `main`; otherwise create a new commit.

Resolve explicit exclusions and conflicting preservation requirements before delivery. Origin alone needs no additional inclusion question, and review filters do not narrow the submitted scope. Authority excludes unrelated history changes, PR approval, and merging.

When local or publication effects apply, inventory staged, unstaged, nonignored untracked, conflicted, and submodule state, the intended final contents, and outgoing ancestry. For partially staged files, establish coherent final worktree content and disclose the staged version it supersedes. Resolve ignored, sensitive, disposable, or independently owned content through its governing restrictions. Resolve conflicts before local or publication effects. Use the helper's inventory on its supported path, or collect it directly for manual delivery.

## Match the plan to existing coverage

Commit and publication require checks covering every submitted delta and outgoing commit, and current-conversation semantic review of every non-test change in that set. This includes supporting, generated, staged-only, untracked, and amended content and existing unpublished commits. Content already at the destination is not newly published merely because it is an ancestor. Tests use the entry's repository classification: they remain within inventory and checks, while production code used by tests remains production code.

Reuse recorded assessments and check results while they cover the exact intended contents, relevant dependencies and inputs, and effects. A commit or expected PR-head change alone does not invalidate that evidence. Complete only missing or stale coverage through the project's verification owner and the entry's supplementary-review procedure. That procedure owns report format, item identities, findings, and pending user decisions; main-review progress and the saved sequence stay unchanged.

Derive Viewed separately from complete per-file PR deltas reviewed in this conversation, including earlier groups not yet recorded. A repaired fragment or successful check does not establish whole-file coverage. Supplement uncovered portions of files intended for recording; leave other partially reviewed files unmarked and disclose why. Thus a repair may be ready to publish while its file's original PR changes remain in the saved review sequence. Unreviewed tests remain ineligible.

Disclose the concrete remaining writes, full submitted contents, outgoing commits, intended Viewed set, and checks or limitations, including amendment and exact-lease publication where applicable. Reuse existing disclosures while they remain accurate. A selected Pass authorizes its disclosed effects; new findings or changed effects return to the entry without losing that pending selection. Resolve coverage gaps and user-owned decisions before delivery writes. Once fixed, the intended Viewed set cannot be reduced to conceal a failed check or readback.

## Complete supported PR delivery with the helper

Resolve `<skill-root>` from the loaded Skill and read its supported interface:

```text
python "<skill-root>/scripts/complete_review.py" --help
```

CLI help owns capabilities, request fields, commands, private state, transport requirements, and retries. The helper requires a verified exact workspace even for Viewed-only. Supply that workspace, established PR/source identity and viewer, intended effects, and existing review, verification, and authorization records. Hashes bind records; they do not establish semantic coverage or permission.

1. **Prepare.** Call `prepare` to obtain the complete current inventory and frozen plan. Compare that plan with the coverage and authority above, using the retained inventory rather than compact counts alone. Resolve any uncovered or changed scope before execution; prepare a replacement only when the settled plan or its evidence changes.
2. **Run.** Execute the covered, authorized plan with `run`. The helper revalidates current state, runs normal hooks, verifies the commit and outgoing scope, publishes to the exact source conditionally, and reads back the PR version and every selected Viewed path. Its Viewed requests retry transient failures by default, reconciling uncertain writes before repeating them. Use those results as the evidence for its mechanical responsibilities.
3. **Finish.** A successful `complete` result, together with the established coverage and authority, completes delivery. Report its resulting workspace, commit, publication, and Viewed state to the entry. Further inspection is needed only for an incomplete or uncertain result or evidence of a subsequent change.

The helper's private state is the delivery recovery record. Keep it outside the worktree in task-managed private temporary storage, referencing existing review and verification evidence. The task owns its retention and cleanup: preserve it while delivery or recovery is pending and until the required result and evidence have been handed off. Use the existing records directly; delivery requires no second archive, copied log collection, or rewritten evidence summary. Any separately requested retention or export keeps its own scope and lifecycle.

### Review the next group while Viewed runs

For authorized Viewed work, use the Harness's managed background process/session while reviewing the next group read-only after Pass or explicit continuation. Retain the handle, output and final exit status; use foreground execution if managed sessions are unavailable.

Finish applicable commit/publication prerequisites first. For publication plans, wait for `phase=viewed` or successful completion, verify the resulting head, and pin the comparison through Preparation. Viewed-only uses its existing comparison. Keep the frozen request, paths, viewer/version, evidence, and any selected workspace unchanged.

Collect status near the next report's end: incomplete Viewed leaves delivery pending without blocking independently valid read-only review. Before repairs, Git/evidence changes or scope exit, join the process or safely stop it and wait for its owned child to exit; retain recovery state for incomplete delivery. Manual Viewed workers retain these lifetime rules and their reconciliation/readback duties.

## Use manual execution for unsupported plans

Use this path for local/branch delivery and effects the helper cannot represent, including eligible Snapshot Viewed-only without the helper's workspace. Preserve the complete selected effects. An unavailable required interface leaves dependent delivery pending.

1. **Prepare and revalidate.** For local or publication effects, collect the inventory above and retain original index, tip, worktree, and applicable untracked recovery evidence in private task storage. For publication, establish the destination and outgoing scope, including the source repository, branch, and remote for PR publication. For PR effects, verify the owning PR, authenticated viewer, current base/head, and authorized write/readback interfaces. Match contents, dependencies, scope, and authority to valid coverage before writing.
2. **Commit when needed.** Stage the full disclosed final content and verify the intended index tree. Apply the selected creation or amendment mode through normal hooks, then verify commit, parent, complete tree, index, and remaining worktree. Hook changes require affected checks and review; explain any residue.
3. **Publish when selected and needed.** Revalidate outgoing ancestry after hooks. Replacing an already-published review commit uses `--force-with-lease=<ref>:<verified-old-remote-SHA>` to the verified source ref; otherwise push normally. Stop on drift or rejection. Read back the destination and complete published delta, plus PR base/head when applicable, to establish the expected commit, checked content, and valid assessments. This includes no automatic rebase, commit exclusion, tag publication, or submodule publication.
4. **Record PR Viewed.** Verify the viewer, both commit IDs, and whole-file coverage against the current PR version after any applicable publication. For each outstanding path, bind the mark to that viewer and version with a supported guard or authoritative checks before and after the write. Stop further writes on drift or an uncertain result. Retain confirmed marks and reconcile the attempted mark before retrying. Read back every selected path, including reused marks, for the same viewer and base/head. All must be `VIEWED`.
5. **Finish.** Report the resulting workspace and remote state as applicable once every selected effect and readback succeeds. Retain the manual recovery record under the same private-storage lifecycle as helper delivery.

## Resume incomplete delivery

Preserve the selected workspace and effects, coverage records and accepted trade-offs, viewer/version, and confirmed, failed, or unknown results. Resume the same helper state through its documented recovery route; for manual delivery, inspect actual local and remote results and perform only missing work. Reconcile uncertain publication before changing transport or retrying. A transport change stays within authority only while the effects and explicit method restrictions still hold.

Changed content, dependencies, destinations, or effects need the corresponding inventory, coverage, and authority resolved before proceeding. Return new findings and decisions to the entry while preserving confirmed effects. Report unavailable, unknown, and pending outcomes as incomplete; an explicit stop preserves recovery evidence and reports residual effects. Recovery includes no automatic rollback.
