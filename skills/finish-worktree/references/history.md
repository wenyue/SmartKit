# History Preparation

Bind publication, integration or expressly selected consolidation to one accepted scope, immutable
base, source branch and HEAD/tree, complete task-owned commit range and destination boundary.
Preserve commits by default. Consolidation requires an explicit user request or applicable project
requirement; history preparation cannot silently synchronize divergence or change accepted content.

## Consume accepted-state evidence

Required checks must pass; ordinarily blocker-free formal review must cover the exact accepted
HEAD/tree. An alternative is valid only when explicitly authorized by the implementation
owner's contract and supplied by that owner: complete original review reports with their immutable
inputs, dispositions for every finding, the bounded authorized repair delta, and owner verification
covering that delta and closure of every blocking finding on the exact final HEAD/tree. This is
owner acceptance, not a new formal reviewer verdict. Retain the original reviewed state and reports
without relabeling them as review of the repaired state.

Finalization consumes this evidence without conducting formal review. Missing or invalid evidence,
unresolved blockers or task work outside the accepted commit returns to the implementation owner
under its repair and review limits. Unrelated local state may remain when the selected operation
cannot affect it and preservation can be proved.

## Already Delivered

Before rewriting or delivering, check whether the authoritative target already contains every
accepted effect. Ancestry suffices when it proves the exact accepted range. Otherwise require
unambiguous equivalent-change evidence covering every effect and accepted-state evidence bound to
that exact target HEAD/tree. Consume this proof from the implementation owner or return the current
target there. An empty diff, similar message, tracker state, partial patch, PR or retained branch
alone cannot prove delivery.

Proven **Already Delivered** avoids rewriting, push and integration. Preserve its authoritative
target identity and evidence in the history and outcome results.

## Preserve commits

Account for every commit in the accepted range against the frozen boundary. Prove the source remains
at the HEAD/tree bound by accepted-state evidence: that HEAD is the delivery commit and proves
history without mutation. Published commits are eligible when the selected outcome is compatible
with their observed publication. Retain local state outside the accepted result and effect boundary.

## Consolidate checkpoints

Require a clean source under `git status --porcelain=v1 -z`, a wholly task-owned range whose exact
target is an ancestor, and evidence that the range is unpublished and unrelied-upon. Establish
commit authority and normal repository hooks. Probe `python
"<skill-root>/scripts/consolidate_worktree_history.py" --help` before preparation; probe failure
stops without a history effect.

Prepare an owned commit-message file outside affected worktrees. Reserve an expected-absent unique
ref under `refs/smartkit/recovery/` and its derived `<recovery-ref>-candidate` ref. Record their
exact create/retain/delete authority, expected values, message bytes and lifecycle owner in the
external [operation receipt](recovery.md#operation-receipt). Create the message once and verify it
before use.

```text
python "<skill-root>/scripts/consolidate_worktree_history.py" --repository "<source-worktree>" --target "<exact-target-oid>" --message-file "<external-message-file>" --recovery-ref "<new-recovery-ref>"
```

The helper runs a normal commit with hooks, preserves the checkpoint under the recovery ref and
checks that the new commit has the target as sole parent and the accepted tree unchanged. Its
internal Git operations form one history attempt; its JSON is evidence to recheck.

After success, independently prove the source HEAD and branch, sole parent, identical tree, clean
checkout and retained recovery ref. Carry accepted-state evidence through the identical tree and
unchanged accepted diff, retaining original input identities; rerun checks dependent on commit
identity or hooks. A hook change to the tree invalidates the binding and returns to the
implementation owner under **Consume accepted-state evidence**.

After failure, inspect the checkout, branch, index, working files and both recovery refs. The helper
may restore its controlled checkout state when guards hold; otherwise it retains partial state.
Creating a recovery ref is already an effect even if a hook rejects the commit. Retain candidates,
message and receipt for their owner and use [effect recovery](recovery.md) before any continuation.

## Preserve the result

Record proven history with its policy, base and target boundary, accepted-state evidence, delivery
HEAD/tree or Already Delivered proof, and recovery items. Later target movement or outcome failure
cannot replace it. Continue only an outcome whose dependencies still match. Otherwise return the
observed state to the implementation/target-movement owner for synchronization and acceptance under
**Consume accepted-state evidence**. A new accepted state does not rewrite the proven history
record.
