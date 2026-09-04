---
name: finish-worktree
description: Finalize or hand off one reviewed isolated linked Git worktree by integrating it locally, creating a pull request, keeping it, or returning it for review; or handle an explicit request to discard one exact isolated worktree and its local state.
---

# Finish Worktree

Close one isolated-worktree job from current evidence. The implementation workflow owns scope,
verification, and formal review. This Skill owns history finalization, one selected outcome, its
recovery, and authorized cleanup. Tracker transitions and changes to the accepted result remain
with their established owners.

## Principles

- **One job, one route.** Finalize or explicitly discard one exact isolated worktree through one
  frozen outcome contract.
- **Proof before effect.** Re-establish current identity, ownership, authority, recovery, and the
  complete effect boundary before every mutation.
- **One retry decision per attempt.** Group child operations under the logical effect attempt whose
  owner decides retry or recovery.
- **Strongest fact wins.** Later failure preserves every independently proven history, delivery, or
  handoff fact without upgrading it.
- **Recovery follows causality.** Retain ambiguous or partial state and return it to the owner of the
  effect that created it.

## Public state model

A **logical effect attempt** is the smallest authorized mutation unit whose child operations share
one retry or recovery decision. Give the attempt one identity and pre-state. Record its commands or
per-path writes as completed, skipped, in-flight, ambiguous, or residual child effects. A child is a
separate attempt only when the selected route gives it an independent retry or recovery decision; a
helper or guarded batch remains one attempt.

Every exit returns `history_result`, `outcome_result`, and `cleanup_result`, using the narrowest
applicable state:

| State | Meaning |
| --- | --- |
| `not-started` | The phase was never entered; name the causal earlier boundary. |
| `inapplicable` | The frozen contract proves the phase does not apply. |
| `stopped` | A prerequisite or guard rejected the intended effect, and complete re-observation proves the attempt effect-free. Record the reason, ledger, residual evidence, and next owner. |
| `failed` | An effect occurred or remains ambiguous, or required post-effect proof failed. Record the causal attempt, ledger, residual state, and recovery owner. An effect-free guard rejection is not failure. |

History and outcome alone may add `proven`; cleanup alone may add `complete`. The phase that proves a
positive state owns its payload.

`preflight` is the causal boundary before all three phases. A finalization stop before Ready returns
all three as `not-started`, with `causal_boundary: preflight`, the rejected prerequisite or guard,
proof that no phase effect occurred, and the exact next owner/action. Explicit discard instead makes
history `inapplicable`; before its first effect, outcome and cleanup are `not-started`. Either
preflight boundary makes overall status `stopped`. A failed history attempt leaves outcome and
cleanup `not-started`.

Overall `status` is `complete` only when outcome is proven and cleanup gives every lifecycle item an
authorized disposition. A preflight rejection is `stopped`; after a phase begins, overall status is
that phase's causal `stopped` or `failed`. Later recovery records its own result without replacing
the cause.

Classification begins as `no positive result`. Proven discard becomes `explicit discard`.
Finalization retains the strongest independently proven classification: `history finalized`,
`authoritative delivery`, or `non-integrating handoff`. Only proven local integration or **Already
Delivered** is authoritative delivery. A later stop or failure adds its partial or unproven effect
without erasing or upgrading that fact.

Every return identifies the frozen route, `status`, `classification`, `causal_boundary`, all three
phase results, and enough evidence to prove each claim and residual effect. Include source, target,
reviewed, delivery, and final heads or trees; verification and review binding; publication;
preservation evidence; and `next_owner` only where material. Summarize unaffected state with the
bounded identity and status evidence that places it outside the effect boundary. Finalization also
returns its fixed contract and history policy. A stopped or failed result names the causal phase and
attempt, mismatch or error, recovery route, and every retained partial, failed, or ambiguous effect.

## Select one route

An explicit request to discard exact local state takes the separate destructive contract in
[`references/discard.md`](references/discard.md) and ends there. Otherwise select exactly one
finalization outcome and read only its reference completely:

| Outcome | Selected contract | Classification |
| --- | --- | --- |
| `merge-locally` | [`references/merge-local.md`](references/merge-local.md) | integrating |
| `create-pull-request` | [`references/create-pull-request.md`](references/create-pull-request.md) | non-integrating until the authoritative target contains the result |
| `keep-for-later` | [`references/keep-for-later.md`](references/keep-for-later.md) | non-integrating |
| `return-for-review` | [`references/return-for-review.md`](references/return-for-review.md) | non-integrating |

Load the selected reference during preflight and freeze it for the run; leave every other reference
unloaded. Bring its complete inputs, grants, possible effects, success proof, recovery, and retention
into the common contract before Ready. Execute that same frozen contract only after Ready.

## 1. Prove the finalization contract

Require one exact source worktree, target, and authorized outcome. Bind:

- the source path and branch; its current expected `HEAD`, tree, immutable base, complete
  scope-owned commit range, and the local, Git-administrative, and lifecycle state needed by the
  selected effects;
- the target checkout and branch, expected `HEAD`, boundary relationship, allowed response to
  movement, exact paths, refs, and Git administrative state the selected operation can address,
  and bounded Git identity and status evidence for unrelated local state;
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

Treat caller assertions as claims to prove. Re-observe Git, repository, and explicitly authorized
host evidence: both physical paths, their common repository, worktree registrations, branches,
commits, trees, refs, publication, and lifecycle owners. Use current task context, Git state and
diff, repository evidence, verification and formal-review evidence, and explicit grants. A prior
`create-worktree` result may locate the source or explain its base and lifecycle, but current
evidence controls every assertion used here. A detached, substituted, unavailable, or multiply
identified source stops finalization.

Infer only technical facts that current evidence uniquely proves. Before mutation, route every
unresolved choice or grant to its owner: the exact target; accepted scope in mixed work; reviewed
head and tree and blocker-free review; publication knowledge required by an operation; history
policy; outcome or remote-action authority; or cleanup ownership and grant.

Define the exact paths, refs, and Git administrative state the selected effects may change. Snapshot
only that write set and state needed for recovery: object IDs for affected commits, trees, and refs;
complete index entries and blob OIDs for affected staged paths; and, for affected non-index content,
a manifest of status, file type, mode, applicable symlink target, and content hash. Preserve raw
bytes only where overwrite, deletion, or authorized recovery can require them. Prove that all other
staged, unstaged, untracked, and ignored state lies outside the selected target and write set, then
retain bounded Git identity and status evidence capable of detecting unexpected effects.

Account for every commit and path in the accepted range, classify each relevant local-state item as
scope-owned, unrelated, or ambiguous, and prove required ancestry. Bind verification and formal
review to the same acceptance fixed point, reviewed head, and reviewed tree. A dirty target remains
eligible only when the write set excludes unrelated state and bounded before-and-after evidence can
detect an unexpected effect.

### Source readiness

Require empty output from `git status --porcelain=v1 -z` only when the
selected history operation reads, replaces, or derives its result from source index or working-tree
state; consolidation requires this clean predicate. Otherwise source-local state is eligible only
when bounded evidence proves each item unrelated to the accepted result and current implementation
job, outside the selected operation's write and effect set, and detectable by before-and-after
comparison, while the committed delivery tree remains exactly the reviewed tree. State material to
the accepted result or current job, or whose relationship is ambiguous, stops before Ready and
returns to the implementation owner. It is eligible only when independent accepted authority
classifies the exact state as a preserved successor scope outside this outcome. Record detailed
ignored-item evidence for every item a selected write, recovery, or lifecycle cleanup operation can
address, and preserve every other ignored item. Dirty source state makes worktree removal
ineligible for finalization cleanup; retain or hand it off. Only the separate explicit-discard
route can authorize its loss. Record commands, outputs, and object IDs sufficient for independent
recheck.

### Ready gate

Ready requires the complete common and selected outcome contracts, current identities, accepted
range, review binding, preservation boundary, authorities, and outcome inputs to be exact and
mutually consistent. History and outcome mutation starts only after this gate.

## 2. Finalize the reviewed history

Immediately before each logical effect attempt, recheck every identity, head, tree, range,
local-state, publication, authority, and recovery predicate for all state its children may affect.
Bind the parent phase, attempt identity, pre-state, and intended affected state once. After return or
interruption, re-observe all of that state once and record every child in the parent ledger. Drift
stops. An interrupted or ambiguous attempt remains in-flight; retain its state for the effect owner,
who governs the next action.

If the target moved, continue only when the contract permits rebinding, the new target remains an
ancestor of the reviewed head, and the recomputed range is wholly scope-owned. Otherwise return the
observed target and reviewed state to the implementation workflow or other frozen target-movement
owner. That owner performs any synchronization or other content change, followed by verification
and formal review before a new finalization attempt.

Before rewriting history, test whether the authoritative outcome target already contains every
accepted effect. Current ancestry is sufficient when it proves the exact range. Otherwise require
unambiguous equivalent-change evidence for every effect and evidence that the exact target `HEAD`
and tree passed required verification and blocker-free formal review. Consume that bound evidence
from the implementation owner or return the target state to that owner; this Skill does not perform
the review. An empty diff, similar message, moved tracker state, partial patch, or proof bound to a
different target identity is insufficient. Record a successful proof as **Already Delivered** and
advance directly with that proof.

Apply the frozen history policy below.

### Preserve commits

Re-enumerate `target..reviewed-head`; prove the whole range scope-owned and the source still at the
reviewed head and tree. That head is the delivery head. Published commits are eligible only when
their observed publication and the selected outcome are compatible.

### Consolidate checkpoints

Require the whole range to be unpublished and unrelied-upon, with the exact target as its ancestor.
Select the Skill's POSIX or PowerShell launcher for the host and prove it runnable before any
preparation effect. Each launcher checks only `python3`, then `python`, verifies each command is
Python 3.10 or newer, and runs the helper with the first compatible command. If neither qualifies,
it prints `ERROR: Python 3.10 or newer is required; checked python3, then python.` and exits `2`;
treat that as an effect-free prerequisite rejection. Before Ready, invoke the selected launcher with
only `--help` and require exit `0`.

Freeze an expected-absent unique recovery ref under `refs/smartkit/recovery/` and its derived
`<recovery-ref>-candidate` ref, including exact create, retain, and expected-old-value delete grants.
Use a valid unique name such as `refs/smartkit/recovery/<job>/<attempt>`. Also freeze an
expected-absent message-file path outside every affected worktree, its repository-conforming bytes
and mode derived from the accepted scope, and exact create, read, retention, deletion, and cleanup
ownership. Create that file once as its own logical history attempt and prove its exact contents
before invoking the launcher once for the history attempt.

On a POSIX host:

```sh
sh "<skill-root>/scripts/consolidate_worktree_history.sh" \
  --repository <source-worktree> \
  --target <exact-target-oid> \
  --message-file <message-file> \
  --recovery-ref <new-recovery-ref>
```

On a PowerShell host:

```powershell
& "<skill-root>/scripts/consolidate_worktree_history.ps1" `
  --repository <source-worktree> `
  --target <exact-target-oid> `
  --message-file <message-file> `
  --recovery-ref <new-recovery-ref>
```

The helper invocation is one parent logical attempt; its internal Git operations are child effects.
Treat its aggregate JSON as attempt evidence, never as an effect ledger or proof. After every return
or interruption, independently re-observe the checkout, branch, commits, trees, and refs and record
them in the parent ledger.

On success, prove exactly one new commit whose sole parent is the target, whose tree is byte-identical
to the reviewed tree, whose branch is the source branch, and whose checkout is clean. Retain the
recovery ref at the reviewed checkpoint head. On error, preserve all state, including the message
file and any reported `-candidate` ref, and establish the exact current checkout and branch.

Freeze `history_result` as `stopped` only when re-observation proves a prerequisite, guard, or
expected-absent rejection effect-free. Freeze it as `failed` when an effect occurred or remains
ambiguous, or required post-effect proof failed. Leave later phases `not-started`; retain the ledger
and exact recovery owner/action. Never retry automatically—the owner governs any separately
authorized later attempt.

Freeze the completed phase as immutable **`history_result: proven`**, bound to the history policy,
target boundary, reviewed head and tree, resulting source head and tree, delivery head or **Already
Delivered** proof, recovery refs, message-file disposition, and effect ledger. All outcome work
consumes this immutable result. Target drift afterward stops the attempt before another mutation
unless current evidence proves **Already Delivered**. Retain `history_result` for the target-movement
owner. Any later synchronization creates a new implementation state that must pass verification and
formal review.

Keep history finalization local and deterministic: address immutable object IDs, preserve unrelated
state, use the helper for consolidation, and move refs only through the specified guarded updates.
No history policy permits pull, stash, hard reset, clean, force push, rebase, a merge commit, an
implicit remote action, or replacement of unrelated state. Outcome execution begins from one proven
delivery head and tree or **Already Delivered** evidence.

## 3. Execute the selected outcome

Execute the contract frozen before Ready against immutable `history_result`. Freeze its terminal
**`outcome_result`** with the outcome, proven or retained classification, active terminal step,
attempt ledger, publication, recovery, and residual state. A stopped or failed outcome retains
`history_result` unchanged.

Authoritative delivery requires independently proven integration into the authoritative target,
including **Already Delivered**. Classify a push, pull request, retained branch, or working-tree
transfer as a non-integrating handoff.

## 4. Close from proof

Apply the scoped proof frozen before Ready. Re-observe in detail every checkout path, ref,
publication fact, and Git administrative item in the selected write, recovery, or lifecycle-cleanup
set. For all other state, reprove non-reachability and compare the bounded Git identity and status
evidence for unexpected effects.

Cleanup becomes eligible only after outcome-specific proof establishes that every exact worktree,
branch, recovery item, ignored item, or workflow-owned auxiliary file selected for cleanup belongs
to this lifecycle, contains no user or unrelated work, and has an exact cleanup grant. The host
removes a host-created worktree. Delete an owned branch or recovery ref only after its retention
owner releases it and through an expected-old-OID compare-and-swap; retain the ref on mismatch.
Before deleting a branch, also prove it is absent from every worktree.

Each worktree removal, auxiliary-file removal, and ref deletion is one logical cleanup attempt. When
removal is not owned here, retention or host handoff is the cleanup disposition.

Freeze **`cleanup_result`** with eligibility, every removed, retained, or delegated item, its
attempt ledger, residual state, and owner. It never rewrites `history_result` or `outcome_result`.
