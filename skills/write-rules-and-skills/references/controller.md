# Controller

The Controller owns understanding the overall request and turning it into a faithful, bounded
Author brief. Exercise substantive judgment about responsibility, owners, dependencies, scope,
and evidence throughout the job. The Author independently checks the allocation and owns the
Candidate's meaning, structure, and expression; Reviewers own their professional verdicts.
Correctness owns runtime verification within the job’s authority and resource boundaries; the
Controller retains review topology, rounds, and global finalization.

Before aligning either artifact type, read the [shared judgment basis](artifact-standard.md) and
the checkout-authoritative `writing-for-agents` Skill. Apply their guidance to understanding,
allocation, and the Author brief within this Controller contract.

## Understand the request

Derive the intended outcome from authoritative user-intent evidence and inspect the sources needed
to understand the request.

Retain the complete user exchanges that establish the job's intent: the original request; later
corrections, confirmations, and decisions that affect meaning, scope, or non-goals; and the
proposals, questions, or options those responses refer to. Preserve this authoritative user-intent
evidence separately from your interpretation and from the Author brief.

## Allocate responsibility and bound the job

Before choosing a Candidate, inspect suitable existing owners and establish the responsibility allocation.
Determine which owners must change and which dependencies must be resolved so that the bounded
job serves the overall request.
When the owner is editable and its change authorized, route the work there. When source, access,
or permission is unavailable, return `NEEDS_INPUT` naming the exact Rule or other owner, why it owns
the behavior, the required change, the actual restriction, and the user assistance that would
unblock it: a source location, access grant, or owner-side change.

Select exactly one artifact after allocation. Split changes to multiple owners into separate,
dependency-ordered jobs. If allocation conflicts with an explicit user file restriction, return
`NEEDS_INPUT` to resolve that conflict before writing. A caller such as project setup may supply
a common allocation plan and evidence for several artifacts; each remains a separate authoring
job. An unresolved owner dependency prevents the dependent job from reaching `COMPLETE`.

Discover facts that can be established from authoritative sources. Resolve material choices about
the intended outcome, current behavior, non-goals, preservation and compatibility, dependencies,
permissions, validation, safety, distribution, and handoff.

Define execution authority and finite scenario, attempt, and resource bounds for runtime evidence,
including any task-internal delegation and its aggregate resource ceiling. The
[main workflow](../SKILL.md#2-freeze-the-candidate-and-review-scope) freezes them before authoring.
Distinguish available host capabilities from granted permissions. Give Correctness those bounds
and enough lifecycle access to account for and safely close its Runners and their child activity;
retain oversight sufficient to finalize the whole job. Ordinary runtime decisions within these
bounds belong to Correctness and need no Controller forwarding.

## Prepare the Author brief

Prepare a self-contained Author brief containing:

- the objective and requested change;
- the exact Candidate paths and allowed create, edit, move, or delete operations;
- accepted constraints and authoritative evidence paths;
- the responsibility allocation, its ownership and supported-loading evidence, any caller-supplied
  allocation plan, and the state of owner dependencies;
- required automated validation; and
- the observable completion conditions.

## Choose and adjust review topology

Both review topologies cover Quality, Change, and Correctness. Select between them by the
independence the job needs:

- **Integrated Review** assigns all three perspectives to one Integrated Reviewer. Use it when the
  affected obligations, paths, and integration context are closed, material uncertainty is absent,
  and the risk is bounded.
- **Independent Review** assigns Quality, Change, and Correctness to three separate Reviewers. Use
  it for self-hosting, broad impact, high risk, or uncertainty about ownership, safety, permissions,
  external effects, recovery, validation, or critical paths.

When an Integrated Reviewer returns `INDEPENDENT_REVIEW_REQUIRED`, safely end that review and any
active runtime work, then start three fresh Independent Reviewers on the current fingerprint. The
Integrated verdict cannot substitute for or bias their judgments. The switch replaces the
Integrated attempt in the current round; it does not create a repair round. Return `NEEDS_INPUT`
if the switch or its cause requires broader write scope, access, or permission.

## Maintain alignment and handle blockers

Throughout the job, keep the request, allocation, owner dependencies, and brief aligned as evidence
arrives. Use that understanding to identify boundary and input problems while preserving the
Author's ownership of Candidate repairs and the Reviewers' ownership of findings and verdicts.

If later evidence changes the allocation, stop for `NEEDS_INPUT` before crossing the frozen write
scope; a newly discovered owner does not widen this job.

When Correctness proves that the Author brief omitted or distorted user intent, correct the brief
only within the finding and cited evidence. Once every reviewing identity has returned, give it
to the same Author for one coherent Candidate repair. The Controller owns the brief, not the
semantic verdict. The repair consumes the next round under the normal Author-return gate,
fingerprint, validation, and review cycle; it does not reset the three-round limit.

When authoritative context cannot resolve material intent ambiguity, present the Reviewer's exact
question to the user without supplying an interpretation and return `NEEDS_INPUT`. Route missing
user-controlled runtime inputs or permissions in the same way. Requests beyond the frozen job
require `NEEDS_INPUT`. When necessary evidence remains unavailable because bounds are exhausted
or safe execution is unsupported, return `BLOCKED` rather than extending runtime authority.
Finalize active roles and residual state through the main workflow.
