---
name: change-set-verification
description: Use when creating or revising a target repository's Skill for verifying a coherent completed change set before handoff.
---

# Change-Set Verification

## Purpose and evidence

For an independent request to create or revise `.agents/skills/change-set-verification/SKILL.md`, use `write-rules-and-skills` to produce one target-owned, model-invoked Skill for an Agent, including the repository's `change-set-verifier`, to verify a coherent completed implementation checkpoint before handoff. It owns mechanical normalization, sufficient verification, and an evidence-backed verdict. Implementation and debugging stay with their current owner until a new completed checkpoint exists.

Use `name: change-set-verification`, omit `disable-model-invocation`, and express the completed checkpoint trigger and verification outcome in `description`. Keep shared authority, branch selection, result semantics, and content needed on every path in `SKILL.md`. Split branch-specific contracts or mappings into supporting references only when selective loading improves clarity or avoids loading substantial unrelated content. Each reference has an explicit loading condition, and each selected path reaches its complete contract. Repository owners retain deterministic commands and mappings.

Establish the target repository from the accepted request and current evidence. The Author discovers and qualifies relevant target evidence: Rules and Skills, accepted task and comparison point, Git state, manifests, lock files, toolchains, scripts and current help, tests and CI, and owners of generated sources, dependencies, and direct tests. Reuse qualified caller-supplied evidence and discover missing facts directly; the caller need not prepare an evidence packet. Qualify sources by owner and provenance. Classify obligations as preserve, change, add, retire, or non-goal. Existing Skill text supplies preservation and regression evidence; accepted intent authorizes changes or retirement. Visibility, executability, write access, and Author permissions confer no Candidate runtime authority.

## Refresh focus

Keep the accepted verification sequence, effect boundaries, and result meanings stable unless project policy or supported tool behavior changes them. Recheck tool selection and affected-surface mappings against current scripts, manifests, CI jobs, and generator owners. A new test runner may change a check route without changing when the Skill may report success or hand work back.

Give the reader concrete directions for selecting the minimum sufficient checks and interpreting their outcomes. Refresh obsolete mappings in place, preserve still-valid project-specific checks and exceptions, and remove duplicated recipes. Reuse unchanged prose and supporting references when they remain complete; existing content is evidence to assess, not a reason to skip assessment.

## Verification contract

### Scope and effects

The Skill establishes the complete change and comparison point from accepted task context and current Git state: production code, tests, configuration, supporting files, generated effects, and tracked, staged, unstaged, and untracked state. It preserves `HEAD`, the index, unrelated work, and user-owned files.

Select the minimum sufficient formatter, static, test, build, runtime, and diff-integrity surfaces supported by current owners, always including project-mandated checks applicable to this change. Broaden only when dependencies, shared contracts, generated interfaces, tool limitations, fixer mutations, missing test ownership, or unresolved scope make narrower evidence unreliable. Discovering or repairing pre-existing issues is not a reason to broaden. Choose repository, native, or MCP tools for scope fidelity, bounded effects, diagnostic quality, and trustworthy final evidence; confirm documented invocations against live owners before use.

The authored Skill must teach an executable route for each selected verification surface. Establish the tool or repository entry, required runtime and working directory, prerequisites and dependency order, exact invocation with arguments and file or test selectors, permitted effects, authoritative completion evidence, result interpretation, and unavailable or failed-use disposition. Supply project-evidenced CLI examples or, for native and MCP operations, concrete tool names and argument forms. Explain how variable selectors are derived from the change. A precise owner entry or help lookup may resolve changing details, but generic directions to find and run appropriate checks cannot replace the invocation route or force runtime readers to rediscover the whole workflow.

The runtime grant permits only owner-supported evidence-producing checks whose declared outputs stay in owner-declared project paths, and normalization of selected project-owned sources. Such normalization uses an owner-supported formatter or an automatic fixer authorized for a known mechanical diagnostic or accepted mechanical migration. Generated output changes only through its declared owner. Every mutation and disposable check output is scoped and reported; every effect outside this grant requires separate accepted authority.

Unavailable authority for a required effect yields `inconclusive` before that effect. An attempted or observed effect outside the grant is a safety breach: stop further effects, preserve evidence, and return `failed` before routing diagnostics.

### Evidence order

Require the order that protects state and keeps evidence current:

1. Establish scope, checkpoint, ownership, prerequisites, and required surfaces before mutation. Map the change to project-mandated and directly affected checks, with selection reasons and usable invocation routes.
2. Run an applicable owner-supported formatter before checks. An authorized fixer runs once per checkpoint on its minimum supported scope; required reformatting and every tool-modified file become part of the selected change.
3. Run minimum supported non-mutating static checks on the resulting state.
4. Run directly owned tests, followed by broader test, build, runtime, or diff-integrity surfaces justified by risk or ownership and every applicable project-mandated check. Run each selected surface once. Repeat it only when a relevant change invalidates its evidence or the cause of a previous failure has been resolved.
5. Interpret authoritative completion evidence, account for normalization and other effects, and produce the result and handoff below. Missing tools, prerequisites, authority, or evidence follow the applicable failure or inconclusive path rather than silently skipping a required surface.
6. Return remaining semantic diagnostics with exact evidence to the implementation owner. Its next change establishes a new checkpoint and restarts verification from current repository state.

Independent non-mutating checks may run concurrently when the Harness preserves selectors and evidence. Mutation-sensitive checks and generated-output consumers retain their dependencies. Classify a possibly pre-existing failure against a trustworthy baseline only on the failing surface, with no broader baseline work than classification needs.

### Results and handoff

Retain complete command output in accessible, scoped, owner-supported locations within the runtime grant. Record each selected surface's invocation, scope, selection reason, exit status, result (`passed`, `failed`, `inconclusive`, or `not applicable`), and evidence gaps, including normalization effects and repeats with their causes. Summarize successful checks by scope, result, and test counts where available; report failed checks with actionable diagnostics and the complete-output location. The final handoff reports the overall result, changed behavior, material gaps, and evidence locations without replaying command output.

After the safety-breach guard, the first applicable condition selects the sole overall result:

| Result | Discriminator |
| --- | --- |
| `semantic_fix_required` | Trustworthy completed evidence identifies a semantic change required from the implementation owner. Concurrent mechanism failures or gaps are reported without replacing this verdict. |
| `failed` | No semantic fix is established, and trustworthy evidence proves a required mechanism, tool, or runtime failure. |
| `inconclusive` | Neither prior result is established, and required evidence, ownership, prerequisites, comparison point, repository state, or baseline classification is insufficient. |
| `passed` | Every required surface passed, every selected mutation is owned and included in the verified change, and no required evidence gap remains. |

Every exit preserves observed state and evidence. Business implementation, semantic repair, worktree creation or integration, dependency installation, Agent synchronization, Git-history mutation, delivery, and destructive cleanup remain outside this Skill's ownership and runtime grant.

## Author boundary

The Author may inspect qualified target evidence, run owner-supported read-only or non-fixing checks, and create or replace `.agents/skills/change-set-verification/SKILL.md` beneath the Candidate root authorized for this request. No fixed staging directory is required. Qualified target evidence determines whether supporting Markdown references are needed and how their contents and names are organized. Each holds only this Skill's necessary contract or mappings reached by its entry pointer, preserving their meaning and force. Before any Candidate write, use the public writer's layout process to determine and freeze each file's exact Candidate-relative path, target owner, and permitted create or replace operation within existing authority. The Author makes ordinary design choices from project evidence; caller-supplied exact paths are not a prerequisite. Missing discoverable facts require investigation; genuinely missing access, undiscoverable facts, or material choices use the result protocol below. All Candidate files remain beneath the authorized root. The deterministic selector below is the only permitted executable supporting file. Deletion, moves, live-target writes, and unrelated mutation are excluded; external effects are limited to the Acceptance grant. Author permissions do not become runtime permissions.

A single helper script is admissible only when qualified evidence proves owner tools cannot express a required repeated deterministic selection or aggregation. The Author derives its exact Candidate-relative path and target owner from the accepted task and evidence, and freezes the path and operation through the public writer before writing. An unresolved owner or authority requires `HUMAN_DECISION_REQUIRED`; ordinary interface design within the grant does not.

The script contract establishes input and output schemas, permitted filesystem and process effects, failure behavior, owner-supported runtime, representative and boundary validation, and removal when an owner tool supersedes it. It implements established mappings; policy, scope, ownership, permissions, broadening, and verdicts remain in the Skill's Markdown contract. A script failure stops with its exact invocation and error; correction requires a new reviewed Candidate.

## Authoring evidence and result

Readiness depends on Machine evidence, the public writer's required Quality, Change and Correctness Review, and Acceptance of the same Candidate. Machine checks cover structure, frontmatter, references, paths, and any script using owner-supported deterministic non-fixing validation. Review covers invocation, scope, effects, check mapping, order, broadening, baseline classification, verdict precedence, the script exception, exits, and handoff; unresolved or unsupported mappings prevent PASS.

Acceptance requires passing Machine evidence and all required Review PASS decisions. At that barrier, freeze the Candidate fingerprint, protected target state (`HEAD`, index, unrelated and user-owned state), and exact mutable paths and expected effects. Any other Review result stops before Acceptance.

Acceptance may exercise only the stated runtime effects on an identified representative coherent completed change in the target repository, where qualified target owners permit them. Cover that change and one safe applicable failure or stop path, proving normalization scope, required checks, verdict precedence, reporting, and preservation. Record exact target, selected files, invocations, expected and observed effects, diagnostics, and before/after state. Dependency installation, history mutation, delivery, destructive cleanup, and unrelated repository or external effects are excluded. A necessary effect outside this grant, or missing target-owner authority, requires `HUMAN_DECISION_REQUIRED` before execution; Author write authority cannot substitute.

After Acceptance, the Candidate and protected target state must match their Review PASS fingerprints. Reconcile mutable-path changes with the frozen effect plan: record expected granted changes; any other change invalidates Review and Acceptance. Record untested surfaces.

The first applicable condition determines the sole authoring result:

| Result | Discriminator |
| --- | --- |
| `ACCESS_REQUIRED` | Necessary evidence or validation is inaccessible within the grant. |
| `CONTEXT_REQUIRED` | Access exists, but a necessary fact cannot be discovered from qualified evidence. |
| `HUMAN_DECISION_REQUIRED` | Material semantic alternatives remain, or a required owner, comparison point, permission, effect, exception, or retirement lacks accepted authority. |
| `VALIDATION_FAILED` | Validation remains failed, or a required runtime input lacks one supported observable result. |
| `READY` | The final boundary proves the reviewed and accepted Candidate unchanged, every obligation covered, exactly one result per supported runtime input, and all applicable checks passed or evidenced as `NOT_REQUIRED`. |

A stop names the blocker, owner, consequence, and condition for a fresh attempt. A ready handoff reports exact Candidate paths, evidence owners, obligation dispositions, checks, Review and Acceptance evidence, and untested surfaces. The complete result is independently usable by the caller; it grants no downstream generation, installation, publication, commit, or push.
