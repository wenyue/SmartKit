# Transfer Back to a Checkout

The public `return-for-review` route puts accepted task changes into one checkout's working files,
before or after review. Preserve target HEAD and the complete index exactly, so existing staged
content stays staged. The result is always a non-integrating handoff.

## Identify the change and the receiving state

Freeze three distinct inputs before deciding what to write:

| Input | Meaning |
| --- | --- |
| **B** | The immutable shared baseline from which task changes are measured, pinned by commit/tree OID. |
| **S** | The accepted task result, frozen as exact bytes, absence, types and modes. |
| **W** | The target's actual working files at preparation time, including committed evolution and local changes. |

S can include attributable staged, unstaged and untracked work without making a commit or changing
the source index. Resolve those layers into accepted final contents and exclude unrelated work.
Ambiguous ownership, B or S stops preparation and returns the decision to the result owner while
both sides remain retained.

Transfer **B → S**, not the whole source checkout. The target's HEAD or index version is not W, and
its current HEAD is not a convenient substitute for the shared B. Formal review applies only when
independent project/caller policy or an expressly selected history operation requires it.

## Decide the whole combined result

Derive every affected path from B → S, including both ends of supported renames. Capture bounded
path and ancestor evidence and complete target HEAD/index evidence at batch boundaries. Reuse
immutable B and accepted S evidence while dependencies match. Inspect unrelated paths for concrete
preservation risks; ordinary transfer does not require repeated global status or untracked/ignored
inventories.

Where W equals B, the output is S. Preserve target-only changes and include identical edits once.
For overlapping ordinary text, a native three-way merge can combine B as ancestor, W as local and S
as incoming; for example, use `git merge-file -p` on temporary files. A textually clean merge still
needs semantic inspection and verification of combined behavior.

Settle all outputs before target writes. Conflicting hunks, delete/modify cases, complex renames,
binary overlap, unsupported types or modes, incompatible behavior and ambiguous generated output
stop this preparation. Regeneration stays with its deterministic owner and needs accepted authority.

## Freeze a plan the mechanism can preserve

For admitted regular-file create/update/delete in existing directories, read [Transfer Mechanism](transfer-mechanism.md)
and prepare one helper plan containing expected W and all accepted outputs. When W=B, use accepted
S files directly; for overlap, supply the prepared combined outputs. The helper freezes the whole
plan and readable external backups before application. Prepare that batch proactively instead of
driving per-file subprocesses through Agent calls.

The Agent owns task attribution, B/S/W reasoning, semantics and verification. The helper owns its
narrower admitted inputs, capability checks and guarded writes. Return unsupported cases to their
implementation owner, or use another authorized mechanism proving the same whole-plan preparation
and preservation, including absence, types, modes, aliases and symlink ancestors. A capability
rejection does not authorize bypassing its boundary. Failed preparation leaves target working files
untouched, though external preparation artifacts may need retention and accounting.

## Apply with preservation evidence

Coordinate writers and apply the prepared batch once, using its entry, path and exit guards and
persistent write record. Reuse source, target HEAD/index and output proofs rather than repeating
whole-repository checks for each child. Changed dependencies or drift need fresh observations.
Partial writes, missing responses and drift require inspection of the original receipt and
[partial-transfer recovery](transfer-mechanism.md#partial-file-transfer) before continuing. Cooperative
concurrency and detected drift do not make multi-file writes atomic or exclude arbitrary concurrent
writers.

Run relevant non-mutating verification on the combined target. Reuse valid checks and refresh those
whose inputs changed. Formatting, fixing or generation is a separate effect needing express
authority. Combine helper proof with bounded evidence for concrete outside dependencies to prove
preservation. If verification fails after full application, retain the reviewable combined target,
source and backup with the failure; do not roll it back to erase that result.

Outcome proof includes preservation, required verification, exact source/target/backup locations and
the next review or acceptance action. Retain the source worktree, branch, snapshot, backup and
required recovery items until the user accepts the transfer. Any delegated acceptance must trace to
the user's authority; owning cleanup does not confer acceptance authority. Before acceptance,
cleanup means retention. Afterward, removal still follows existing cleanup authority and lifecycle
conditions. Identical changes already present at the target do not turn this handoff into delivery.
