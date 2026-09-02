# Return for Review

Materialize the accepted result in the target working tree while leaving target `HEAD` and every
index entry unchanged. This is a non-integrating handoff.

1. Recheck the target identity and snapshot its `HEAD`, complete index entries, staged and unstaged
   changes, untracked paths, file types, modes, and bytes. Derive the transfer from the exact diff
   between the proven target boundary and delivery tree. If **Already Delivered** leaves no accepted
   scope effect to return, preserve the target unchanged. This branch terminates the outcome
   immediately: return the authoritative **Already Delivered** result and evidence; create no backup
   or manifest, perform no transfer, and enter no later transfer or recovery step.
2. Before writing, create an authorized external backup and manifest for every path the transfer
   could touch as one logical backup attempt, including absence, file type, symlink target, mode,
   and bytes. Prove that attempt complete, readable, and outside every affected worktree.
3. Classify paths. For a scope path without target-local change, validate the complete worktree-only
   patch. For overlapping text, construct a three-way candidate in temporary files from the
   merge-base version, current target working file, and accepted result. After every path is
   unambiguous, apply the complete worktree-only transfer without staging as one guarded batch
   logical attempt; its per-path writes are child effects, not separate attempts. A shared pathname
   alone is overlap, not evidence of conflict.
4. Stop before an unsafe write on delete/modify conflict, complex rename, binary overlap,
   incompatible file type or mode, mutually exclusive behavior, ambiguous generated output, or a
   result that accepted evidence cannot determine. Regenerate only through an explicitly authorized
   deterministic owner procedure.
5. Run the required non-mutating verification in the target. A formatter, fixer, generator, or
   dependency updater is a separate mutation and requires its own authority and proof.
6. Prove target `HEAD` and every index entry are unchanged; unrelated local state matches the
   snapshot; and each returned scope path contains the accepted change plus every compatible local
   change. Returned changes remain unstaged or untracked.
7. Retain the source branch/worktree, history recovery refs, and external backup until the result
   owner accepts the working-tree handoff. Freeze the proven `outcome_result` as a non-integrating
   handoff and return their exact locations and the next review action.

If transfer fails before a complete candidate exists, restore only this run's writes from the
backup, only after proving no intervening edit would be overwritten, as one separately authorized
restore attempt. Otherwise retain the exact current target and backup. A stop before the batch
transfer freezes a stopped `outcome_result`; a transfer mutation, failed proof, or ambiguous effect
freezes a failed one. Record any later restore result without replacing that causal status. A
post-transfer verification failure leaves the reviewable result and recovery intact without
classifying it as a proven handoff. Never retry an ambiguous attempt, move target `HEAD`, alter the
index, or reset unrelated state.
