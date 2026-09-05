# Finalize the Accepted Batch

Enter with every selected ticket accepted, the exact final batch state verified and independently
reviewed, no unresolved Worker, and no unresolved prior finalizer attempt. A retained finalizer
response enters **Consume the result** directly; a missing or possibly live response first uses
[Pause and resume](resume.md).

## Give the finalizer one accepted result

Read public `finish-worktree`, its chosen outcome reference, and the history, recovery and results
contracts it requires. Preserve the caller-selected outcome and exact authority. Its supported
outcomes are `keep-for-later`, `create-pull-request`, `merge-locally`, `return-for-review`, and
explicit discard; none implicitly selects another. Preserve per-ticket history by default.
A separately explicit consolidation selection uses the finalizer's history contract and retains
source boundaries for recovery and tracker closure.

Immediately before handoff, recheck the physical worktree, Git common identity, registration,
branch, immutable batch base, HEAD/tree, index/local state and authoritative target. Require the
accepted final state and complete change attribution, including material untracked/ignored residuals.
Use [Tracker boundary](tracker.md) to revalidate every frozen ticket/source and dependency. Material
content, source or target drift pauses for reconciliation under its owner; retain evidence and
refresh only proofs whose actual inputs changed.

Supply the finalizer with the complete accepted scope and ticket/spec sources; exact source and
target identities; immutable batch base and accepted HEAD/tree/diff; complete ticket and repair
commit boundaries; full required-verification and independent-review reports with provenance and
any equivalent-state bindings; selected outcome/history policy; observed publication and local
residuals; preservation and lifecycle owners; and exact outcome, history and cleanup authority.

The finalizer validates and consumes this evidence without launching another formal review.
Its operation-sensitive checks remain required. Content changes, invalidated source facts or target
movement return to this implementation workflow for supported synchronization, verification and
review before the affected effect continues. Accepted source commits remain fixed; a necessary new
repair follows [batch repair](review.md#repair-the-whole-batch). Synchronization needing a different
history operation requires its owning contract and authority, not an improvised rewrite.

For a net-empty batch, provide the complete requirement-based acceptance reports. `finish-worktree`
can classify **Already Delivered** only after independently proving that the exact authoritative
target satisfies every accepted effect. Supply target-bound verification and independent acceptance
when needed; source emptiness alone is insufficient. If target fulfillment cannot be proved, return
for that evidence or the already selected supported outcome. Never manufacture delivery, a content
change, or an empty PR to evade the boundary.

Invoke the finalizer once for this accepted result and retain its attributable raw response and
observed effects. Its own external operation receipt is compatible with this Skill's no-batch-journal
model. An interrupted attempt resumes with that owner instead of starting a replacement invocation.

## Consume the result

Preserve the raw `status`, `classification`, `causal_boundary`, phase results, effects, evidence,
residuals and next owner/action. Route by the strongest independently proven classification:

- `authoritative delivery`, including only the finalizer's own **Already Delivered** result:
  continue [tracker closure](tracker.md#close-after-authoritative-delivery). A coincident stopped or
  failed status does not erase delivery. Give closure proof to the named lifecycle owner for its
  remaining cleanup or retention, without repeating delivery.
- `non-integrating handoff`: return the PR, retained worktree or transfer evidence and named
  continuation. Tickets remain open, claims held, and required source/recovery state retained.
- `explicit discard`: retain its exact authorized loss evidence and residual disposition; it
  establishes no tracker completion. Any outstanding tracker disposition remains with that owner.
- `history finalized` or `no positive result`: retain the exact result and incomplete owner/action;
  neither permits tracker completion or a replacement finalization by inference.
- unavailable or ambiguous classification: retain one unresolved handoff with the complete raw
  result and return classification to the finalizer owner. Infer no delivery or new effect.

Record that this response has been consumed in the retained handoff. Resume only its named
unfinished action: proven tracker prefixes, history, publication, outcome and cleanup effects stay
proven. Keep accepted source boundaries until tracker and lifecycle owners establish their required
dispositions, including after explicitly authorized delivery-history consolidation.
