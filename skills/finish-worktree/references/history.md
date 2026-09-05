# History Preparation

Use this reference for publication or integration, and whenever consolidation is expressly selected.
Bind the accepted scope and immutable base, source branch and HEAD/tree, complete task-owned commit
range, destination boundary, required verification, and blocker-free formal review. The
implementation workflow owns that evidence. Missing review or task work outside the accepted commit
returns there before delivery; unrelated local state may remain only when the selected operation
cannot affect it and its preservation can be proved.

Preserve commits by default. Consolidate checkpoints only on an explicit user request or applicable
project requirement. A choice of outcome alone never requests rewriting history. History preparation
cannot silently synchronize a divergent target or change reviewed content.

## Already Delivered

Before rewriting or delivering, check whether the authoritative target already contains every
accepted effect. Ancestry suffices when it proves the exact accepted range. Otherwise require
unambiguous equivalent-change evidence covering every effect, plus required verification and
blocker-free formal review bound to that exact target HEAD/tree. Consume that proof from the
implementation owner or return the current target there. An empty diff, similar message, tracker
state or partial patch does not prove delivery.

A proven **Already Delivered** result avoids needless rewriting, push or integration. Preserve its
authoritative target identity and evidence in the history and outcome results. A PR or retained
branch alone cannot provide this proof.

## Preserve commits

Enumerate the accepted range against the frozen boundary and account for every commit. Prove the
source remains at the verified/reviewed HEAD and tree. That exact HEAD is the delivery commit;
record `history_result: proven` without a history mutation. Published commits are eligible when the
selected outcome is compatible with their observed publication. Retain local state outside the
accepted result and selected effect boundary.

## Consolidate checkpoints

Require a clean source under `git status --porcelain=v1 -z`, a wholly task-owned range whose exact
target is an ancestor, and evidence that the range is unpublished and unrelied-upon. Establish the
commit authority and normal repository hooks. Probe the appropriate launcher with `--help` before
preparation. Both launchers check only `python3`, then `python`, selecting Python 3.10+; when neither
qualifies they report that requirement once and exit 2 without a history effect.

Prepare an owned commit-message file outside affected worktrees. Reserve an expected-absent unique
ref under `refs/smartkit/recovery/` and its derived `<recovery-ref>-candidate` ref. Record their exact
create/retain/delete authority, expected values, message bytes and lifecycle owner in the external
[operation receipt](recovery.md). Create the message once and verify it before the helper invocation.

On POSIX, invoke:

```sh
sh "<skill-root>/scripts/consolidate_worktree_history.sh"   --repository <source-worktree> --target <exact-target-oid>   --message-file <external-message-file> --recovery-ref <new-recovery-ref>
```

Use `scripts/consolidate_worktree_history.ps1` with the same arguments on PowerShell. The helper's
normal commit runs hooks, preserves the checkpoint under the recovery ref, and checks that the new
commit has the target as sole parent and the reviewed tree unchanged. Its internal Git operations
belong to one history attempt. Its JSON is evidence to recheck, not an authoritative phase result.

After success, independently prove the new source HEAD, branch, sole parent, identical tree, clean
checkout and retained recovery ref. Bind the original review to the identical resulting tree and
unchanged accepted diff; rerun checks whose validity depends on commit identity or hooks. A hook
change to the tree invalidates that binding and returns to implementation.

After failure, inspect the actual checkout, branch, index, working files and both recovery refs.
The helper may restore its controlled checkout state when its guards hold; it otherwise retains the
partial state. A created recovery ref is already an effect, even if the commit hook rejected the
commit. Preserve candidates, message and receipt until their owner resolves the attempt. Follow
[recovery](recovery.md), rather than invoking the helper again from its original arguments.

## Preserve the result

Freeze `history_result: proven` with policy, base and target boundary, reviewed HEAD/tree, delivery
HEAD/tree or Already Delivered proof, and recovery items. Later target movement or outcome failure
cannot replace it. Continue only an outcome whose dependencies still match; otherwise return the
observed state to the implementation/target-movement owner for synchronization and renewed
verification/review. That produces a new accepted state, not a rewrite of the proven history record.
