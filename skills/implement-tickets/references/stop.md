# Stop or Hand Off the Batch

Stop at the first unproved boundary and block every later ticket and phase. Preserve an owner's raw
result: use `stopped` for a missing prerequisite, authority, dependency, decision, or observation
before its guarded effect; retain a returned `failed` result after an attempted effect; and use
`in-flight` when an original worker, tracker, worktree, or finalizer attempt may still run or its
effect cannot yet be distinguished. Do not turn one state into another from intuition.

For a boundary before any Batch effect, return the bounded scope, tracker route and observations,
selection or exclusions, exact missing fact or capability, proof that no mutation occurred, and
the decision or dependency owner. This establishes no Batch. A proven empty eligible selection is
instead tracker.md's successful `nothing-to-do` result.

For a Pre-ready selection, return two independent partitions. The claim partition contains the
frozen Selection Result and claim plan; zero or more proven initial claims with raw responses and
current tracker proof; an optional current failed or in-flight claim attempt with its intended
delta, before-state, raw result, observation, and tracker owner/action; the untouched initial
suffix; and every JIT/no-claim disposition. An unresolved claim belongs to neither prefix nor
suffix.

The Create partition is exactly one of:

- `never-started`, with the worktree absent and proof that no Create attempt exists;
- `non-ready-or-in-flight`, with the original dependency owner/action and every raw result,
  observation, effect, artifact, and residual; or
- attributable `ready`, with the complete public handoff and current snapshot.

Resume by re-observing both partitions. Consume proven claims without replay. Only after all
required initial claims are proven and no claim is unresolved may `never-started` invoke one
initial Create. `non-ready-or-in-flight` remains exclusively with its original owner/action.
Attributable `ready` is consumed without reinvocation and enters the main Skill's common Batch
binding and immediate readiness recheck. A drifted ready snapshot requires public
`create-worktree` Reuse evaluation and never becomes `never-started`. Include no fabricated
`ready` path, branch, `HEAD`, or tree.

For an established Batch, return enough current evidence for the named owner to resume safely:

- selected tickets, dependency order, immutable base and target;
- Batch Worktree identity, branch, `HEAD`, tree, complete local state, Ticket Commit prefix, and
  current ticket or repair range;
- tracker observations, acquired claims, the exact requested or in-flight operation, and raw
  response;
- worker and finalizer identities, status, retained dependency handoffs and effects;
- verification, review, delivery, publication, lifecycle, and retained recovery evidence; and
- the failed or unproved boundary, residual uncertainty, next owner, and one exact next action.

Resume by re-observing current tracker and Git state and consuming retained attributable handoffs.
Keep supported claims through authoritative delivery and retain source history until post-delivery
tracker and lifecycle closure. An in-flight effect remains with its original owner and is never
repeated merely because the current state resembles its intended result.

Every handoff preserves the canonical checkout, user and unrelated state, worktrees, commits,
refs, and external effects needed for recovery. Force, rebase, reset, clean, rollback, discard,
claim abandonment, unconfigured tracker mutation, implicit remote effects, and deletion of
retained recovery state require separate explicit authority and their owning workflow.

**Complete when:** later work is blocked and the exact raw boundary, preserved state, recovery
owner, and next useful action are unambiguous.
