---
name: change-set-verification
description: Verify a coherent completed change set with scoped normalization and required project checks, and report an evidence-backed result before handoff.
---

# Change-Set Verification

## Purpose and evidence

For an independent request to create or revise `.agents/skills/change-set-verification/SKILL.md`, use `write-rules-and-skills` to produce one target-owned, model-invoked Skill for an Agent, including the repository's `change-set-verifier`, to verify a coherent completed implementation checkpoint before handoff. It owns mechanical normalization, sufficient verification, and an evidence-backed verdict. Implementation and debugging stay with their current owner until a new completed checkpoint exists.

Use `name: change-set-verification` and omit `disable-model-invocation`. Supply [fixed-content.json](fixed-content.json) and this directory's source files to the public writer as fixed-content inputs: the blueprint's `description` is copied unchanged into the target Skill, [target metadata](target/agents/openai.yaml) supplies its six interface fields, and [the icon](target/assets/icon.svg) supplies its packaged asset. Preserve independent metadata fields and valid project additions. The blueprint and these sources work with the writer independently of Setup.

Keep shared authority, branch selection, result semantics, and content needed on every path in `SKILL.md`. Split branch-specific contracts or mappings into supporting references only when selective loading improves clarity or avoids loading substantial unrelated content. Each reference has an explicit loading condition, and each selected path reaches its complete contract. Repository owners retain deterministic commands and mappings; repository-specific selection details belong in the body rather than the fixed discovery description.

Establish the target repository from the accepted request and current evidence. The Author discovers and qualifies relevant target evidence: Rules and Skills, accepted task and comparison point, Git state, manifests, lock files, toolchains, scripts and current help, tests and CI, and owners of generated sources, dependencies, and direct tests. Reuse qualified caller-supplied evidence and discover missing facts directly; the caller need not prepare an evidence packet. Qualify sources by owner and provenance. Classify obligations as preserve, change, add, retire, or non-goal. Existing Skill text supplies preservation and regression evidence; accepted intent authorizes changes or retirement. Visibility, executability, write access, and Author permissions confer no Candidate runtime authority.

## Refresh focus

Keep the accepted verification sequence, effect boundaries, and result meanings stable unless project policy or supported tool behavior changes them. Recheck tool selection and affected-surface mappings against current scripts, manifests, CI jobs, and generator owners. A new test runner may change a check route without changing when the Skill may report success or hand work back.

Give the reader concrete directions for selecting the minimum sufficient checks and interpreting their outcomes. Refresh obsolete mappings in place, preserve still-valid project-specific checks and exceptions, and remove duplicated recipes. Reuse unchanged prose and supporting references when they remain complete; existing content is evidence to assess, not a reason to skip assessment.

## Verification contract

### Scope and effects

The Skill establishes the complete change and comparison point from accepted task context and current Git state: production code, tests, configuration, supporting files, generated effects, and tracked, staged, unstaged, and untracked state. It preserves `HEAD`, the index, unrelated work, and user-owned files.

Select the minimum sufficient formatter, static, test, build, runtime, and diff-integrity surfaces supported by current owners, always including project-mandated checks applicable to this change. Broaden only when dependencies, shared contracts, generated interfaces, tool limitations, fixer mutations, missing test ownership, or unresolved scope make narrower evidence unreliable. Discovering or repairing pre-existing issues is not a reason to broaden. Choose repository, native, or MCP tools for scope fidelity, bounded effects, diagnostic quality, and trustworthy final evidence; confirm documented invocations against live owners before use.

The authored Skill must teach an executable route for each selected verification surface. Establish the tool or repository entry, required runtime and working directory, prerequisites and dependency order, exact invocation with arguments and file or test selectors, permitted effects, authoritative completion evidence, result interpretation, and unavailable or failed-use disposition. Supply project-evidenced CLI examples or, for native and MCP operations, concrete tool names and argument forms. Explain how variable selectors are derived from the change. A precise owner entry or help lookup may resolve changing details, but generic directions to find and run appropriate checks cannot replace the invocation route or force runtime readers to rediscover the whole workflow.

Run checks in the existing environment when their prerequisites are satisfied. A linked-worktree location or stale preparation record alone does not invoke environment preparation. An evidenced missing or stale prerequisite for a selected check may require the environment owner, under that owner's invocation conditions and effect authority; verification does not acquire preparation or dependency-installation authority from the gap.

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

The Author may inspect qualified target evidence, run owner-supported read-only or non-fixing checks, and create or replace the Skill entry, target metadata and icon beneath the authorized Candidate root. The target directory is `.agents/skills/change-set-verification/`, containing `SKILL.md`, `agents/openai.yaml`, and `assets/icon.svg`. No fixed staging directory is required. Qualified target evidence determines whether supporting Markdown references are needed and how their contents and names are organized. Each holds only this Skill's necessary contract or mappings reached by its entry pointer, preserving their meaning and force.

Before any Candidate write, use the public writer's layout process to determine and freeze each file's exact Candidate-relative path, target owner, and permitted create or replace operation within existing authority. The Author makes ordinary design choices from project evidence; caller-supplied exact paths are not a prerequisite. Investigate discoverable facts and report unresolved access, evidence, or authority gaps through the writer. All Candidate files remain beneath the authorized root. The deterministic selector below is the only permitted executable supporting file. Deletion, moves, live-target writes, and unrelated mutation are excluded; external effects are limited to the acceptance grant. Author permissions do not become runtime permissions.

A single helper script is admissible only when qualified evidence proves owner tools cannot express a required repeated deterministic selection or aggregation. The Author derives its exact Candidate-relative path and target owner from the accepted task and evidence, and freezes the path and operation through the public writer before writing. Resolve missing ownership or authority before dependent work; ordinary interface design within the grant needs no additional decision.

The script contract establishes input and output schemas, permitted filesystem and process effects, failure behavior, owner-supported runtime, representative and boundary validation, and removal when an owner tool supersedes it. It implements established mappings; policy, scope, ownership, permissions, broadening, and verdicts remain in the Skill's Markdown contract. A script failure stops with its exact invocation and error; correction requires a new reviewed Candidate.

## Acceptance for the target Skill

The public writer owns authoring roles, review, Candidate evidence, and terminal results. The following requirements supply task-specific acceptance for the authored target Skill. Verify invocation, scope, effects, check mappings, order, broadening, baseline classification, verdict precedence, the script exception, exits, and handoff. Each supported runtime input must select exactly one result, and every accepted obligation and mapping needs evidence. Run applicable owner-supported deterministic non-fixing checks, including any script's validation; omitting a check needs evidence that it is not applicable.

Before effectful acceptance, freeze the Candidate fingerprint, protected target state (`HEAD`, index, unrelated and user-owned state), and exact mutable paths and expected effects within the writer's authorized runtime bounds.

Acceptance may exercise only the stated runtime effects on an identified representative coherent completed change in the target repository, where qualified target owners permit them. Cover that change and one safe applicable failure or stop path, proving normalization scope, required checks, verdict precedence, reporting, and preservation. Record exact target, selected files, invocations, expected and observed effects, diagnostics, and before/after state. Dependency installation, history mutation, delivery, destructive cleanup, and unrelated repository or external effects are excluded. Resolve a necessary effect outside this grant or missing target-owner authority through the writer before execution; Author write authority cannot substitute.

After acceptance, prove the Candidate and protected target state unchanged. Reconcile mutable-path changes with the frozen effect plan: record expected granted changes; any other change invalidates the evidence. Record untested surfaces.

Include evidence owners, obligation dispositions, acceptance evidence, effects, and untested surfaces in the writer's handoff. For an unresolved gap, identify the blocker, its owner and consequence, and what would enable continuation. The handoff must be independently usable by the caller and grants no downstream generation, installation, publication, commit, or push.
