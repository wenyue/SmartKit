# Transfer Back to a Checkout

The public route `return-for-review` transfers accepted task changes into one target checkout's
working files, before or after review, while preserving its HEAD and complete index exactly.
Existing staged content stays staged. This is always a non-integrating handoff.

## Freeze the three inputs

Identify the target and accepted task scope. Establish **B**, the immutable shared baseline from
which task changes are measured; **S**, the frozen accepted task result; and **W**, the target's
actual working files at preparation time. Pin B by commit/tree OID and S by exact bytes, absence,
types and modes. S may include attributable staged, unstaged and untracked work without a commit or
source-index change. Resolve layered edits to accepted final contents, exclude unrelated source
work, and stop on ambiguous ownership.

Transfer only **B → S**. W includes committed target evolution and local changes; it is not the HEAD
or index version. Never copy the whole checkout or choose the destination's current HEAD as B for
convenience. If B or S is ambiguous, retain both sides and return the decision to the result owner.
Formal review is required only by independently applicable project/caller policy or an expressly
selected history operation.

## Prepare the entire result before writing

Derive all affected paths from B → S, including both ends of supported renames. Capture bounded path
and ancestor evidence with complete target HEAD/index evidence at batch boundaries. Reuse immutable
B and accepted S evidence while dependencies match. Inspect unrelated paths only for a concrete
preservation risk; ordinary transfer needs no repeated global status, untracked or ignored
inventory.

Prepare one accepted combined result. Where W=B, use S directly. Preserve target-only changes and
include identical edits once. For overlapping ordinary text, use native three-way merging with B as
ancestor, W as local and S as incoming, such as `git merge-file -p` on temporary files. Inspect
semantic compatibility and verify combined behavior even without textual conflicts. Conflicting
hunks, delete/modify, complex renames, binary overlap, unsupported types/modes, incompatible
behavior or ambiguous generated output stop before target writes. Regeneration retains its
deterministic owner and requires accepted authority.

For regular-file create/update/delete in existing directories, read the [transfer
mechanism](transfer-mechanism.md) and prepare one helper plan with expected W and accepted outputs.
Use accepted S files directly for W=B; supply prepared combined outputs for overlap. The helper
freezes all outputs and readable external backups before applying anything. Prepare the whole plan
proactively, without driving per-file subprocesses through Agent calls. The Agent owns task
attribution, B/S/W reasoning, semantics and verification; helpers own guarded mechanics.

Return unsupported transfers to their implementation owner. Another authorized mechanism must prove
the same whole-plan preparation and preservation, including absence, types, modes, aliases and
symlink ancestors. A helper capability rejection grants no authority to bypass that boundary. Failed
preparation leaves target working files untouched.

## Apply with preservation evidence

Coordinate with other writers, then apply the prepared batch once under the mechanism's entry, path
and exit guards and persistent write record. Reuse its source, target HEAD/index and output proofs
instead of repeating whole-repository checks per child; re-observe on drift or a changed dependency.
Partial writes, missing responses and drift require original-receipt inspection and
[partial-transfer recovery](transfer-mechanism.md#partial-file-transfer) before continuation. The
mechanism handles cooperative concurrency and detected drift; it cannot promise portable atomic
multi-file writes or protection from arbitrary simultaneous writers.

Run relevant non-mutating verification on the combined target, reusing valid checks and renewing
those whose inputs changed. A formatter, fixer or generator is a separate effect requiring express
authority. Combine helper output proof with bounded evidence of concrete outside dependencies to
prove preservation. If verification fails after full application, retain the reviewable target,
source and backup with that failure; a completed transfer is not rolled back to erase the result.

Proven transfer includes preservation and required verification, the exact source, target and backup
locations, and the next review/acceptance action. Keep the source worktree, branch, snapshot, backup
and required recovery items until the user accepts the transfer. Delegated acceptance must trace to
the user's authority; cleanup ownership alone grants no acceptance authority. Until acceptance,
cleanup is retention; afterward, existing cleanup authority and lifecycle conditions still apply.
Even a target that already contained identical changes does not turn this handoff into delivery.
