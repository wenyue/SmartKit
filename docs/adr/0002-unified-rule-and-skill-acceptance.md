# ADR 0002: Unify the Rule and Skill Acceptance Standard

Status: Superseded by [ADR 0009](0009-separate-authoring-protocol-from-role-launch.md)

This record describes the former unified workflow. ADR 0009 replaces its lifecycle, role,
reference, review, correction, Acceptance, and candidate-state contracts; retain this file only as
decision history.

Date: 2026-08-14

## Context

Rules, Skills, and authoring workflows previously used acceptance processes of different sizes. An
initial unification then encoded candidate states, recovery, and verdicts
as persistent directory trees and ran Review, Acceptance, and fresh re-review sequentially. This
created many empty directories, duplicate candidates, and repeated evidence collection without
leaving reliably recoverable gate state.

The initiating authoring goal is semantic preservation plus clear, concise, executable Rule and
Skill writing. Matt-informed expression and Markdown mechanics support that goal; qualification is
the proof mechanism, not the product objective.

## Decision

SmartKit uses one Acceptance Standard: evidence-driven authoring, independent quality review,
machine validation, fresh Correctness Review, risk-matched Acceptance, and explicit handoff. Different
artifacts use different Acceptance Portfolios, but no portfolio may replace or weaken a gate.

Shared writing and authoring guidance owns expression mechanics. Rule and Skill authoring and review do
not select or compare external exemplars; they judge the candidate's observable information
hierarchy, executability, and semantic fidelity against accepted evidence. Machine validation must
pass before semantic gates begin. A machine failure stops the run and hands off the exact command,
final exit, relevant output, unrun gates, and unverified surfaces.

One fresh reviewer evaluates one frozen candidate in one bounded task. It performs Correctness Review
first and, only after that passes, runs the candidate's Acceptance Portfolio. The two gates return
separate verdicts. For a directly used Rule or Skill, the reviewer judges observable work from an isolated
Acceptance Runner that receives only runtime-visible candidate content, the representative tasks,
and the context or tools needed for those tasks. Every case starts from its frozen input and does
not inherit another case's output. The Runner receives no ledger, expected result,
diff, author reasoning, review finding, or prior case output.

Before machine validation, one fresh Semantic Economy Reviewer that did not author the candidate reads the
complete candidate without its predecessor, diff, author reasoning, intended edits, or expected
verdict. It checks for stale or duplicated meaning, unnecessary caches of environment facts, no-op
instructions, misplaced branch material, and removable wording or structure. It specifically
challenges instructions that only restate an evidenced Agent or host default, repeat a reliably
loaded broader owner, or follow uniquely from the candidate's trigger, inputs, steps, or adjacent
context. Deletion must leave representative actions, choices, authority, safety boundaries, and
exits unchanged; a default requires governing host evidence. The Reviewer writes no candidate file.
Corrections return to the same Reviewer until the Quality stage passes. Passing does not require a
numeric size reduction, but every increase from an available baseline must map to a distinct
supported obligation.

Setup Authoring Contracts use a separately owned static qualification workflow. A generated Rule or
Skill is a separate candidate that inherits neither evidence nor verdicts and independently passes
the Rule and Skill authoring protocol.

Classify every finding independently. Finding count does not create a decision: one correction step
fixes all current `uniquely-forced` findings. A `decision-required` finding exists only when the
current evidence leaves materially different supported outcomes or correction needs new intent,
evidence, authority, scope, or external action; it must identify the exact unresolved choice, its
owner, and the evidence for each supported outcome. Stop on a valid `decision-required`; otherwise,
return each corrected version through invalidated Quality and machine stages, then give it
to an eligible fresh reviewer to confirm prior findings, falsify the complete artifact, and rerun
affected Acceptance cases. Continue while corrections change the candidate and findings do not
recur; repeated findings or an unchanged correction stop as no progress.

A Qualification Campaign applies the same standard to multiple representative Canary Candidates;
it does not define another quality tier. Candidates are corrected and frozen independently in the
active checkout or a necessary Task Worktree and are invalidated according to their dependencies;
only the Adoption Gate accepts them together as the repository result. When changing the Acceptance
Standard itself, evaluate the candidate against the previously accepted Standard and the current
accepted Spec so the candidate cannot qualify by weakening its own grader.

A Candidate Version is a logical content state in the active checkout or a necessary Task
Worktree, not a copied directory tree. Qualification creates no persistent workspace or report;
the Review Packet is assembled on demand, and the final handoff records commands, exits, verdicts,
and unverified surfaces. Reusable evaluation cases are versioned test inputs, not retained run
state. Generated candidates, mutable working copies, Git state, verdicts, and Acceptance sandboxes
remain temporary.

A shared artifact needs evidence that its policy or job is independent of source-project facts. One
representative traceable context plus direct portability evidence is the default; a second context
is required only when portability materially affects acceptance and direct evidence cannot resolve
it.

## Consequences

Rule and Skill authoring and workflow qualification share the same quality language and termination
conditions. Quality and Correctness separate editorial reduction from semantic falsification; an
isolated Acceptance Runner demonstrates use without receiving the answer. Risk-matched cases and a
progress-checked Correction Loop permit automatic convergence without repeating a
failed operation. The project task contract owns a Qualification Campaign's specific
canaries, scheduling, budget, Defect Cards, and write scope; they do not enter the cross-project
`write-rules-and-skills` runtime Skill. Project Rules and tests own the location, integrity, and
runtime isolation of committed evaluation inputs.
