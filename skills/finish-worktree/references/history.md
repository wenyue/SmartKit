# History Preparation

Read this contract for publication, integration or expressly selected consolidation. Bind the work
to one accepted scope, immutable base, source branch and HEAD/tree, complete task-owned commit range
and destination boundary. Preserve commits unless the user explicitly requests consolidation or
applicable project policy requires it. Neither policy authorizes synchronizing divergence or
changing accepted content during finalization.

## Establish the accepted state

Required checks must have passed. Ordinarily, blocker-free formal review covers the exact accepted
HEAD/tree. An alternative is available only when the implementation owner's contract explicitly
authorizes it and that owner supplies all of the following together: original review reports and
their immutable inputs, dispositions for every finding, a bounded authorized repair delta, and owner
verification of that delta and closure of every blocking finding on the exact final HEAD/tree.

That alternative is owner acceptance, not a new formal-review verdict. Keep the original reports
and reviewed identities intact; do not relabel them as review of the repaired state. Finalization
consumes either supported evidence route without conducting formal review itself.

Missing or invalid evidence, unresolved blockers, or task work outside the accepted commit returns
to the implementation owner under its repair and review limits. Unrelated local state may remain
when the selected operation cannot affect it and preservation can be proved.

## Already Delivered

Check for delivery before rewriting or delivering again. The authoritative target must already
contain every accepted effect. Ancestry is sufficient when it proves the exact accepted range.
Otherwise require unambiguous equivalent-change evidence for all effects plus accepted-state evidence
bound to the exact target HEAD/tree. Consume that proof from the implementation owner or return
the current target to that owner for acceptance.

An empty diff, a similar commit message, tracker state, a partial patch, a PR or a retained branch
alone does not establish this result. Proven **Already Delivered** avoids rewriting, push and
integration; record the authoritative target identity and proof in both history and outcome results.

## Preserve the accepted commits

Account for every commit in the range against the frozen boundary. When source HEAD/tree still
matches the accepted-state binding, that HEAD is the delivery commit and history is proven without
mutation. Already published commits remain eligible when the selected outcome is compatible with
their observed publication. Retain local state outside the accepted result and effect boundary.

## Consolidate only the authorized range

Consolidation requires a wholly task-owned, unpublished and unrelied-upon range, whose exact target
is an ancestor, and a clean source under `git status --porcelain=v1 -z`. Establish commit authority
and normal repository hooks. Probe the helper before preparation:

```text
python "<skill-root>/scripts/consolidate_worktree_history.py" --help
```

A failed probe stops before a history effect. Prepare an owned message file outside affected
worktrees and reserve a unique, expected-absent ref under `refs/smartkit/recovery/`, together with
its derived `<recovery-ref>-candidate` ref. The external [operation receipt](recovery.md#operation-receipt)
records exact create/retain/delete authority, expected values, message bytes and lifecycle owner.
Create the message once and verify it before use.

```text
python "<skill-root>/scripts/consolidate_worktree_history.py" --repository "<source-worktree>" --target "<exact-target-oid>" --message-file "<external-message-file>" --recovery-ref "<new-recovery-ref>"
```

The helper keeps the checkpoint under the recovery ref and makes a normal commit with hooks. Its
Git operations form one attempt. It checks that the new commit's sole parent is the exact target
and that its tree equals the accepted tree; recheck its JSON against observed repository state.

After success, independently prove source HEAD and branch, sole parent, identical tree, clean
checkout and retained recovery ref. Carry accepted-state evidence through the identical tree and
unchanged accepted diff, keeping original input identities. Rerun checks whose result depends on
commit identity or hooks. A hook that changes the tree breaks the acceptance binding and returns
that state to the implementation owner.

After failure, inspect checkout, branch, index, working files and both recovery refs. Guarded helper
restoration may have restored controlled checkout state; unsafe restoration leaves partial state
retained. Even a hook-rejected commit can follow the effect of creating a recovery ref. Keep
candidates, message and receipt for their owner, and use [Effect Recovery](recovery.md) before
continuing.

## Carry the proof into the outcome

Record history policy, base and target boundary, accepted-state evidence, delivery HEAD/tree or
Already Delivered proof, and recovery items. Later target movement or outcome failure does not
replace this proven record. Continue only while the outcome's dependencies still match. Otherwise
return the observations to the implementation or target-movement owner for synchronization and
acceptance under the evidence contract above. A newly accepted state gets its own binding; it does
not rewrite the earlier proof.
