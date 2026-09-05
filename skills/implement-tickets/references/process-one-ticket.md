# Process One Ticket

Enter with one frozen dependency-ready ticket in the attributable batch worktree. Read
[Worker boundary](worker-transaction.md) before dispatch. The Worker produces a candidate; the
Controller alone accepts `completed-in-batch`.

## Establish the ticket and choose its review route

Use [Tracker boundary](tracker.md) to revalidate the ticket, complete accepted sources, blockers,
status and claim. Consume its proven initial claim, perform its supported just-in-time claim, or
establish its current no-claim eligibility. Freeze `ticket_base` and its tree at the preceding
accepted HEAD. On resume recover that boundary and the owned current state through
[Pause and resume](resume.md), rather than choosing a new base.

Give a fresh Worker the canonical ticket ID, complete requirements and source revisions,
applicable project rules, dependency results, relevant research pointers, exact worktree and
batch/ticket bases, accepted previous commit identities, targeted checks, and scoped write/commit
authority. Require all intended changes to belong to this ticket. Run checks needed for ticket
acceptance and safe subsequent work; disclose genuinely noncritical deferred coverage for the
whole-batch barrier.

Establish whether fulfilling the ticket requires a code change before choosing the commit and
review sequence. If no change is needed, use [independent empty-diff acceptance](review.md#independently-accept-an-empty-difference)
to prove existing fulfillment and create its authorized empty ticket commit, then join **Accept the
ticket commit** below. A nonempty result follows **Review and mark a nonempty candidate** first.
Neither branch may omit intended changes to manufacture an empty result.

## Review and mark a nonempty candidate

The Worker creates one normal-hook candidate whose sole parent is `ticket_base`. Its message
identifies the ticket using the configured tracker's discoverable reference syntax, but contains no
`SmartKit-Ticket` trailer. Pause Worker writes and independently verify HEAD contains the entire
intended result, the index and working tree are clean under the project predicate, and all material
untracked or ignored state has a known owner. An omitted change or failed check returns to the same
Worker before review.

Invoke public `code-review` from exact `ticket_base` against the frozen candidate. Give it the
complete accepted ticket/spec input, preserving each source's identity and revision even when
commit-message discovery finds only one component. Require both its independent Standards and Spec
subagents to cover that exact base, HEAD/tree and diff. Standards retains the dependency's complete
standards and smell-baseline contract; a heuristic smell is advisory unless project authority makes
it blocking. A skipped or incomplete Spec axis cannot pass this workflow.

Keep the full reports and their original reviewed commit identities. Blocking findings return to
the same Worker, which repairs and amends only the current unpublished, unaccepted candidate through
normal hooks. Pause writes again, repeat applicable checks, and rerun both public review axes on
the resulting immutable state. Prior reports may inform the new reviewers but cannot supply a
passing verdict for changed code. If repair yields a genuinely empty result, switch to independent
empty-diff acceptance before marking it. Missing capability, ambiguous evidence, or a repair that
can make no progress enters `resume.md`.

After required checks and both axes pass, the Controller authorizes one bounded normal-hook
message amendment of the current candidate to add its sole completion trailer:

```text
SmartKit-Ticket: <canonical-id>
```

This authorization covers that exact candidate and message change. The Worker receives no
authority to mark another ticket or amend accepted history. A metadata-only amendment may reuse
review evidence only when all its reviewed inputs remain equivalent. Keep the original report's
reviewed commit and an explicit binding to the new commit; do not relabel its provenance. Rerun
commit-identity and hook-sensitive checks. Hook-created content changes invalidate the pass: retain
the candidate as incomplete, remove its premature completion marker during the supported repair,
and repeat this candidate/check/review sequence before marking it again.

## Accept the ticket commit

After either review route and its authorized commit operation, the Controller pauses writes and
independently proves:

- the first-parent range from `ticket_base` contains exactly one commit, its sole parent is
  `ticket_base`, and its sole ticket trailer is the canonical ID;
- the entire accepted result belongs to this ticket, earlier accepted commits are unchanged,
  and the final tree and accepted diff match the complete review or empty-acceptance inputs;
- required checks pass for the resulting state, full Standards and Spec evidence remains valid,
  the worktree is clean, and the Worker is quiescent; and
- the worktree/target binding and frozen sources, blockers, status and claim are still current.

A trailer, even after a successful hook, is never acceptance evidence by itself. Return the
independently accepted commit as `completed-in-batch`. It satisfies this selected dependency for
later tickets, but proves neither tracker completion nor delivery.
