---
name: worktree-environment-setup
description: Use when creating or revising a target repository's Skill for preparing an already-selected linked Git worktree for implementation.
---

# Worktree Environment Setup

## Target meaning

When `setup-project-agents` requests
`GENERATED/.agents/skills/worktree-environment-setup/SKILL.md`, author that one target-owned,
model-invoked Skill. Its actor is an Agent preparing the exact linked worktree already selected by
an owning workflow; its trigger is that worktree's need for repository-specific preparation before
implementation. The Skill owns environment setup evidence and an environment-only result.
`create-worktree` alone decides whole-worktree readiness and lifecycle handoff.

The target uses `name: worktree-environment-setup`, remains model-invoked, and gives `description`
the trigger and environment result. Keep runtime judgment in `SKILL.md`; live repository owners
retain commands, dependency inventories, generated mappings, and service configuration.

Use accepted project intent and evidence qualified by its target-repository owner and provenance.
Relevant evidence includes applicable Rules and Skills; manifests, lock files, toolchain and runtime
configuration; repository-owned setup and generation entry points; CI; required inputs and outputs;
credential requirements without secret values; service lifecycle declarations; and functional
readiness checks. The existing target is regression evidence, not design authority. Visibility,
executability, and write access grant no meaning or permission.

## Obligation dispositions

- Preserve minimum preparation, accepted optional branches, primary-checkout rejection, functional
  readiness, safe reruns, partial-effect recovery, and bounded reporting.
- Change cached recipes to current target-owner lookup and exact selected-root binding.
- Add pre-authorized effect envelopes and complete post-attempt censuses to readiness.
- Preserve a narrow Skill-owned script exception only for otherwise unsupported repeated
  deterministic orchestration; retire prescribed script shapes, fixed wait recipes, and
  setup-authoring mechanics.
- Exclude provisioning, worktree lifecycle, baseline or completed-change verification,
  implementation, history, integration, cleanup, and Agent synchronization;
  `change-set-verification` retains completed-change verification.

## Required runtime contract

### Selected target and authority

Require the exact already-selected root and the caller's authority for its setup effects. Before
mutation, prove its lexical path, effective physical root, registration, repository identity, and
Git common directory; reject the primary checkout or any ambiguous, unregistered, or different
root. Resolve every command from current target-owner evidence and bind its working directory or
explicit repository argument to that physical root.

Define the **Git preservation invariant** from the pre-effect baseline: the selected worktree's
`HEAD` and attachment state, current commit tree, and complete index state remain exact; when
attached, its named branch/ref and target also remain exact. No commit is created, and no ref is
created, deleted, or changes target. Capture that baseline before any effect and prove the
invariant immediately before and after every attempted effect and at the final census.

Establish the minimum preparation every supported new worktree requires and only optional,
platform, or task branches selected by accepted context. Prefer the narrowest current locked entry
point. When no target owner supports a necessary operation, stop rather than inventing a command,
dependency, mapping, degraded result, or cross-platform promise.

Before each effect, freeze its owner-backed invocation and envelope: filesystem targets, durable Git
common-state changes, and external or persistent effects such as credential access or services.
Bind the caller's authority for every mutation to this worktree. Missing, ambiguous, or unowned
authority ends before the effect. Setup may change only authorized state inside those envelopes and
must preserve the Git preservation invariant; an effect envelope never authorizes changing the
protected Git identity, index, or ref state.

### Preparation and recovery

Run only selected evidence-backed dependency installation, input initialization, owned generation,
or required service preparation. Observe the worktree, Git common state, and every effect target
before and after each attempt, including unavailable, failed, or interrupted attempts. Map every
delta to its owner and grant; preserve partial output and process evidence.

A terminating operation requires its owner-declared successful exit; a persistent service requires
its declared lifecycle, liveness, and readiness evidence. Preserve the process and output of a
long-running operation, and base any deadline on its declared duration. After lost control or
uncertain completion, inspect that operation and its effects. Retry only after proving it ended and
its owner declares repetition safe from the observed partial state; otherwise retain evidence and
stop. A reporting or wait interval is not process completion.

Establish environment readiness from current functional evidence for required configuration,
outputs, tools, and services. A version probe suffices only when its owner declares it the readiness
check. Finish with a census proving every effect inside its envelope, every selected branch's
readiness condition satisfied, and the Git preservation invariant holds.

### Observable result and exit

Return exactly one result; the first matching discriminator governs and ends the run:

1. `environment-non-ready` when target identity or binding is invalid; required evidence, input,
   command, authority, or readiness is unavailable or ambiguous; an operation remains failed,
   interrupted, or uncertain after authorized recovery; an unexpected or out-of-envelope effect
   appears; the Git preservation invariant fails, even within an authorized effect envelope; or the
   final census is incomplete.
2. `environment-ready` when all required preparation was already satisfied or completed
   successfully, including any authorized recovery; every selected optional branch is satisfied,
   every actual effect is authorized and in-envelope, every functional readiness check passes, and
   the Git preservation invariant holds.

Report the root; preparation and optional-branch dispositions; invocations and results; effects;
readiness evidence; Git preservation verdict; and work left to another owner.
`environment-non-ready` also reports the blocker, retained partial state, recovery condition, and
when a fresh invocation is safe. Neither result authorizes baseline verification or later
lifecycle action. `environment-ready` is setup evidence for `create-worktree`; only that owner may
combine it with its other gates and issue a worktree-ready handoff.

## Future Author grant and validation

The future Author may inspect qualified target evidence, run owner-supported read-only or
non-fixing checks, and create or replace only
`GENERATED/.agents/skills/worktree-environment-setup/SKILL.md`. When qualified target evidence proves
that necessary repeated deterministic orchestration has no reliable repository-owned entry point,
only accepted input from an owner authorized for every script field may grant the narrow exception.
Before any write, that input must unambiguously name the granting owner; each exact path under the
Skill's `scripts/` directory and its `create` or `replace` operation; target-established runtime;
inputs; outputs; complete effect envelope; required validation; and lifecycle including retention,
update, and removal ownership. The future Author may consume only that grant and may not infer,
supplement, or broaden it. Missing,
ambiguous, unauthorized, or evidence-mismatched fields end with the applicable
`ACCESS_REQUIRED`, `CONTEXT_REQUIRED`, or `HUMAN_DECISION_REQUIRED` handoff. The smallest such
script owns only deterministic sequencing and no judgment; `SKILL.md` retains invocation,
prerequisites, branches, readiness, recovery, and results. No other supporting resource, script
operation, Candidate deletion or move, live-target write, unrelated mutation, or external effect is
authorized without a separate accepted grant.

Bind Machine, Review, and Acceptance evidence to one immutable fingerprint of every Candidate file;
a change invalidates all three. First pass every applicable owner-supported deterministic non-fixing
Machine check. Record `NOT_REQUIRED` only when qualified owner evidence establishes that no Machine
check applies; it cannot replace an applicable check or its failure. Then obtain Quality and
Correctness Review `PASS` for the complete Candidate: Quality covers economy, hierarchy, invocation,
and completion bounds; Correctness covers target binding, commands and any script, effects, optional
branches, recovery, results, preservation, and ownership. Acceptance cannot begin while either
prerequisite is missing or non-PASS.

Only after that barrier may Acceptance execute the Candidate. Each effectful invocation requires a
separate accepted grant naming its root and envelopes. In a representative already-created linked
worktree, exercise the default path, prove primary-checkout rejection before mutation, and establish
the environment result. Record the fingerprint, invocation, pre-effect baseline, final Git
preservation proof, effects, functional evidence, and stop evidence.

Each accepted optional branch with materially distinct behavior, effects, or risk requires its own
Acceptance or owner-supported deterministic proof of its distinct control path, envelope,
preservation, and result. Qualified evidence may share one proof only across equivalent branches.
Unaccepted or unreachable branches need no exercise and are reported outside the accepted
capability. An unproved accepted distinct branch fails validation and blocks ready handoff.

Return exactly one authoring result; the first matching discriminator has precedence:

1. `ACCESS_REQUIRED` when necessary evidence or validation is inaccessible within the grant.
2. `CONTEXT_REQUIRED` when access exists but a necessary fact cannot be discovered from qualified
   evidence.
3. `HUMAN_DECISION_REQUIRED` when qualified evidence permits materially different semantics or a
   required owner, permission, effect, exception, or retirement lacks accepted authority.
4. `VALIDATION_FAILED` when a Machine check or Review is non-PASS, Acceptance fails, any accepted
   materially distinct optional branch lacks sufficient proof, an effect is unaccounted, Git
   preservation invariant fails, or a supported runtime input lacks exactly one observable result.
5. `READY` when the one Candidate contains every required obligation, each supported runtime input
   selects exactly one observable environment result, the Machine and both Review gates pass, and
   Acceptance proves every required accepted capability under exact authority.

Every non-`READY` result ends the current run. Its handoff reports the exact blocker and boundary,
consequence, retained evidence, resolving owner, observable retry predicate, and exact authority
required to retry in a fresh run. In addition:

- `ACCESS_REQUIRED` identifies the missing access, why authorized discovery or validation could not
  obtain it, who can grant it, and the exact access and retry authority required for a fresh run.
- `CONTEXT_REQUIRED` identifies the missing fact, the authorized discovery attempted and why it
  remained undiscoverable despite access, its fact owner, and the exact qualified fact and retry
  authority required for a fresh run.
- `HUMAN_DECISION_REQUIRED` names the decision owner, the live choices, evidence and consequence of
  each, and the accepted choice and authority required for a fresh run.

`READY` reports the Candidate fingerprint, evidence owners, obligation dispositions, Machine and
Review decisions, Acceptance coverage and effects, Git preservation verdict, excluded or
unreachable branches, and untested non-capabilities. It is ready input only for
`setup-project-agents`; it neither invokes setup nor authorizes generation, installation,
publication, commit, push, or a whole-worktree ready handoff.
