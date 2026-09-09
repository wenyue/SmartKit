---
name: finish-worktree
description: Finish an isolated linked Git worktree by keeping it for later, publishing a pull request, merging locally, transferring its changes back to a checkout, or explicitly discarding it.
---

# Finish Worktree

Achieve one selected outcome for an isolated worktree and account for what remains. This Skill owns
history preparation, the selected handoff or delivery, recovery of its effects, cleanup and
reporting. The implementation workflow owns changes to the accepted result, verification and formal
review; tracker closure stays with its existing owner.

## Choose the outcome

Establish the accepted scope, ownership of local state, selected outcome and any unresolved prior
effects. Identify the source's physical path, linked-worktree registration, common repository,
branch and current HEAD. A prior `create-worktree` result can locate the job; current Git evidence
must resolve its identity, including substitutions or ambiguity.

Read the selected route's complete contract. Resolve an ambiguous outcome before mutation; never
silently replace integration with transfer or cleanup with discard.

| Outcome | Contract and completion |
| --- | --- |
| `keep-for-later` | [Retain available work](references/keep-for-later.md) with its continuation owner, including unfinished and dirty work. |
| `create-pull-request` | [Publish an accepted commit and establish its PR](references/create-pull-request.md). |
| `merge-locally` | [Prove the accepted result on the authorized local target](references/merge-local.md) through fast-forward or Already Delivered evidence. |
| `return-for-review` | [Transfer task changes into a checkout](references/return-for-review.md), preserving its HEAD and complete index. |
| explicit discard | [Remove only authorized observed losses](references/discard.md) and prove unaffected-target preservation. |

Derive effect authority from the accepted request and applicable policy; reuse grants already made.
A PR request authorizes necessary publication; a transfer request authorizes its bounded transfer
and protective preparation. Ask only for a missing material choice or effect, such as an
unidentified destination or loss outside explicit discard authority. Retain state whose ownership is
uncertain. Independently applicable project or caller policy may require stronger verification or
review.

Preserve commits by default. Publication, integration and explicitly selected consolidation require
[history preparation](references/history.md). Consolidation needs an express user request or project
requirement; choosing an outcome alone does not authorize it. Ordinary retention and transfer need
neither history rewriting nor a blanket formal-review gate; their history phase is inapplicable.

## Carry out the bounded effect

The route defines readiness and positive proof. Use native Git and the repository's host interface
for deterministic facts and bounded operations; judge scope, ownership, semantic compatibility and
authority yourself. Before the first state-changing effect, read [effect
recovery](references/recovery.md) and persist its external receipt. Resume an unresolved prior
attempt there before another effect on the same state. Read-only retention needs only the returned
record.

Capture the write set and dependencies once. Use shared proofs at batch boundaries and related path
guards within a bounded batch. Immediately before an effect, refresh its mutable dependencies:
identities, relevant refs, index, affected files, host state and authority over newly observed
losses. Afterward observe what it could change. Reuse immutable commit/tree and review evidence
while its dependencies match. Content changes return verification and acceptance to the
implementation owner under its contract; drift stops the dependent effect while preserving completed
phases.

## Close the lifecycle and report

Follow the proven outcome's retention conditions. Retain dirty sources: finalization cleanup grants
no authority to lose their contents. Remove only exact owned items released by their lifecycle and
retention owners, with removal already authorized. Inventory ignored content before a removal that
could reach it. The host removes host-created worktrees. Branch deletion requires absence from all
worktrees; delete owned branch/recovery refs through expected-old-OID updates. Record and recover
each removal separately. Retention or delegation with an owner and release condition completes
cleanup without removal.

Read [Public Results](references/results.md) before every return, including stops and failures.
Report the selected route, actual effects and concise evidence, retained locations and next owner
and action. Completion requires the route's proven outcome and a disposition for every lifecycle
item. Report required checks that did not pass without claiming their outcome proven. Preserve any
independently proven history, publication, handoff or delivery despite a later failure.
