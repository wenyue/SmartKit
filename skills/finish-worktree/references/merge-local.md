# Merge Locally

Integrate by advancing the exact authorized local target branch with one fast-forward.

1. Recheck the target identity, expected `HEAD`, complete local-state snapshot, `history_result`,
   delivery head and tree, ancestry, and grant. Prove the operation preserves every unrelated
   item. Target movement after the History Result does not re-enter history finalization: reprove
   **Already Delivered** when possible, otherwise retain the result and stop for the
   target-movement owner with a stopped `outcome_result`. Unsafe overlap stops and may identify
   `return-for-review` as a new decision, never an automatic substitute.
2. For **Already Delivered**, mutate nothing and reprove the accepted result on the current target.
   Otherwise create an authorized unique recovery ref at the exact old target head with an
   expected-absent update as one logical attempt and re-observe it. Only after that attempt is
   proven, run one fast-forward logical attempt from the target checkout:

   ```text
   git merge --ff-only <exact-delivery-head>
   ```

   Use the immutable commit ID, not a branch name.
3. Prove the target branch now points to the delivery head, its tree is the reviewed delivery tree,
   required verification passes on that target, and every unrelated index, working-tree,
   untracked, and ignored item matches the snapshot.

After every recovery-ref or fast-forward attempt return or interruption, census its complete effect
envelope. A prerequisite, guard, expected-absent, or expected-old rejection proven effect-free
freezes stopped `outcome_result`. An occurred or ambiguous effect, or failed required post-effect
proof, freezes failed `outcome_result`. Preserve completed recovery, the ledger, observed target
state, `history_result`, and the exact recovery or verification owner/action; never automatically
roll back or retry.

A proven result freezes an authoritative-delivery `outcome_result` and returns to **Close from
proof**.
