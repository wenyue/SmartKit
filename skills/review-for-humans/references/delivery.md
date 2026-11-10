# Delivery

Complete the physical effects selected through the [Skill entry](../SKILL.md). The Agent establishes coverage and authority; the completion helper inventories, freezes, executes, and verifies supported PR effects. Return findings and actual results to the entry for decisions and advancement.

## Establish the effect set

The selected workspace is the exact disclosed review path. Delivery covers all outstanding changes there and the complete outgoing scope, including work from outside this conversation.

| Review context | Applicable effects, in order |
| --- | --- |
| PR | Commit outstanding workspace changes, publish the complete outgoing scope to the verified PR source, and record every eligible file reviewed in this conversation as Viewed, with readback. |
| Local or branch | Commit outstanding workspace changes. Publish only to the destination and with the effect the user selected; PR creation and Viewed recording are not implied. |

Reuse complete, still-valid effects. A clean workspace needs no empty commit; a current source ref needs no redundant push. Viewed-only delivery applies only when no commit or publication remains. Snapshot review needs a selected deliverable workspace before local or publication effects can be promised.

When a commit is needed, amend when recorded actions establish HEAD as this review's fix/optimization commit and both current and push-target branches are neither `master` nor `main`; otherwise create a new commit.

Resolve explicit exclusions and conflicting preservation requirements before delivery. Origin alone needs no additional inclusion question, and review filters do not narrow the submitted scope. Authority excludes unrelated history changes, PR approval, and merging.

The inventory includes staged, unstaged, nonignored untracked, conflicted, and submodule state, the intended final contents, and outgoing ancestry. For partially staged files, establish coherent final worktree content and disclose the staged version it supersedes. Resolve ignored, sensitive, disposable, or independently owned content through its governing restrictions. Conflicts block delivery. Use the helper's inventory on its supported path; collect this evidence directly only for manual delivery.

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

CLI help owns capabilities, request fields, commands, private state, transport requirements, and retries. Supply the selected workspace, established PR/source identity and viewer, intended effects, and existing review, verification, and authorization records. Hashes bind records; they do not establish semantic coverage or permission.

1. **Prepare.** Call `prepare` to obtain the complete current inventory and frozen plan. Compare that plan with the coverage and authority above, using the retained inventory rather than compact counts alone. Resolve any uncovered or changed scope before execution; prepare a replacement only when the settled plan or its evidence changes.
2. **Run.** Execute the covered, authorized plan with `run`. The helper revalidates current state, runs normal hooks, verifies the commit and outgoing scope, publishes to the exact source conditionally, and reads back the PR version and every selected Viewed path. Its Viewed requests retry transient failures by default, reconciling uncertain writes before repeating them. Use those results as the evidence for its mechanical responsibilities.
3. **Finish.** A successful `complete` result, together with the established coverage and authority, completes delivery. Report its resulting workspace, commit, publication, and Viewed state to the entry. Further inspection is needed only for an incomplete or uncertain result or evidence of a subsequent change.

The helper's private state is the delivery recovery record. Keep it outside the worktree in task-managed private temporary storage, referencing existing review and verification evidence. The task owns its retention and cleanup: preserve it while delivery or recovery is pending and until the required result and evidence have been handed off. Use the existing records directly; delivery requires no second archive, copied log collection, or rewritten evidence summary. Any separately requested retention or export keeps its own scope and lifecycle.

### Review the next group while Viewed runs

For authorized Viewed work, use the Harness's managed background process/session while reviewing the next group read-only after Pass or explicit continuation. Retain the handle, output and final exit status; use foreground execution if managed sessions are unavailable.

Finish applicable commit/publication prerequisites first. For publication plans, wait for `phase=viewed` or successful completion, verify the resulting head, and pin the comparison through Preparation; Viewed-only uses its existing comparison. Keep the frozen request, paths, viewer/version, workspace and evidence unchanged.

Collect status near the next report's end: incomplete Viewed leaves delivery pending without blocking independently valid read-only review. Before repairs, Git/evidence changes or scope exit, join the process or safely stop it and wait for its owned child to exit; retain recovery state for incomplete delivery. Manual Viewed workers retain these lifetime rules and their reconciliation/readback duties.

## Use manual execution for unsupported plans

Use this path for local/branch delivery and effects the helper cannot represent. Preserve the complete selected effects; tool limitations do not narrow them. An unavailable required interface leaves dependent delivery incomplete.

1. **Prepare and revalidate.** Collect the inventory above and retain original index, tip, worktree, and applicable untracked recovery evidence in private task storage. Establish the destination and outgoing scope; for PR effects, verify owning/source repositories, source branch and remote, authenticated viewer, base/head, and usable write/readback interfaces. Match contents, dependencies, scope, and authority to valid coverage before writing.
2. **Commit when needed.** Stage the full disclosed final content and verify the intended index tree. Apply the selected creation or amendment mode through normal hooks, then verify commit, parent, complete tree, index, and remaining worktree. Hook changes require affected checks and review; explain any residue.
3. **Publish when selected and needed.** Revalidate outgoing ancestry after hooks. Replacing an already-published review commit uses `--force-with-lease=<ref>:<verified-old-remote-SHA>` to the verified source ref; otherwise push normally. Stop on drift or rejection. Read back the destination and complete published delta, plus PR base/head when applicable, to establish the expected commit, checked content, and valid assessments. This includes no automatic rebase, commit exclusion, tag publication, or submodule publication.
4. **Record PR Viewed.** Verify viewer, both commit IDs, and whole-file coverage against the actual published version. Mark every selected path still awaiting recording, then read back every selected path, including reused markings, and base/head. All must be `VIEWED`, with unchanged base/head throughout recording.
5. **Finish.** Report the resulting workspace and remote state to the entry once every applicable effect and readback succeeds. Retain the manual recovery record under the same private-storage lifecycle as helper delivery.

## Resume incomplete delivery

Preserve the selected workspace and effects, coverage records and accepted trade-offs, viewer/version, and confirmed, failed, or unknown results. Resume the same helper state through its documented recovery route; for manual delivery, inspect actual local and remote results and perform only missing work. Reconcile uncertain publication before changing transport or retrying. A transport change stays within authority only while the effects and explicit method restrictions still hold.

Changed content, dependencies, destinations, or effects need the corresponding inventory, coverage, and authority resolved before proceeding. Return new findings and decisions to the entry while preserving confirmed effects. Report unavailable, unknown, and pending outcomes as incomplete; an explicit stop preserves recovery evidence and reports residual effects. Recovery includes no automatic rollback.
