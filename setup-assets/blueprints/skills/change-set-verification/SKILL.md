---
name: change-set-verification
description: Use when creating or revising a target repository's Skill for verifying a coherent completed change set before handoff.
---

# Change-Set Verification

## Target meaning

When `setup-project-agents` requests
`GENERATED/.agents/skills/change-set-verification/SKILL.md`, author that one target-owned,
model-invoked Skill. Its actor is an Agent verifying a coherent completed change set, including the
target repository's `change-set-verifier`; its trigger is a completed implementation checkpoint
before handoff. It owns mechanical normalization, selection of sufficient verification, and an
evidence-backed verdict. Active implementation or debugging remains with its current owner until a
new completed checkpoint exists.

The target frontmatter uses `name: change-set-verification`, omits
`disable-model-invocation`, and gives `description` the completed-checkpoint trigger and verification
outcome. Keep the complete runtime contract in the one `SKILL.md`; live repository owners retain
deterministic commands and mappings.

Use accepted project intent and evidence qualified by its target-repository owner and provenance.
Relevant evidence includes project Rules and Skills; the accepted task and comparison point;
version-control state; manifests, lock files, toolchain declarations, repository scripts and current
help; test layout and CI configuration; and generated-source, dependency, and direct-test owners.
The existing target Skill is preservation and regression evidence, not design authority. Preserve
its supported behavior unless accepted intent changes or retires it; visibility, executability,
write access, or Future Author authority grants no runtime permission to the Candidate.

## Required runtime contract

### Selection, effects, and safety

Require the Skill to:

- establish the intended change set and comparison point from accepted task context and current
  repository state, accounting for its production code, tests, configuration, supporting files,
  generated effects, and tracked, staged, unstaged, and untracked state;
- preserve `HEAD`, the index, unrelated work, and user-owned files, while limiting normalization to
  selected project-owned sources and changing generated output only through its declared owner;
- map the change set to the minimum sufficient formatter, static, test, build, runtime, and
  diff-integrity surfaces supported by current owners, broadening only when dependencies, shared
  contracts, generated interfaces, tool limitations, fixer mutations, missing test ownership, or
  unresolved scope would make narrower evidence unreliable, never merely to discover or repair
  pre-existing issues; and
- select effective repository, native, or MCP tools by scope fidelity, mutation boundary,
  diagnostic quality, and trustworthy final evidence. Point to live owners rather than caching
  command inventories or values recoverable from current configuration or help.

The Candidate's runtime effect grant is exhaustive: it may run owner-supported evidence-producing
checks whose declared outputs stay within owner-declared project paths, and may normalize only
selected project-owned sources with an owner-supported formatter or an automatic fixer authorized
for a known mechanical diagnostic or accepted mechanical migration. It may update generated output
only through its declared owner. Every mutation and disposable check output must be scoped and
reported. Preserve `HEAD`, the index, unrelated work, user-owned files, and every effect outside
this grant. An unavailable required effect yields `inconclusive` before the effect. An attempted or
observed effect outside the grant is a safety breach: stop further effects, preserve its evidence,
and return `failed` before diagnostic routing.

### Procedure island

Require only the order that protects state and evidence:

1. Establish the checkpoint, selected scope, ownership, prerequisites, and required surfaces before
   mutation.
2. Run an owner-supported formatter on selected project-owned sources when applicable. Run an
   authorized automatic fixer only for a known mechanical diagnostic or accepted mechanical
   migration, once per checkpoint on its minimum supported scope. Reformat when required and add
   every tool-modified file to the selected change set.
3. From the resulting state, run the minimum supported non-mutating static checks, then directly
   owned tests, then only the broader surfaces selected by evidenced risk or ownership. Run each
   unique surface once unless a later mutation invalidates its evidence.
4. Return remaining semantic diagnostics with exact evidence to the implementation owner. Any
   implementation-owner change creates a new checkpoint and restarts verification from current
   repository state.

Independent non-mutating checks may run concurrently when the active Harness preserves their
selectors and evidence. Mutation-sensitive checks and consumers of generated output remain ordered.
When a selected failure may predate the change, classify only that failing surface against a
trustworthy baseline and do no broader baseline work than classification requires.

### Optional deterministic selector

A Candidate may contain one helper script only when qualified evidence proves owner tools cannot
express a required repeated deterministic selection or aggregation and accepted input from an
authorized source supplies its exact Candidate-relative path and target owner. The Future Author may
verify and consume, but not choose, either value. Missing, ambiguous, or owner-mismatched authority
stops before any Candidate write with `HUMAN_DECISION_REQUIRED`; a glob, directory-wide grant, or
runtime-selected path is insufficient. The Candidate specifies exact input and output schemas,
permitted filesystem and process effects, failure behavior, owner-supported runtime, representative
and boundary validation, and removal when an owner tool supersedes it. The script implements the
established mapping; it cannot choose policy, scope, ownership, permissions, broadening, or verdicts.
A script failure reports its exact invocation and error and stops; correction requires a new
reviewed Candidate.

### Observable results and exits

For every selected surface, report its owner-backed invocation, scope, selection reason, result as
`passed`, `failed`, `inconclusive`, or `not applicable`, and any remaining gap. Also report every
normalization invocation and mutation, repeat and its cause, semantic diagnostic, and untested
surface.

After the safety-breach guard above, return exactly one overall result under this precedence; the
first true discriminator governs:

1. `semantic_fix_required` when trustworthy completed evidence diagnoses a semantic change that
   the implementation owner must make to the checkpoint. Report concurrent mechanism failures or
   evidence gaps, but they cannot replace this result.
2. `failed` when no semantic fix is established and trustworthy evidence shows a required mechanism,
   tool, or runtime failure.
3. `inconclusive` when neither prior result is established and required evidence, ownership,
   prerequisites, comparison point, repository state, or baseline classification is insufficient.
4. `passed` only when every required surface passed, every selected mutation is owned and included
   in the verified change set, and no required evidence gap remains.

An exit preserves the observed state and evidence. The Skill does not own business implementation,
semantic repair, worktree creation or integration, dependency installation, Agent synchronization,
Git-history mutation, delivery, or destructive cleanup. It may perform only the selected
project-owned normalization and evidence-producing checks above; any other mutation or external
effect requires separate accepted authority and otherwise yields `inconclusive` before that effect.

## Future Author grant

The future Author may inspect qualified target evidence, run owner-supported read-only or
non-fixing checks, and create or replace only
`GENERATED/.agents/skills/change-set-verification/SKILL.md`, plus the single optional script at the
exact path and owner granted by accepted input above. The Author has no delete or move authority and
no authority to write the live target or mutate unrelated target state. Outside the Acceptance grant
below, the Author has no external-effect authority. Creating the Candidate does not transfer the
Author's permissions into its runtime grant.

## Authoring proof and Acceptance grant

Proof is an evidence dependency graph, not an implementation sequence:

- **Machine evidence:** validate the complete Candidate's structure, frontmatter, references, paths,
  and any script with owner-supported deterministic non-fixing checks.
- **Quality and Correctness Review:** review invocation, scope, effect grant, check mapping,
  ordering, broadening, baseline classification, result precedence, script exception, exits, and
  handoff against qualified evidence. **Review PASS** requires every unsupported or ambiguous
  mapping to be resolved.
- **Acceptance barrier:** Acceptance requires Machine evidence and Quality and Correctness Review
  PASS over the same Candidate. At PASS, freeze its fingerprint, protected target state
  (`HEAD`, index, unrelated and user-owned state), and the exact mutable paths and expected effects
  granted to Acceptance. Any other Review result stops before Acceptance.
- **Acceptance evidence:** exercise the actual Candidate on a representative coherent completed
  change set and one safe applicable failure or stop path. Prove normalization scope, required
  checks, verdict precedence, reporting, and preservation of unrelated repository state.
- **Final boundary:** after Acceptance, recheck the Candidate and protected target state against the
  Review PASS fingerprints, and reconcile every authorized mutable-path change with the frozen
  Acceptance effect plan. Expected granted changes are recorded rather than treated as drift; any
  other change invalidates Review and Acceptance. Record exact invocations, mutations, diagnostics,
  initial and final state, and untested surfaces.

This contract grants Acceptance only the Candidate runtime effects stated above, limited to the
identified representative change set in the target repository and only when qualified target
owners permit those effects. Record the exact target, selected files, invocations, expected effects,
and observed effects before and after execution. This grant excludes dependency installation,
history mutation, delivery, destructive cleanup, and every unrelated repository or external effect.
If the necessary Acceptance effect is outside this grant or target-owner authority is absent, stop
before execution with `HUMAN_DECISION_REQUIRED`; Future Author write authority cannot authorize it.

Return exactly one authoring result; the first matching discriminator has precedence:

1. `ACCESS_REQUIRED` when necessary evidence or validation is inaccessible within the grant.
2. `CONTEXT_REQUIRED` when access exists but a necessary fact cannot be discovered from qualified
   evidence.
3. `HUMAN_DECISION_REQUIRED` when qualified evidence permits materially different semantics or the
   required ownership, comparison point, permission, effect, exception, or retirement lacks
   accepted authority.
4. `VALIDATION_FAILED` when validation remains failed or any required runtime input lacks one
   supported observable result.
5. `READY` only when the final boundary proves that the reviewed and accepted Candidate is
   unchanged, contains every required obligation, maps each supported runtime input to exactly one
   result, and all applicable checks passed or are recorded `NOT_REQUIRED`.

Every stop reports the blocker, owner, consequence, and condition for a fresh attempt. `READY`
reports the exact Candidate paths, evidence owners, preserved, changed, added, retired, and non-goal
dispositions, checks, Review and Acceptance evidence, and untested surfaces. It is ready input only
for `setup-project-agents` and grants no downstream generation, installation, publication, commit,
or push.
