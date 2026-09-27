---
name: finish-worktree
description: Finish an isolated linked Git worktree by keeping it for later, publishing a pull request, merging locally, transferring its changes back to a checkout, or explicitly discarding it.
---

# Finish Worktree

Finish one selected outcome and leave every remaining item with an owner. This Skill prepares
history when needed, carries out the handoff or delivery, recovers its effects, and accounts for
cleanup. The implementation workflow owns accepted content, verification and formal review.
Tracker closure belongs to its existing owner.

## Establish the job and choose its outcome

Identify the source by its physical path, linked-worktree registration, common repository, branch
and current HEAD. A `create-worktree` handoff helps locate it; current Git evidence must establish
that it is still the intended worktree. Resolve substitutions or ambiguous identities before effects.
Establish the accepted scope, ownership of local state and any unresolved earlier attempt.

Choose the intended result and read its complete route before proceeding:

| Selected route | Result to establish |
| --- | --- |
| `keep-for-later` | [Available work and a continuation owner](references/keep-for-later.md), including dirty or unfinished work. |
| `create-pull-request` | [The exact accepted commit published with its PR](references/create-pull-request.md). |
| `merge-locally` | [The accepted result on the authorized local target](references/merge-local.md), by fast-forward or Already Delivered proof. |
| `return-for-review` | [Task changes combined with a checkout's working files](references/return-for-review.md), preserving its HEAD and complete index. |
| explicit discard | [Only the authorized observed losses removed](references/discard.md), with the unaffected target preserved. |

An ambiguous outcome needs a decision before mutation. Integration, transfer and discard have
different consequences; do not substitute one for another to get past a blocked route.

Use authority already supplied by the request and applicable policy. A PR request includes necessary
publication; a transfer request includes its bounded transfer and protective preparation. Ask only
for a missing material choice or effect, such as the destination or loss beyond an explicit discard
grant. Retain state of uncertain ownership. Independent project or caller requirements for checks
and review still apply.

## Prepare only the phases this outcome needs

Preserve commits by default. For publication, integration or expressly selected consolidation,
read [History Preparation](references/history.md). Consolidation needs an explicit user request or
project requirement; selecting a finishing route alone does not authorize it. Ordinary retention
and transfer have an inapplicable history phase and no blanket formal-review prerequisite.

The route supplies readiness and positive proof. Native Git and the repository's host interface
supply deterministic facts and bounded operations; the Agent decides scope, ownership, semantic
compatibility and authority. If a required capability or source is unavailable, stop its dependent
work and report the missing dependency rather than claiming the route's proof.

Before the first state-changing effect, read [Effect Recovery](references/recovery.md) and persist
its external receipt. If an earlier attempt is unresolved, recover that original attempt before
another effect on the same state. A read-only retention handoff needs only its returned record.

Capture the write set and dependencies once. Reuse shared evidence at batch boundaries, with related
path guards inside the bounded batch. Immediately before an effect, refresh the mutable facts it
depends on: identities, relevant refs, index, affected files, host state and authority over newly
observed losses. Observe afterward what the effect could have changed. Immutable commit/tree and
review evidence remains reusable while its dependencies match.

Drift stops the dependent effect and leaves completed phases intact. If content changes, return
verification and acceptance to the implementation owner under its contract; finalization does not
silently accept a different result.

## Account for what remains

Follow the proven route's retention conditions. Dirty sources stay retained: ordinary finalization
cleanup does not authorize losing their contents. Removal requires exact owned items, release by
their lifecycle and retention owners, and existing removal authority. Inventory ignored content
before any removal that could reach it. Use the host to remove host-created worktrees.

Before deleting a branch, prove it is absent from every worktree. Delete owned branch and recovery
refs with expected-old-OID updates. Give each removal its own receipt and recovery decision.
Authorized retention or delegation, with an owner and release condition, completes cleanup without
requiring deletion.

Read [Public Results](references/results.md) before every return, including stops and failures.
Report actual effects, concise evidence, retained locations and the next owner/action. Completion
requires both the route's positive proof and a disposition for every lifecycle item. A required
check that did not pass leaves its outcome unproven. Later failure cannot erase independently proven
history, publication, handoff or delivery.
