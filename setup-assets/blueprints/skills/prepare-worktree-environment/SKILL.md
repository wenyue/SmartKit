---
name: prepare-worktree-environment
description: Use when creating or revising a target repository's Skill for preparing an already-selected linked Git worktree for implementation.
---

# Prepare Worktree Environment

## Purpose and evidence

For an independent request to create or revise `.agents/skills/prepare-worktree-environment/SKILL.md`, use `write-rules-and-skills` to produce one target-owned, model-invoked Skill for an Agent preparing the exact linked worktree already selected by its owning workflow. It supplies repository-specific environment preparation and an environment-only result. `create-worktree` combines this evidence with current selection and workspace state to decide immediate readiness; it runs no project baseline checks. Later lifecycle owners reconstruct current state and act under their own explicit grants.

Use `name: prepare-worktree-environment`, keep model invocation enabled, and express the preparation trigger and environment result in `description`. `SKILL.md` owns runtime judgment; repository owners retain commands, dependency inventories, generated mappings, and service configuration.

Establish the target repository from the accepted request and current evidence. The Author discovers and qualifies relevant target evidence: Rules and Skills, manifests and lock files, toolchain and runtime configuration, owned preparation and generation entry points, CI, required inputs and outputs, credential requirements without secret values, service lifecycles, and functional readiness checks. Reuse qualified caller-supplied evidence and discover missing facts directly; the caller need not prepare an evidence packet. Qualify sources by owner and provenance. Existing text is regression evidence, not design authority; visibility, executability, and write access confer no authority.

Preserve minimum preparation, accepted optional branches, primary-checkout rejection, functional readiness, safe reruns, partial-effect recovery, and bounded reporting. Replace cached recipes with current owner lookup and exact root binding; require pre-authorized effect envelopes and complete post-attempt censuses. Require scripted stable, repeatable preparation as described below, while leaving script shape to project evidence and retiring fixed waits and caller orchestration. At runtime, provisioning, worktree lifecycle, baseline or completed-change verification, implementation, history, integration, cleanup, and Agent synchronization are non-goals; `change-set-verification` owns completed-change verification. Authoring Acceptance exercises the lifecycle through its owners without transferring those responsibilities to the environment Skill.

## Refresh focus

Preserve accepted root-identity checks, Git protection, effect boundaries, recovery, and readiness meaning while they remain valid. Revisit the current dependency manifests, lock files, preparation entry points, required generated outputs, and service readiness owners when the environment changes. A new preparation command should update its owner lookup and effects without weakening the surrounding preservation contract.

Explain which evidence distinguishes an already-ready worktree from one needing preparation, and which failed condition prevents readiness. Keep working project-specific optional branches and reasons, refresh obsolete preparation facts in place, and remove superseded recipes instead of accumulating alternatives. Retain unchanged complete content where current evidence supports it.

## Environment contract

### Identity and preservation

The selected root and the caller's authority for its preparation effects are prerequisites. Before mutation, prove the lexical path, effective physical root, registration, repository identity, and Git common directory. Reject the primary checkout and ambiguous, unregistered, or different roots. Resolve commands from current target-owner evidence, binding their working directory or explicit repository argument to that physical root.

The **Git preservation invariant** protects the pre-effect `HEAD`, attachment state, current commit tree, and complete index state; an attached branch's name/ref and target also remain exact. No commit is created; no ref is created, deleted, or retargeted. Capture the baseline before any effect and prove this invariant immediately before and after every attempted effect and at the final census. An effect envelope cannot authorize changing protected Git state.

### Preparation and effects

Establish the minimum preparation required for every supported new worktree, plus only optional, platform, or task branches selected by accepted context. Execute stable, repeatable preparation through the narrowest reliable current project-owned scripts, retaining locked entry points. When no reliable entry exists, the Author supplies the necessary deterministic orchestration under the script contract below. One-off operations may use direct owner-supported commands with an evidenced reason for remaining unscripted. A necessary underlying operation without a supporting target owner requires a stop, not an invented command, dependency, mapping, degraded result, or platform promise.

Before each effect, freeze its owner-backed invocation and **effect envelope**: filesystem targets, durable Git common-state changes, and external or persistent effects, including credential access and services. Bind the caller's authority for each mutation to this worktree. Missing, ambiguous, or unowned authority stops before the effect; preparation may change only authorized state inside its envelopes while preserving the Git invariant.

Permitted preparation consists of selected, evidenced dependency installation, input initialization, owned generation, and required services. A census of the worktree, Git common state, and every effect target brackets each attempt, including unavailable, failed, and interrupted attempts. Attribute every delta to its owner and grant, preserving partial output and process evidence.

A terminating operation needs its owner-declared successful exit; a persistent service needs its declared lifecycle, liveness, and readiness evidence. Long-running operations retain their process and output, with deadlines grounded in declared duration. Lost control or uncertain completion requires observing the original operation and its effects. Retry only after it has ended and its owner supports repetition from the observed partial state; otherwise retain evidence and stop. Wait and reporting intervals establish no completion fact.

Readiness requires current functional evidence for required configuration, outputs, tools, and services. A version probe suffices only when its owner declares it the readiness check. The final census proves every effect within its envelope, every selected branch ready, and Git preservation.

### Results and handoff

The first applicable condition determines the sole environment result and ends the run:

| Result | Discriminator |
| --- | --- |
| `environment-non-ready` | Identity or binding is invalid; necessary evidence, input, command, authority, or readiness is missing or ambiguous; an operation remains failed, interrupted, or uncertain after authorized recovery; an unexpected or out-of-envelope effect appears; Git preservation fails even inside an envelope; or the final census is incomplete. |
| `environment-ready` | Required preparation was already satisfied or completed, including authorized recovery; every selected optional branch is satisfied, every effect is authorized and in-envelope, functional readiness passes, and Git preservation holds. |

Report the root, preparation and optional-branch dispositions, invocations and results, effects, readiness evidence, Git preservation verdict, and work retained by other owners. A non-ready result also names the blocker, retained partial state, recovery condition, and when a fresh invocation is safe. A ready result is current environment evidence for `create-worktree`, not completed-change verification or authority for later lifecycle effects.

## Author boundary

The Author may inspect qualified target evidence, run owner-supported read-only or non-fixing checks, and create or replace the Skill entry and necessary Skill-owned scripts beneath the Candidate root authorized for this request. The entry's target-relative path is `.agents/skills/prepare-worktree-environment/SKILL.md`; new Skill-owned scripts belong under its `scripts/` directory. No fixed staging directory is required. Candidate deletion or moves, live-target writes, unrelated mutation, and external effects need accepted authority distinct from Candidate writing.

Reuse reliable repository-owned preparation scripts. Where qualified evidence establishes stable, repeatable deterministic preparation without a reliable entry, author the smallest script that supplies it. Derive its exact path, target-supported runtime, interface, effect envelope, validation, and retention, update, and removal owner from the accepted task and project evidence. Use the public writer's layout process to freeze exact Candidate paths and create or replace operations before writing. The Author may make these engineering choices within existing authority; the caller need not supply every field. Missing discoverable facts require investigation; genuinely missing access, undiscoverable facts, or material choices use the stops below.

Document each script's invocation, root binding, inputs and outputs, failure and partial-effect behavior, safe reruns, and functional checks. Keep intent, permission, optional-branch selection, recovery decisions, and interpretation of readiness in `SKILL.md`; scripts carry deterministic execution and probes. Script creation alone is not validation.

## Authoring evidence and result

Machine, Review, and Acceptance evidence bind to one immutable fingerprint of every Candidate file; a Candidate change invalidates all three. Machine evidence requires every applicable owner-supported deterministic non-fixing check. `NOT_REQUIRED` is valid only when qualified owner evidence proves no check applies; it cannot replace an applicable check or its failure.

The public writer's required reviews remain in force. Quality Review covers economy, hierarchy, invocation, and completion bounds. Change Review covers intended changes and preservation. Correctness Review covers target binding, commands and scripts, effects, optional branches, recovery, results, preservation, and ownership. Acceptance requires Machine success and all required Review PASS decisions for the complete Candidate.

Bind effectful Acceptance to accepted authority for the actual roots, creation and cleanup losses, and preparation envelopes; reuse authority already covering those effects. For a new or modified preparation script, Acceptance must execute the complete real-target lifecycle. Make the frozen Candidate, including its scripts, discoverable to `create-worktree` in an authorized isolated test source of the actual target repository, recording how that invocation binds to this fingerprint. Invoke `create-worktree` to create a dedicated test worktree and actually invoke this Candidate's environment Skill. Observe creation, the preparation invocation and functional readiness, and `create-worktree`'s final `ready` result for that same root. Then invoke `finish-worktree` with accepted explicit-discard authority for the test-owned state, verifying worktree and temporary branch removal and owner-supported cleanup of test-owned processes and resources. Preserve shared caches and resources outside that loss boundary. Worktree creation and finish remain with those Skills, and environment resource cleanup remains with its declared owner.

A mocked command, script syntax check, manually prepared worktree, or separate preparation invocation after creation cannot substitute for this full-chain evidence. If scripts are unchanged, exercise the default environment path in a representative linked worktree or reuse still-applicable evidence as permitted by the fingerprint contract. In every case, prove primary-checkout rejection before mutation. Record the fingerprint, real repository and test source, exact invocations and results, pre-effect baseline, functional evidence, environment Git preservation, lifecycle effects, cleanup and retained state. Prove the original checkout's HEAD, branch, complete index, tracked, untracked and ignored contents unchanged by the test. A failed, interrupted, uncertain, or incompletely cleaned-up lifecycle cannot pass Acceptance; retain diagnostics and partial state, and complete only safe, authorized cleanup without masking the original failure.

Every accepted optional branch with materially distinct behavior, effects, or risk needs its own Acceptance or owner-supported deterministic proof of its control path, envelope, preservation, and result. Qualified evidence may share proof across equivalent branches only. Unaccepted or unreachable branches are reported outside the accepted capability; an unproved accepted distinct branch blocks readiness.

The first applicable condition determines the sole authoring result:

| Result | Discriminator |
| --- | --- |
| `ACCESS_REQUIRED` | Necessary evidence or validation is inaccessible within the grant. |
| `CONTEXT_REQUIRED` | Access exists, but a necessary fact cannot be discovered from qualified evidence. |
| `HUMAN_DECISION_REQUIRED` | Material semantic alternatives remain, or a required owner, permission, effect, exception, or retirement lacks accepted authority. |
| `VALIDATION_FAILED` | Machine or Review is non-PASS, Acceptance or a required lifecycle stage fails or remains uncertain, required test cleanup is incomplete, an accepted distinct branch lacks proof, an effect is unaccounted, Git preservation fails, or a supported runtime input lacks exactly one result. |
| `READY` | Every obligation is present, each supported runtime input selects exactly one environment result, Machine and all required Review gates pass, and Acceptance proves every required accepted capability under exact authority. |

Every stop ends the run and identifies the blocker and boundary, consequence, retained evidence, resolving owner, observable retry condition, and exact authority for a fresh run. An access stop also explains why authorized discovery or validation could not obtain the access and who can grant it. A context stop names the missing fact and its owner, the discovery attempted, and why it remained undiscoverable despite access. A decision stop gives its owner, live choices, evidence, and consequences; resumption requires the accepted choice and authority.

A ready handoff reports the Candidate fingerprint, evidence owners, obligation dispositions, Machine and Review decisions, Acceptance coverage and effects, Git preservation verdict, excluded or unreachable branches, and untested non-capabilities. The complete result is independently usable by the caller; generation and downstream effects remain with their owning workflows and explicit grants.
