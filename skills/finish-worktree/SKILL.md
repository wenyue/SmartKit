---
name: finish-worktree
description: Finalize or hand off one reviewed isolated linked Git worktree by integrating it locally, creating a pull request, keeping it, or returning it for review; also handle an explicit request to discard one exact isolated worktree and its local state. A pull request is a non-integrating handoff, not delivery.
---

# Finish Worktree

Close one isolated-worktree job from current evidence. The implementation workflow owns scope,
verification, and formal review; this Skill owns history finalization, the selected outcome,
recovery, and authorized cleanup. It does not own tracker transitions or adapt the accepted result.

## Use one effect and result vocabulary

One **logical effect attempt** is the smallest authorized mutation unit whose child operations
share one retry or recovery decision. Give that parent one identity and pre-state. Commands or
per-path writes inherit the parent identity, have no independent retry identity, and appear only in
its ledger as completed, skipped, in-flight, ambiguous, or residual child effects. A child becomes
another logical attempt only when the selected branch contract explicitly gives it a separate
retry or recovery decision. Never split a helper into per-command attempts or a guarded batch into
per-file attempts.

Every exit returns `history_result`, `outcome_result`, and `cleanup_result`. Each phase result uses
the smallest applicable state:

- `not-started`: the phase was not entered; name the causal earlier boundary;
- `inapplicable`: the fixed contract proves the phase does not apply;
- `stopped`: a prerequisite or guard rejects the intended effect and a complete post-census proves
  the logical attempt effect-free; record the reason, ledger, residual evidence, and next owner; or
- `failed`: an effect occurred or remains ambiguous, or required post-effect proof failed; record
  the causal attempt identity, ledger, residual state, and recovery owner. This state excludes a
  prerequisite or guard rejection proven effect-free.

Only history and outcome add `proven`; only cleanup adds `complete`. Their positive payloads remain
defined at the phase that proves them. **`preflight`** is a causal boundary, not a fourth phase. In
finalization, a stop before Ready returns all three phases `not-started` and
`causal_boundary: preflight`, recording the rejected prerequisite or guard, proof that no phase
effect occurred, and the exact next owner/action. Explicit discard instead always uses history
`inapplicable`; before its first effect, outcome and cleanup remain `not-started`. Either preflight
boundary directly derives overall `stopped`. A failed history attempt returns failed
`history_result` and later phases `not-started`.

Overall `status` is `complete` only when `outcome_result` is proven and `cleanup_result` gives
every lifecycle item an authorized disposition. A preflight rejection is `stopped`. After a phase
starts, overall status copies its causal `stopped` or `failed` phase state; a later recovery records
its own result without replacing that cause.

Classification is `no positive result` until a history or outcome fact is proven. A proven explicit
discard is `explicit discard`. Finalization preserves its strongest independently proven fact:
`history finalized`, `authoritative delivery`, or `non-integrating handoff`. A later stop or failure
adds its partial or unproven effect without erasing or upgrading that fact. Only proven local
integration or **Already Delivered** is `authoritative delivery`.

Every return includes the selected route contract, `status`, `classification`, `causal_boundary`,
all three phase results, applicable source, target, reviewed, delivery, and final heads and trees,
verification and review evidence, publication, preserved unrelated state, exact residual state,
and `next_owner` with one exact action. Finalization also includes its fixed contract and history
policy. A stopped or failed return names the causal phase and attempt, mismatch or error, and
recovery route. Preserve recovery after partial, failed, or ambiguous effects.

An explicit request to discard exact local state now takes the separate destructive route in
[`references/discard.md`](references/discard.md) and ends there. Otherwise follow this contract.

Select exactly one outcome and read only its reference completely now:

| Outcome | Selected contract | Classification |
| --- | --- | --- |
| `merge-locally` | [`references/merge-local.md`](references/merge-local.md) | integrating |
| `create-pull-request` | [`references/create-pull-request.md`](references/create-pull-request.md) | non-integrating until the authoritative target contains the result |
| `keep-for-later` | [`references/keep-for-later.md`](references/keep-for-later.md) | non-integrating |
| `return-for-review` | [`references/return-for-review.md`](references/return-for-review.md) | non-integrating |

Load for preflight only and freeze that selected contract for the run; unselected references remain
unloaded. Its complete inputs, grants, success proof, recovery, retention, and effect boundaries
must enter the common contract before Ready. Execute no branch step yet; later execution uses this
same frozen branch contract.

## Fix the finalization contract

Require one exact source worktree, target, and authorized outcome. Bind:

- the source path and branch; its originating `create-worktree` ready handoff as lifecycle
  provenance; either an uninterrupted, attributable implementation-owner handoff from that ready
  state or, after any execution, identity, control, or evidence gap, a fresh Reuse `ready` handoff;
  and the current expected `HEAD`, tree, index, local state, creation and cleanup owners, immutable
  base, and complete scope-owned commit range;
- the target checkout and branch, expected `HEAD`, boundary relationship, allowed response to
  movement, and every preserved staged, unstaged, untracked, ignored, file-type, mode, and symlink
  item;
- the acceptance sources and fixed point; required verification and formal `code-review` result;
  their exact reviewed `HEAD` and tree; and absence of blocking findings;
- `preserve-commits` or `consolidate-checkpoints`; exactly one outcome—`merge-locally`,
  `create-pull-request`, `keep-for-later`, or `return-for-review`—and every value, grant,
  prerequisite, observable success, recovery, and retention requirement from its selected
  contract;
- publication evidence, recovery-ref ownership and retention, lifecycle and effect grants, one
  identity for each logical effect attempt, cleanup authority including any workflow-owned
  auxiliary file, next owner, and every outcome-specific value; and
- the authoritative implementation workflow and the observable unavailable, stopped, failed, or
  ambiguous result of each dependency.

Caller assertions are inputs to prove. Re-observe Git, repository, and explicitly authorized host
evidence. Resolve both physical paths, common repository, worktree registrations, branches,
commits, trees, refs, publication, and lifecycle owners. An uninterrupted handoff must account
causally for every mutation from the originating ready-state recheck through the reviewed fixed
point and prove the implementation owner quiescent. Otherwise require and recheck the fresh Reuse
handoff. Independently recheck either current-state route against the observed source; an
unavailable, non-ready, stale, substituted, detached, or multiply identified source stops
finalization.

Snapshot every affected checkout, including ignored items and their file types, modes, symlink
targets, and bytes, and account for every commit and path in the range. Classify each local-state
item as scope-owned, unrelated, or ambiguous. Prove the base and target boundary are ancestors
where the selected history policy requires it. Bind verification and formal review to the same
acceptance fixed point, reviewed head, and reviewed tree. Missing evidence, a blocking finding,
unsafe overlap, incomplete publication knowledge needed by an operation, or ambiguous ownership
stops before mutation and returns the exact dependency or decision owner.

The source must be clean under the repository's history-mutation predicate; ignored source items
remain inventoried preservation and lifecycle state. A dirty target is eligible only when the
selected outcome can preserve every unrelated item byte-for-byte and index-for-index. Record
commands, outputs, and object IDs sufficient for independent recheck.

**Ready when:** the complete common and selected outcome contracts, current identities, accepted
range, review binding, preservation boundary, authorities, and outcome inputs are exact and
mutually consistent. No history or outcome mutation precedes this gate.

## Finalize the reviewed history

Immediately before each logical effect attempt, recheck every identity, head, tree, range,
local-state, publication, authority, and recovery predicate required by its complete child-effect
envelope. Bind the parent phase, attempt identity, pre-state, and intended envelope once. After its
return or interruption, census that whole envelope once into the parent ledger. Drift stops. An
interrupted or ambiguous attempt remains in-flight: retain its state and route it to the effect
owner rather than retargeting or retrying it.

If the target moved, continue only when the contract permits rebinding, the new target remains an
ancestor of the reviewed head, and the recomputed range is wholly scope-owned. Otherwise return the
observed target and reviewed state to the implementation workflow or other frozen target-movement
owner. Any synchronization or other content change belongs to that owner and requires verification
and formal review before a new finalization attempt; this Skill does not perform it.

Before rewriting history, test whether the authoritative outcome target already contains every
accepted effect. Current ancestry is sufficient when it proves the exact range. Otherwise require
unambiguous equivalent-change evidence for every effect and evidence that the exact target `HEAD`
and tree passed required verification and blocker-free formal review. Consume that bound evidence
from the implementation owner or return the target state to that owner; this Skill does not perform
the review. An empty diff, similar message, moved tracker state, partial patch, or proof bound to a
different target identity is insufficient. Record a successful proof as **Already Delivered** and
perform no empty history or delivery mutation.

Apply the fixed history policy:

- **Preserve commits:** re-enumerate `target..reviewed-head`; prove the whole range scope-owned and
  the source still at the reviewed head and tree. That head is the delivery head. Published commits
  are eligible only when their observed publication and the selected outcome are compatible.
- **Consolidate checkpoints:** require the whole range to be unpublished and unrelied-upon, with
  the exact target as its ancestor. Resolve and freeze one interpreter executable from the
  project's supported-runtime evidence, proving both version compatibility and ability to run the
  helper; absence stops before any preparation effect. Freeze an expected-absent unique recovery
  ref and its derived `<recovery-ref>-candidate` ref, including the helper's exact create, retain,
  and expected-old-value delete grants. Also freeze an expected-absent message-file path outside
  every affected worktree, its repository-conforming bytes and mode derived from the accepted
  implementation scope, and exact create, read, retention, deletion, and cleanup ownership. Create
  that file once as its own logical history attempt and prove its exact contents before invoking
  the package script once:

  ```text
  <compatible-interpreter> <skill-root>/scripts/consolidate_worktree_history.py \
    --repository <source-worktree> \
    --target <exact-target-oid> \
    --message-file <message-file> \
    --recovery-ref <new-recovery-ref>
  ```

  The helper invocation is one parent logical attempt; its internal Git operations are child
  effects. Treat its aggregate JSON as attempt evidence, not an effect ledger or proof. After every
  return or interruption, independently census the checkout, branch, commits, trees, and refs to
  produce the parent effect ledger. On success, prove one new commit whose sole parent is the exact
  target, whose tree is byte-identical to the reviewed tree, whose branch is the source branch, and
  whose checkout is clean; retain the recovery ref at the reviewed checkpoint head. On error,
  preserve all state, including the message file and any reported `-candidate` ref, and establish
  the exact current checkout and branch. Freeze stopped `history_result` only when a prerequisite,
  guard, or expected-absent rejection is proven effect-free by that census; freeze failed
  `history_result`
  when an effect occurred or remains ambiguous, or required post-effect proof failed. Leave later
  phase results `not-started`, retain the ledger and exact recovery owner/action, and never retry.

Freeze the completed phase as immutable **`history_result: proven`** bound to the history policy,
target boundary, reviewed head and tree, resulting source head and tree, delivery head or **Already
Delivered** proof, recovery refs, message-file disposition, and effect ledger. This closes history
finalization for the attempt. No later outcome may re-enter or repeat the history policy. In
particular, target drift after proven `history_result` stops the current attempt before another
mutation unless current evidence proves **Already Delivered**. Retain `history_result` and hand it
to the target-movement owner. Any later synchronization is a new implementation state that must be
verified and formally reviewed; it cannot resume this attempt or reuse its proof.

No history policy permits pull, stash, hard reset, clean, force push, rebase, a merge commit, an
implicit remote action, or replacement of unrelated state. A `history_result` is either one proven
delivery head and tree or **Already Delivered** evidence; otherwise no outcome begins.

## Execute one outcome

Execute the selected contract frozen before Ready against immutable `history_result`; do not
reread, substitute, or discover new prerequisites after history finalization. Freeze its terminal
**`outcome_result`** with the outcome, proven or retained classification, active terminal step,
attempt ledger, publication, recovery, and residual state. A stopped or failed outcome retains
`history_result` rather than replacing it.

Only independently proven integration into the authoritative target, including **Already
Delivered**, is delivery. A push, pull request, retained branch, or working-tree transfer is a
non-integrating handoff and must not be reported as delivery.

## Close from proof

After the outcome, re-observe its exact effect, both checkouts, refs, publication, and unrelated
state. Cleanup is eligible only after outcome-specific proof and proof that the exact worktree,
branch, and recovery item are owned by this lifecycle, contain no user or unrelated work, and are
covered by an exact cleanup grant. The census includes ignored state and every workflow-owned
auxiliary file. A host removes a host-created worktree. Delete any owned ref, including a branch or
recovery ref, only after its retention owner releases it and through an expected-old-OID
compare-and-swap; a mismatch retains the ref. Before branch deletion also prove it is absent from
every worktree. Each worktree removal, auxiliary-file removal, and ref deletion is one logical
cleanup attempt. Retention or host handoff is the cleanup disposition when removal is not owned
here.

Freeze **`cleanup_result`** with eligibility, every removed, retained, or delegated item, its
attempt ledger, residual state, and owner. It never rewrites `history_result` or `outcome_result`.

Never call an unproven delivery, cleanup, publication, pull request, or non-integrating handoff
complete.
