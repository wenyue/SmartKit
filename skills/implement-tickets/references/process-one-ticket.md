# Process One Ticket

Enter with one frozen dependency-ready ticket and the attributable batch worktree. The Worker
produces the candidate; the Controller alone accepts `completed-in-batch`. Read
[Review and repair](review.md) before freezing review, and [Pause and resume](resume.md) when
recovering an existing phase.

## Worker protocol

This protocol applies to each ticket and the batch repair. Use a fresh Worker for each new unit;
keep a ticket's implementation and consolidated repair with that Worker. The host runtime must
provide supported dispatch, identity, observation, interruption and quiescence interfaces. An
unavailable or ambiguous runtime stops before dispatch.

Immediately before dispatch, prove the exact worktree and unit base, current HEAD/tree, local-state
ownership and scoped authority, with every prior writer quiescent. At most one Worker may write.
Read-only independent review roles may run in parallel while implementation is paused. Reuse the
established environment, with each Worker bounded to its current unit.

Give the Worker its canonical ticket identity or batch-repair scope, complete requirements and
source revisions, project rules, dependency results and relevant research pointers. Include exact
worktree and batch/unit bases, previous accepted commits, required targeted checks, and scoped
write/normal-hook commit authority. Repairs also receive frozen review evidence, consolidated
findings and remaining allowance from `review.md`. The Worker may change only its unit's candidate;
it cannot amend accepted commits, act on the tracker, finalize the batch or authorize its own
completion marker.

Require a return identifying the Agent and raw status, candidate and final HEAD/tree, complete owned
local state, checks with their inputs, whether the phase returned or remains interrupted, and
unresolved work/next action. For a repair, include finding dispositions and the exact delta. Preserve
failures as failed attempts even when files look complete; recover original phase facts through
`resume.md`.
Prove writes paused before review and quiescence before acceptance. A missing response or elapsed
time alone establishes neither failure nor quiescence.

## Establish the candidate

Use [Tracker boundary](tracker.md) to revalidate complete accepted sources, blockers, status and
claim. Consume the proven initial claim, perform the supported just-in-time claim, or establish
current no-claim eligibility. Freeze `ticket_base` and its tree at the preceding accepted HEAD;
recovery retains that boundary instead of choosing a new base.

Dispatch the ticket Worker under the protocol above. Require the complete intended ticket result
and checks needed for acceptance and safe subsequent work. Disclose any genuinely noncritical
coverage deferred to the whole-batch barrier. Ordinary implementation, testing and debugging
continue until the review freeze.

For a nonempty result, the Worker creates one normal-hook candidate whose sole parent is
`ticket_base`. Its message uses the configured tracker's discoverable ticket reference syntax and
has no `SmartKit-Ticket` trailer. If no change is needed, retain the base state for requirement-based
review; intended changes cannot be omitted to manufacture emptiness.

Pause writes and independently verify the entire intended result, passing ticket checks, a clean
index/worktree under the project predicate, and known ownership of material untracked or ignored
state. Return omitted changes or failed checks to the same Worker before freezing review.

## Review and close

Apply `review.md`'s one-round contract from exact `ticket_base`: use public `code-review` for a
nonempty diff and independent existing-fulfillment review for an empty diff. After complete reports,
the Controller disposes of findings and sends any consolidated repair to the same Worker within the
unit's allowance. Amend only its current unpublished, unaccepted candidate; create the ticket's
one candidate if repair changes the base state. Use normal hooks.

Enter Controller closure on the resulting state under `review.md`. A changed diff shape keeps the
original round. Proceed to marking only when that contract's acceptance evidence holds; unresolved
findings, inadequate coverage or further required repair pause the batch.

## Mark the accepted candidate

After closure, the Controller authorizes one bounded normal-hook operation on this exact candidate,
with the canonical ticket reference and sole trailer:

```text
SmartKit-Ticket: <canonical-id>
```

Amend an existing candidate's message. For a no-change ticket without a candidate, create one empty
commit with `ticket_base` as sole parent. If repair left an existing candidate empty, amend that same
candidate into the empty ticket commit; never append another ticket commit.

Recheck the resulting tree, diff and commit. Bind metadata-only equivalents explicitly to the
original reports without changing their provenance, and rerun commit-identity and hook-sensitive
checks. A no-change result must equal the base tree and retain affirmative fulfillment evidence.

Hook-created content leaves the ticket incomplete. Only an unused ticket repair allowance with
adequate original coverage may remove the premature marker and resolve the hook delta through
focused closure. Reauthorize the marker after closure. Spent allowance, inadequate evidence or
another content change needing repair pauses with state retained. A marker or successful hook alone
never establishes acceptance.

## Accept the ticket commit

After the marker operation, pause writes. The Controller independently proves:

- exactly one commit in the first-parent range from `ticket_base`, with that sole parent and one
  ticket trailer containing the canonical ID;
- the whole result belongs to this ticket, earlier accepted commits are unchanged, and the final
  tree/diff is bound to original review and any Controller repair closure;
- required checks and all `review.md` acceptance predicates hold on the resulting state, the
  worktree is clean and the Worker quiescent; and
- the worktree/target binding and frozen sources, blockers, status and claim remain current.

Return that commit as `completed-in-batch`. It satisfies the selected dependency for later tickets,
but establishes neither tracker completion nor delivery. Acceptance fixes the commit; any later
correction belongs to the whole-batch barrier and its allowance.
