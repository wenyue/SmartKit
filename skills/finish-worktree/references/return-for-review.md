# Transfer Back to a Checkout

The public route remains `return-for-review` for established callers. Its effect is a working-file
transfer, useful before or after review: bring accepted task changes into one target checkout while
preserving that checkout's HEAD and complete index exactly. Existing staged content stays staged;
transferred changes affect working files only. This is always a non-integrating handoff.

## Freeze the three inputs

Identify the target checkout and accepted task scope. Establish **B**, the immutable shared baseline
from which the task changes are measured; **S**, a frozen snapshot of the accepted task result; and
**W**, the target's actual working files at preparation time. Pin B by commit/tree OID and S by exact
file bytes, absence, types and modes. S may include attributable staged, unstaged and untracked task
work without making a commit or changing the source index. Resolve layered edits to their accepted
final contents; ambiguous ownership stops. Exclude unrelated source work from S.

Transfer only the task difference **B → S**. W is not the target HEAD or index version: it includes
committed target evolution and the user's local changes. Never copy the whole source checkout, and
never use the destination's current HEAD as B merely because it is convenient. If there is no
unambiguous shared baseline or accepted source snapshot, retain both sides and return that decision
to the result owner. Formal review is needed only when independently required by project/caller
policy or an expressly selected history operation.

## Prepare the entire result before writing

Derive the exact affected paths from B → S, including both ends of any supported rename. Use
bounded evidence for those paths and their ancestors, with complete target HEAD/index evidence at
batch boundaries. Existing evidence for immutable B and accepted S remains usable while its
dependencies match. Inspect unrelated paths only when a concrete preservation risk reaches them;
ordinary transfer needs no repeated global status, untracked or ignored inventory.

Prepare the accepted combined result in one local batch. Where W equals B, S is the result: a
three-way merge adds no information. Preserve target-only changes and include identical edits once.
For overlapping ordinary text, use native three-way merging with B as ancestor, W as local and S
as incoming input, such as `git merge-file -p` on temporary files. Inspect semantic compatibility
and verify the combined behavior even when Git reports no textual conflict. Conflicting hunks,
delete/modify, complex renames, binary overlap, unsupported types/modes, incompatible behavior and
ambiguous generated output stop before target writes. Regeneration keeps its deterministic owner
and needs accepted authority.

Use the [batch transfer helper](recovery.md#batch-transfer-mechanism) for ordinary file
create/update/delete operations in existing directories. Give it one accepted-output plan, including
expected W and output states. For the simple W=B case, that plan can refer directly to accepted S
files; for overlap, provide the prepared combined outputs. The helper freezes every output and a
readable backup outside affected worktrees before applying anything. It gathers deterministic facts
and performs bounded mechanics; the Agent owns task attribution, B/S/W reasoning, semantics and
needed verification. Prepare a whole plan, rather than driving one subprocess per file through
Agent tool calls.

Keep unsupported transfers with their owning implementation workflow. A different authorized
mechanism must establish the same complete preparation and preservation contract, including absence,
types, modes, aliases and symlink ancestors; the helper's support limit is not permission to improvise
an unsafe write. Failed preparation leaves target working files untouched.

## Apply with preservation evidence

Coordinate with other writers, then apply the prepared batch once. The helper checks accepted S,
target identity, HEAD and complete index at entry; inside the batch it guards only each related path,
ancestor and output. It records writes durably and checks the resulting paths and unchanged HEAD/index
at exit. Reuse this proof instead of repeating whole-repository checks around each child operation.
Additional observation follows actual drift or a dependency changed by another effect.

There is no portable atomic multi-file filesystem guarantee. The procedure protects against
cooperative concurrency and detected drift, not arbitrary simultaneous writers. Partial writes,
missing responses and observed drift use [recovery](recovery.md#partial-file-transfer); inspect the
original receipt before choosing continuation. A shared pathname alone is not a conflict, and a
clean textual merge alone is not semantic proof.

Run relevant non-mutating verification on the combined target. Reuse still-valid checks; renew those
whose inputs changed. A formatter, fixer or generator is a separate effect outside this transfer
unless expressly authorized. Complete index preservation keeps existing staged content staged;
the transfer itself changes working files only. Use the helper's output proof and bounded evidence
for concrete outside dependencies to establish preservation. If later verification fails, retain
the reviewable target, source and backup with that failure; do not roll back a completed transfer.

A proven transfer returns `outcome_result: proven`, `classification: non-integrating handoff`, and
the exact source, target and backup locations with the next review/acceptance action. Keep the source
worktree, branch, snapshot, backup and required recovery items until the user accepts this transfer.
Delegated acceptance must be traceable to the user's authority; a lifecycle owner cannot accept on
the user's behalf merely by owning cleanup. Until acceptance, the cleanup disposition is retention;
afterward, existing cleanup authority and lifecycle conditions still apply. No working-file transfer
proves delivery, even when the target already had identical changes.
