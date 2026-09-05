---
name: worktree-environment-setup
description: Use when creating or revising a target repository's Skill for preparing an already-selected linked Git worktree for implementation.
---

# Worktree Environment Setup

## Purpose and evidence

For a `setup-project-agents` request targeting `.agents/skills/worktree-environment-setup/SKILL.md`,
the Author produces one target-owned, model-invoked Skill for an Agent preparing the exact linked
worktree already selected by its owning workflow. It supplies repository-specific environment
preparation and an environment-only result. `create-worktree` combines this evidence with current
selection and workspace state to decide immediate readiness; it runs no project baseline checks.
Later lifecycle owners reconstruct current state and act under their own explicit grants.

Use `name: worktree-environment-setup`, keep model invocation enabled, and express the preparation
trigger and environment result in `description`. `SKILL.md` owns runtime judgment; repository owners
retain commands, dependency inventories, generated mappings, and service configuration.

Setup must supply relevant target evidence: Rules and Skills, manifests and lock files, toolchain
and runtime configuration, owned setup and generation entry points, CI, required inputs and outputs,
credential requirements without secret values, service lifecycles, and functional readiness checks.
Qualify sources by owner and provenance. Existing text is regression evidence, not design authority;
visibility, executability, and write access confer no authority.

Preserve minimum preparation, accepted optional branches, primary-checkout rejection, functional
readiness, safe reruns, partial-effect recovery, and bounded reporting. Replace cached recipes with
current owner lookup and exact root binding; require pre-authorized effect envelopes and complete
post-attempt censuses. Retain the narrow script exception below, while retiring prescribed script
shapes, fixed waits, and setup-authoring mechanics. Provisioning, worktree lifecycle, baseline or
completed-change verification, implementation, history, integration, cleanup, and Agent
synchronization are non-goals; `change-set-verification` owns completed-change verification.

## Environment contract

### Identity and preservation

The selected root and the caller's authority for its setup effects are prerequisites. Before
mutation, prove the lexical path, effective physical root, registration, repository identity, and
Git common directory. Reject the primary checkout and ambiguous, unregistered, or different roots.
Resolve commands from current target-owner evidence, binding their working directory or explicit
repository argument to that physical root.

The **Git preservation invariant** protects the pre-effect `HEAD`, attachment state, current commit
tree, and complete index state; an attached branch's name/ref and target also remain exact. No
commit is created; no ref is created, deleted, or retargeted. Capture the baseline before any effect
and prove this invariant immediately before and after every attempted effect and at the final
census. An effect envelope cannot authorize changing protected Git state.

### Preparation and effects

Establish the minimum preparation required for every supported new worktree, plus only optional,
platform, or task branches selected by accepted context. Prefer the narrowest current locked entry
point. A necessary operation without a supporting target owner requires a stop, not an invented
command, dependency, mapping, degraded result, or platform promise.

Before each effect, freeze its owner-backed invocation and **effect envelope**: filesystem targets,
durable Git common-state changes, and external or persistent effects, including credential access
and services. Bind the caller's authority for each mutation to this worktree. Missing, ambiguous,
or unowned authority stops before the effect; preparation may change only authorized state inside
its envelopes while preserving the Git invariant.

Permitted preparation consists of selected, evidenced dependency installation, input initialization,
owned generation, and required services. A census of the worktree, Git common state, and every
effect target brackets each attempt, including unavailable, failed, and interrupted attempts.
Attribute every delta to its owner and grant, preserving partial output and process evidence.

A terminating operation needs its owner-declared successful exit; a persistent service needs its
declared lifecycle, liveness, and readiness evidence. Long-running operations retain their process
and output, with deadlines grounded in declared duration. Lost control or uncertain completion
requires observing the original operation and its effects. Retry only after it has ended and its
owner supports repetition from the observed partial state; otherwise retain evidence and stop.
Wait and reporting intervals establish no completion fact.

Readiness requires current functional evidence for required configuration, outputs, tools, and
services. A version probe suffices only when its owner declares it the readiness check. The final
census proves every effect within its envelope, every selected branch ready, and Git preservation.

### Results and handoff

The first applicable condition determines the sole environment result and ends the run:

| Result | Discriminator |
| --- | --- |
| `environment-non-ready` | Identity or binding is invalid; necessary evidence, input, command, authority, or readiness is missing or ambiguous; an operation remains failed, interrupted, or uncertain after authorized recovery; an unexpected or out-of-envelope effect appears; Git preservation fails even inside an envelope; or the final census is incomplete. |
| `environment-ready` | Required preparation was already satisfied or completed, including authorized recovery; every selected optional branch is satisfied, every effect is authorized and in-envelope, functional readiness passes, and Git preservation holds. |

Report the root, preparation and optional-branch dispositions, invocations and results, effects,
readiness evidence, Git preservation verdict, and work retained by other owners. A non-ready result
also names the blocker, retained partial state, recovery condition, and when a fresh invocation is
safe. A ready result is current environment evidence for `create-worktree`, not completed-change
verification or authority for later lifecycle effects.

## Author boundary

The Author may inspect qualified target evidence, run owner-supported read-only or non-fixing
checks, and create or replace `GENERATED/.agents/skills/worktree-environment-setup/SKILL.md` under
setup's request root. Supporting resources, script operations, Candidate deletion or moves,
live-target writes, unrelated mutation, and external effects need a separate accepted grant,
except for the narrow script authorization described here.

A Skill-owned script is admissible only when qualified target evidence proves necessary repeated
deterministic orchestration lacks a reliable repository-owned entry point. Before any write,
accepted input from an owner authorized for every field must specify the granting owner; each
exact path under the Skill's `scripts/` directory and its `create` or `replace` operation; the
target-established runtime; inputs and outputs; complete effect envelope; required validation; and
retention, update, and removal ownership. The Author consumes that grant without inferring,
supplementing, or broadening it. Missing, ambiguous, unauthorized, or evidence-mismatched fields
produce the applicable access, context, or decision stop below.

Use the smallest script that supplies the required deterministic sequencing. Invocation,
prerequisites, branches, readiness, recovery, and results remain judgments in `SKILL.md`.

## Authoring evidence and result

Machine, Review, and Acceptance evidence bind to one immutable fingerprint of every Candidate file;
a Candidate change invalidates all three. Machine evidence requires every applicable owner-supported
deterministic non-fixing check. `NOT_REQUIRED` is valid only when qualified owner evidence proves
no check applies; it cannot replace an applicable check or its failure.

Quality Review covers economy, hierarchy, invocation, and completion bounds. Correctness Review
covers target binding, commands and scripts, effects, optional branches, recovery, results,
preservation, and ownership. Acceptance requires Machine success and both Review PASS decisions
for the complete Candidate.

Each effectful Acceptance invocation requires a separate accepted grant naming its root and
envelopes. In a representative already-created linked worktree, Acceptance exercises the default
path, proves primary-checkout rejection before mutation, and establishes the environment result.
Record the fingerprint, invocation, pre-effect baseline, final Git preservation proof, effects,
functional evidence, and stop evidence.

Every accepted optional branch with materially distinct behavior, effects, or risk needs its own
Acceptance or owner-supported deterministic proof of its control path, envelope, preservation, and
result. Qualified evidence may share proof across equivalent branches only. Unaccepted or
unreachable branches are reported outside the accepted capability; an unproved accepted distinct
branch blocks readiness.

The first applicable condition determines the sole authoring result:

| Result | Discriminator |
| --- | --- |
| `ACCESS_REQUIRED` | Necessary evidence or validation is inaccessible within the grant. |
| `CONTEXT_REQUIRED` | Access exists, but a necessary fact cannot be discovered from qualified evidence. |
| `HUMAN_DECISION_REQUIRED` | Material semantic alternatives remain, or a required owner, permission, effect, exception, or retirement lacks accepted authority. |
| `VALIDATION_FAILED` | Machine or Review is non-PASS, Acceptance fails, an accepted distinct branch lacks proof, an effect is unaccounted, Git preservation fails, or a supported runtime input lacks exactly one result. |
| `READY` | Every obligation is present, each supported runtime input selects exactly one environment result, Machine and both Review gates pass, and Acceptance proves every required accepted capability under exact authority. |

Every stop ends the run and identifies the blocker and boundary, consequence, retained evidence,
resolving owner, observable retry condition, and exact authority for a fresh run. An access stop
also explains why authorized discovery or validation could not obtain the access and who can grant
it. A context stop names the missing fact and its owner, the discovery attempted, and why it
remained undiscoverable despite access. A decision stop gives its owner, live choices, evidence,
and consequences; resumption requires the accepted choice and authority.

A ready handoff reports the Candidate fingerprint, evidence owners, obligation dispositions,
Machine and Review decisions, Acceptance coverage and effects, Git preservation verdict, excluded
or unreachable branches, and untested non-capabilities. It is input to `setup-project-agents`;
generation and downstream effects remain with their owning workflows and explicit grants.
