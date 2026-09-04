# Stop or Hand Off the Batch

This reference preserves one noncomplete boundary and the evidence needed to resume safely.

## Principles

- **First boundary wins.** Stop at the first unproved boundary and block every later ticket and
  phase. Use `stopped` for an unproved prerequisite before its guarded effect,
  retain an owner's returned `failed` result after an attempted effect, and use `in-flight` while an
  original attempt may still run or its effect cannot be distinguished. Never translate one state
  into another by intuition.
- **Recoverable handoff.** Preserve enough current evidence for the named owner to take one exact
  next action without repeating an effect or losing attribution. Keep claims, source history,
  worktrees, refs, and other recovery state until their owners prove an authorized disposition.

## Before a Batch exists

For a boundary before any Batch effect, return the bounded scope, tracker route and observations,
selection or exclusions, exact missing fact or capability, proof that no mutation occurred, and
the decision or dependency owner. This establishes no Batch. A proven empty eligible selection is
instead tracker.md's successful `nothing-to-do` result.

For a Pre-ready selection, return two independent partitions. The **claim partition** contains the
frozen Selection Result and claim plan; zero or more proven initial claims with raw responses and
current tracker proof; an optional current failed or in-flight claim attempt with its intended
delta, before-state, raw result, observation, and tracker owner/action; the untouched initial
suffix; and every JIT/no-claim disposition. An unresolved claim belongs to neither prefix nor
suffix.

The **Create partition** is exactly one of:

- `never-started`, with the worktree absent and proof that no Create attempt exists;
- `non-ready-or-in-flight`, with the original dependency owner/action and every raw result,
  observation, effect, artifact, and residual; or
- attributable `ready`, with the complete readiness result and its recorded snapshot.

Resume by entering [`tracker.md`](tracker.md)'s **Resume a Pre-ready selection** route with both
partitions and current evidence. That route owns claim consumption, the one possible initial Create,
dependency recovery, and readiness re-evaluation for the existing candidate.

## After Batch binding

For an established Batch, return the current evidence the named owner needs to resume without
repeating effects or losing attribution, including as applicable:

- selected tickets, dependency order, immutable base and target;
- Batch Worktree identity, branch, `HEAD`, tree, complete local state, Ticket Commit prefix, and
  current ticket or repair range;
- tracker observations, acquired claims, the exact requested or in-flight operation, and raw
  response;
- worker and finalizer identities, status, retained dependency handoffs and effects;
- verification, review, delivery, publication, lifecycle, and retained recovery evidence; and
- the failed or unproved boundary, residual uncertainty, next owner, and one exact next action.

Resume by re-observing current tracker and Git state, consuming retained attributable handoffs, and
re-entering the main Skill at **Establish the route** with that retained and current evidence. Apply
its complete route predicates, which preserve the readiness, review, and finalizer-state gates, then
follow the selected route and next owner.

Keep supported claims through authoritative delivery and retain source history until post-delivery
tracker and lifecycle closure. An in-flight effect remains with its original owner and is never
repeated merely because the current state resembles its intended result.

## Preservation boundary

Every handoff preserves the canonical checkout, user and unrelated state, worktrees, commits,
refs, and external effects needed for recovery. Force, rebase, reset, clean, rollback, discard,
claim abandonment, unconfigured tracker mutation, implicit remote effects, and deletion of
retained recovery state require separate explicit authority and their owning workflow.

**Complete when:** later work is blocked and the exact raw boundary, preserved state, recovery
owner, and next useful action are unambiguous.
