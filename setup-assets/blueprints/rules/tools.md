# Tools

## Purpose and evidence

For an independent request to create or revise `.agents/rules/tools.md`, use `write-rules-and-skills` to produce one target-owned Rule titled `Tools`.

Establish the target repository from the accepted request and current evidence. The Author discovers and qualifies relevant target evidence: entry guidance, manifests and runtime requirements, repository scripts and current help, task runners and CI, Git state, existing Rules and Skills, and accepted Issues, Specs, or ADRs. Reuse qualified caller-supplied evidence and discover missing facts directly; the caller need not prepare an evidence packet. Qualify each source by owner and provenance. Accepted project intent governs; existing Rule text supplies preservation and regression evidence. Classify obligations as preserve, change, add, retire, or non-goal, preserving supported policy unless accepted intent changes or retires it. Visibility and access confer no authority.

## Policy to establish

The Rule connects each consequential condition to its required outcome:

- **Invocation:** working-directory and runtime requirements that determine whether a tool works.
- **Synchronization:** canonical changes, their required synchronization, supported read-only drift checks, and generated effects requiring review.
- **Mutation:** the authority for each operation and the permitted read-only, scoped, dry-run, or stop alternative when authority is absent.
- **Verification:** the complete change from its declared comparison point, including tracked, staged, unstaged, and untracked state, generated effects, affected surfaces, and every applicable non-fixing check.
- **Handoff:** an existing Skill's observable trigger and bounded result when that Skill owns the job.

Bind each handoff to the called Skill's invocation conditions and authority. For environment preparation, those conditions are first use of a newly created linked worktree, an evidenced missing or stale environment prerequisite for the current task, or an explicit user preparation request. Ordinary implementation and checks use the existing environment when their prerequisites are satisfied. A linked-worktree location or invalid cached preparation record alone establishes no preparation need; cache validity determines evidence reuse within an otherwise warranted invocation.

Keep API, capability, generated-source, delivery, installation, dependency, contract-evolution, and placement policy with their existing owners. Scripts retain deterministic mechanics; Skills retain procedures. Include live-owner facts only when their omission changes a policy outcome, leaving inventories, command catalogs, snapshots, and caller orchestration to those owners.

## Refresh focus

Recheck runtime requirements, tool entry points, generator ownership, and CI selectors on each refresh. Follow the current manifests, script help, and CI jobs to determine which changes need synchronization or verification. Correct changed facts promptly, even when this blueprint is unchanged; preserve project-specific conditions and permission boundaries that still apply.

Emphasize decisions a contributor needs before running a tool: the correct root, affected inputs and outputs, the supported check, and the action required by its result. Keep stable policy wording when its meaning remains accurate. Replace outdated mappings instead of appending another competing recipe, and retain an unchanged complete Rule when the evidence warrants no correction.

## Authoring boundary and acceptance

The Author may inspect target evidence, run owner-supported read-only or non-fixing checks, and create or replace `.agents/rules/tools.md` beneath the Candidate root authorized for this request. Settle that root, exact path and operation through the public writer before writing. No fixed staging directory is required. Deletion, moves, live-target writes, unrelated mutation, and external effects require separate accepted authority.

The public writer owns authoring, review, and terminal results. Acceptance for this Rule requires every required mapping and affected surface to have an evidenced outcome: each supported predicate selects one observable policy outcome without invented facts, and every included exact command is supported by its current owner. Required checks must pass; omitting a check needs evidence that it is not applicable.

Include target and evidence owners, obligation dispositions, check results, preserved constraints, and uncertain or untested surfaces in the writer's handoff. For an unresolved access, evidence, or authority gap, identify the blocker, its owner and consequence, and what would enable continuation. The handoff must be independently usable by the caller and grants no downstream generation, installation, publication, commit, or push.
