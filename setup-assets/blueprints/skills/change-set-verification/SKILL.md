---
name: change-set-verification
description: Use when creating or revising a target repository's Skill for verifying a coherent completed change set before handoff.
---

# Change-Set Verification

## Purpose and evidence

For a `setup-project-agents` request targeting `.agents/skills/change-set-verification/SKILL.md`,
the Author produces one target-owned, model-invoked Skill for an Agent, including the repository's
`change-set-verifier`, to verify a coherent completed implementation checkpoint before handoff.
It owns mechanical normalization, sufficient verification, and an evidence-backed verdict.
Implementation and debugging stay with their current owner until a new completed checkpoint exists.

Use `name: change-set-verification`, omit `disable-model-invocation`, and express the completed
checkpoint trigger and verification outcome in `description`. Keep the complete runtime contract
in `SKILL.md`; repository owners retain deterministic commands and mappings.

Setup must supply relevant target evidence: Rules and Skills, accepted task and comparison point,
Git state, manifests, lock files, toolchains, scripts and current help, tests and CI, and owners of
generated sources, dependencies, and direct tests. Qualify sources by owner and provenance.
Classify obligations as preserve, change, add, retire, or non-goal. Existing Skill text supplies
preservation and regression evidence; accepted intent authorizes changes or retirement. Visibility,
executability, write access, and Author permissions confer no Candidate runtime authority.

## Verification contract

### Scope and effects

The Skill establishes the complete change and comparison point from accepted task context and
current Git state: production code, tests, configuration, supporting files, generated effects,
and tracked, staged, unstaged, and untracked state. It preserves `HEAD`, the index, unrelated work,
and user-owned files.

Select the minimum sufficient formatter, static, test, build, runtime, and diff-integrity surfaces
supported by current owners. Broaden only when dependencies, shared contracts, generated interfaces,
tool limitations, fixer mutations, missing test ownership, or unresolved scope make narrower
evidence unreliable. Discovering or repairing pre-existing issues is not a reason to broaden.
Choose repository, native, or MCP tools for scope fidelity, bounded effects, diagnostic quality,
and trustworthy final evidence; resolve commands from live owners.

The runtime grant permits only owner-supported evidence-producing checks whose declared outputs
stay in owner-declared project paths, and normalization of selected project-owned sources. Such
normalization uses an owner-supported formatter or an automatic fixer authorized for a known
mechanical diagnostic or accepted mechanical migration. Generated output changes only through its
declared owner. Every mutation and disposable check output is scoped and reported; every effect
outside this grant requires separate accepted authority.

Unavailable authority for a required effect yields `inconclusive` before that effect. An attempted
or observed effect outside the grant is a safety breach: stop further effects, preserve evidence,
and return `failed` before routing diagnostics.

### Evidence order

Require the order that protects state and keeps evidence current:

- Scope, checkpoint, ownership, prerequisites, and required surfaces are established before mutation.
- An applicable owner-supported formatter precedes checks. An authorized fixer runs once per
  checkpoint on its minimum supported scope; required reformatting and every tool-modified file
  become part of the selected change.
- The resulting state receives minimum supported non-mutating static checks, then directly owned
  tests, then broader surfaces justified by risk or ownership. Each unique surface runs once unless
  a later mutation invalidates its evidence.
- Remaining semantic diagnostics return with exact evidence to the implementation owner. Its next
  change establishes a new checkpoint and restarts verification from current repository state.

Independent non-mutating checks may run concurrently when the Harness preserves selectors and
evidence. Mutation-sensitive checks and generated-output consumers retain their dependencies.
Classify a possibly pre-existing failure against a trustworthy baseline only on the failing surface,
with no broader baseline work than classification needs.

### Results and handoff

Report each selected surface's owner-backed invocation, scope, selection reason, result (`passed`,
`failed`, `inconclusive`, or `not applicable`), and gaps. Include normalization invocations and
mutations, repeats and their causes, semantic diagnostics, and untested surfaces.

After the safety-breach guard, the first applicable condition selects the sole overall result:

| Result | Discriminator |
| --- | --- |
| `semantic_fix_required` | Trustworthy completed evidence identifies a semantic change required from the implementation owner. Concurrent mechanism failures or gaps are reported without replacing this verdict. |
| `failed` | No semantic fix is established, and trustworthy evidence proves a required mechanism, tool, or runtime failure. |
| `inconclusive` | Neither prior result is established, and required evidence, ownership, prerequisites, comparison point, repository state, or baseline classification is insufficient. |
| `passed` | Every required surface passed, every selected mutation is owned and included in the verified change, and no required evidence gap remains. |

Every exit preserves observed state and evidence. Business implementation, semantic repair, worktree
creation or integration, dependency installation, Agent synchronization, Git-history mutation,
delivery, and destructive cleanup remain outside this Skill's ownership and runtime grant.

## Author boundary

The Author may inspect qualified target evidence, run owner-supported read-only or non-fixing
checks, and create or replace `GENERATED/.agents/skills/change-set-verification/SKILL.md` under
setup's request root. The only supporting-file exception is the deterministic selector below.
Deletion, moves, live-target writes, and unrelated mutation are excluded; external effects are
limited to the Acceptance grant. Author permissions do not become runtime permissions.

A single helper script is admissible only when qualified evidence proves owner tools cannot express
a required repeated deterministic selection or aggregation, and accepted input from an authorized
source supplies its exact Candidate-relative path and target owner. The Author verifies and
consumes those values; it does not choose them. Missing, ambiguous, or owner-mismatched authority
requires `HUMAN_DECISION_REQUIRED` before any Candidate write. A glob, directory grant, or
runtime-selected path is insufficient.

The script contract establishes input and output schemas, permitted filesystem and process effects,
failure behavior, owner-supported runtime, representative and boundary validation, and removal when
an owner tool supersedes it. It implements established mappings; policy, scope, ownership,
permissions, broadening, and verdicts remain in `SKILL.md`. A script failure stops with its exact
invocation and error; correction requires a new reviewed Candidate.

## Authoring evidence and result

Readiness depends on Machine evidence, Quality and Correctness Review, and Acceptance of the same
Candidate. Machine checks cover structure, frontmatter, references, paths, and any script using
owner-supported deterministic non-fixing validation. Review covers invocation, scope, effects,
check mapping, order, broadening, baseline classification, verdict precedence, the script exception,
exits, and handoff; unresolved or unsupported mappings prevent PASS.

Acceptance requires passing Machine evidence and Quality and Correctness Review PASS. At that
barrier, freeze the Candidate fingerprint, protected target state (`HEAD`, index, unrelated and
user-owned state), and exact mutable paths and expected effects. Any other Review result stops
before Acceptance.

Acceptance may exercise only the stated runtime effects on an identified representative coherent
completed change in the target repository, where qualified target owners permit them. Cover that
change and one safe applicable failure or stop path, proving normalization scope, required checks,
verdict precedence, reporting, and preservation. Record exact target, selected files, invocations,
expected and observed effects, diagnostics, and before/after state. Dependency installation, history
mutation, delivery, destructive cleanup, and unrelated repository or external effects are excluded.
A necessary effect outside this grant, or missing target-owner authority, requires
`HUMAN_DECISION_REQUIRED` before execution; Author write authority cannot substitute.

After Acceptance, the Candidate and protected target state must match their Review PASS
fingerprints. Reconcile mutable-path changes with the frozen effect plan: record expected granted
changes; any other change invalidates Review and Acceptance. Record untested surfaces.

The first applicable condition determines the sole authoring result:

| Result | Discriminator |
| --- | --- |
| `ACCESS_REQUIRED` | Necessary evidence or validation is inaccessible within the grant. |
| `CONTEXT_REQUIRED` | Access exists, but a necessary fact cannot be discovered from qualified evidence. |
| `HUMAN_DECISION_REQUIRED` | Material semantic alternatives remain, or a required owner, comparison point, permission, effect, exception, or retirement lacks accepted authority. |
| `VALIDATION_FAILED` | Validation remains failed, or a required runtime input lacks one supported observable result. |
| `READY` | The final boundary proves the reviewed and accepted Candidate unchanged, every obligation covered, exactly one result per supported runtime input, and all applicable checks passed or evidenced as `NOT_REQUIRED`. |

A stop names the blocker, owner, consequence, and condition for a fresh attempt. A ready handoff
reports exact Candidate paths, evidence owners, obligation dispositions, checks, Review and
Acceptance evidence, and untested surfaces. It is input to `setup-project-agents`; it grants no
downstream generation, installation, publication, commit, or push.
