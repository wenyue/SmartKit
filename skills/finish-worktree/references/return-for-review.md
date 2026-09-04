# Return for Review

Materialize the accepted result in the target working tree while preserving target `HEAD` and every
index entry exactly. This is a non-integrating handoff.

1. Recheck target identity and derive the exact transfer write set from the difference between the
   proven target boundary and delivery tree. If **Already Delivered** leaves no accepted effect to
   return, reprove that authoritative result and end the outcome immediately: preserve the target,
   create no backup or manifest, perform no transfer, and enter no recovery step. Otherwise capture
   scoped read-only preflight evidence: `HEAD`; exact index entries and blob OIDs for write-set paths;
   and their non-index status, file type, mode, applicable symlink target, and content hash. Use
   bounded identity and status evidence to place every other item outside the write set and detect
   unexpected effects.
2. Before writing, create an authorized external backup and manifest for every path the transfer
   could touch as one logical backup attempt, including absence, file type, symlink target, mode,
   and bytes. Prove that attempt complete, readable, and outside every affected worktree.
3. Classify every path. For a scope path without target-local change, validate the complete
   worktree-only patch. For overlapping text, build a three-way candidate in temporary files from
   the merge-base version, current target working file, and accepted result. Stop before an unsafe
   write for a delete/modify conflict, complex rename, binary overlap, incompatible file type or
   mode, mutually exclusive behavior, ambiguous generated output, or any result accepted evidence
   cannot determine. Regenerate only through an explicitly authorized deterministic owner procedure.
4. Once every path is unambiguous, apply the complete worktree-only transfer without staging as one
   guarded-batch logical attempt. Per-path writes are child effects. A shared pathname is overlap,
   not by itself evidence of conflict.
5. Run the required non-mutating verification in the target. A formatter, fixer, generator, or
   dependency updater is a separate mutation and requires its own authority and proof.
6. Prove target `HEAD` and the write-set index entries are unchanged, every affected path contains
   the accepted change plus every compatible local change, and bounded Git identity and status
   evidence shows no unexpected effect outside the write set. Returned changes remain unstaged or
   untracked.
7. Retain the source branch and worktree, history recovery refs, and external backup until the result
   owner accepts the working-tree handoff. Freeze `outcome_result: proven` as a non-integrating
   handoff and return each exact location and the next review action.

After a partial or failed batch transfer, restore only this run's exact writes from backup, only when
the written set is completely observed and no intervening edit would be overwritten, and only as a
separately authorized restore attempt. An ambiguous write set or unsafe restore retains the exact
current target and backup. If the batch completed but post-transfer verification or proof fails,
retain that reviewable target and backup; do not restore it. A successful transfer and proof enters
no recovery path. Classify the outcome under the top-level phase states and record any later restore
without replacing the causal status. Never retry an ambiguous attempt, move target `HEAD`, alter the
index, or reset unrelated state.
