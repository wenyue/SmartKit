# Review and Repair

This reference owns review depth, allowances and Controller closure for every ticket and the whole
batch. Public `code-review` owns generic independent Standards/Spec mechanics and its advisory smell
baseline. [Process one ticket](process-one-ticket.md) owns ticket sequencing and the shared Worker
protocol; this reference owns the final batch barrier.

## One round and at most one repair

Each ticket and the whole batch receives exactly one formal round on one immutable state. Both
independent axes collect all findings before repair; together they constitute one round. A
one-ticket batch still receives separate ticket and batch rounds.

After complete review evidence, combine repair-worthy findings and required-check failures into at
most one consolidated repair per unit. No repair is needed when neither exists. A repair is one
attributable dispatch/return phase, including implementation, debugging, normal-hook operations and
checks. An interrupted phase may resume unfinished work; a returned phase needing further correction
pauses the batch. Ordinary ticket implementation/testing before review freezes does not consume
repair, but corrections after the freeze do. Batch acceptance never reopens ordinary implementation.

Changing Worker, commit, diff shape, source facts or route, resuming control, or returning from
finalization preserves the original round and remaining allowance. There is no formal re-review or
new unit that resets them.

Retain the immutable review inputs, role identities and each axis's `never-started`, `in-flight`,
`complete` or unresolved state, with full original reports or recovery locations. Retain check
failures, finding dispositions, repair `unused`, `in-flight` or `returned` state and Worker identity,
exact delta, focused closure and remaining allowance. Keep these in the existing handoff described
in [Pause and resume](resume.md); unknown attempt state remains unresolved, not unused.

## Brief the deep review

Freeze comparison base, HEAD/tree, complete intended diff and accepted requirements with source
identities/revisions. Prove writers paused and no intended task change omitted from the reviewed
state. For a nonempty diff invoke public `code-review` with those exact inputs and every accepted
source, even if commit discovery finds only one. For an empty diff use the independent route below.
A missing or skipped Spec axis cannot satisfy acceptance.

Give both axes this brief for the applicable ticket or complete batch:

- Trace every accepted requirement to implementation and verification evidence, identifying missing,
  partial, incorrect or unsupported fulfillment and unintended scope.
- Inspect relevant callers, callees and affected contracts beyond changed lines. Challenge edge,
  error and recovery paths, compatibility and regressions. Batch coverage also includes shared
  constraints, conflicting requirements and interactions, without narrowing to interactions alone.
- Collect all useful evidence-backed findings. Cite concrete source locations, the requirement or
  standard, behavior and supporting evidence. Distinguish severity, advisory smells, coverage gaps
  and uncertainty; prioritize consequences over speculative cosmetic objections.
- Keep independent axes and findings separate. If compact public summaries cannot hold all findings
  and coverage, retain full supporting reports linked from them. State limits explicitly; a short
  summary must not omit findings.

Each role's complete report identifies immutable inputs, coverage, findings and uncertainty.
Recover incomplete or missing reports through `resume.md` before dispatching repair; incomplete
coverage cannot become a clean verdict.

### Empty differences

Public `code-review` rejects an empty diff. Use the unit's same sole round for two independent
read-only **Standards** and **Spec** roles, independent of the Worker and each other. Supply the frozen
implementation and base, accepted requirements, applicable standards, public smell-baseline
treatment, checks and the deep brief above. They may run in parallel in the established environment.
Missing roles or required inputs stop.

Require affirmative evidence for every requirement and Standards coverage of relevant implementation.
For a ticket, prove existing fulfillment at `ticket_base`; for the final batch, prove all selected
requirements, including when changed tickets cancel one another. Preserve individual ticket commits.
Absence of edits, cancellation or Worker claims alone is insufficient evidence.

If repair changes an empty diff to nonempty or the reverse, use original coverage and focused closure
below to establish fulfillment. Do not switch to a second formal-review route. Inadequate evidence
pauses; ticket marking stays with the ticket procedure and delivery proof with the finalizer.

## Close findings

The Controller judges every finding against accepted requirements and standards, recording a
reasoned disposition for each, including advisory or declined findings. Give the implementation
owner the consolidated repair set and check failures. Preserve original reports and reviewed
identities unchanged.

After any repair returns, pause writes, repeat required checks on the resulting state, including
normal-hook/commit-identity effects, and record the exact delta from review. Perform focused
verification: prove each accepted finding resolved, inspect repair impact on directly affected
behavior/contracts for regressions, and explain how complete original coverage plus closure supports
the final state. This is finding resolution and repair-impact verification, not an open-ended new
Standards/Spec review.

Acceptance requires complete original coverage, justified dispositions for every finding, no
unresolved blocker or required-check failure, an attributable authorized repair delta when present,
and Controller verification bound to exact final HEAD/tree and accepted scope. Unchanged state uses
original reports; metadata-only changes need explicit equivalence and refreshed dependent checks.
For repaired code, report Controller acceptance with repair closure, never a passing reviewer verdict
on a state the roles did not review.

Further required repair, insufficient coverage or material uncertainty pauses the whole batch with
work retained and an exact next owner/action. Subsequent content changes may use only the applicable
unit's still-unused repair with adequate original evidence. Accepted ticket commits stay fixed;
after batch review, correction belongs to the batch allowance.

## Accept the whole batch

With all tickets accepted and Workers quiescent, freeze the final HEAD/tree. Run required whole-batch
checks and obtain both full independent reports against immutable `batch_base` and all accepted
requirements using the contracts above. Ticket reports are context for reviewing the entire combined
result, including interactions and regressions.

Collect check failures and findings before choosing repair. Ordinary check failures need not prevent
review of a meaningfully reviewable frozen state; a missing prerequisite or incomplete evidence
pauses the barrier. If repair is needed, freeze `repair_base` at accepted HEAD and preserve that
failed state, complete reports and every accepted ticket commit. Dispatch a fresh batch-repair
Worker under [Worker protocol](process-one-ticket.md#worker-protocol) with those inputs and the
consolidated findings, scope and remaining authority.

Within that phase, run targeted checks and create at most one separate normal-hook repair candidate
if content changes, with `repair_base` as sole parent and no ticket trailer. Amend only this
unpublished, unaccepted candidate before the phase returns. If content need not change, retain HEAD
and evidence resolving the failure.

Apply Controller closure and required whole-batch checks to exact final state within `batch_base`.
Prove scope, unchanged accepted ticket history, clean local state, Worker quiescence, source
freshness and complete acceptance evidence. For a repair candidate, also prove the sole parent,
one-commit range and absent ticket trailer; otherwise prove unchanged HEAD. Failed closure retains
the candidate and pauses. Acceptance fixes any repair commit; finalization or drift cannot create
another repair commit or acceptance cycle after that allowance is consumed.
