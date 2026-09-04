# Merge Locally

Integrate the reviewed result by advancing one exact authorized local target branch with a single
fast-forward.

1. Recheck the target identity, expected `HEAD`, immutable `history_result`, delivery head and tree,
   ancestry, grant, exact fast-forward paths and refs, Git administrative state, and their scoped
   snapshot. Use bounded identity and status evidence to prove the fast-forward cannot address other
   state and to detect unexpected effects. Target movement after history never re-enters history
   finalization. Reprove **Already Delivered** when possible; otherwise retain `history_result` for
   the target-movement owner and stop with `outcome_result: stopped`. Unsafe overlap also stops. It
   may present `return-for-review` as a new owner decision, never select it automatically.
2. For **Already Delivered**, mutate nothing and reprove the accepted result on the current target.
   Otherwise create an authorized unique recovery ref at the exact old target head through an
   expected-absent update, as one logical attempt, and re-observe it. Only after that attempt is
   proven, run one fast-forward logical attempt from the target checkout:

   ```text
   git merge --ff-only <exact-delivery-head>
   ```

   Use the immutable commit ID, not a branch name.
3. Prove the target branch points to the delivery head, its tree is the reviewed delivery tree,
   required verification passes on that target, every affected path has the expected state, and
   bounded index, working-tree, untracked, and ignored evidence shows no unexpected effect outside
   the fast-forward write set.

After every recovery-ref or fast-forward return or interruption, re-observe all state that the
attempt could affect and classify it under the top-level phase states. Preserve completed recovery,
the ledger, observed target, `history_result`, and the exact recovery or verification owner/action.
Never roll back or retry automatically.

A proven result freezes an authoritative-delivery `outcome_result` and returns to **Close from
proof** in the main Skill.
