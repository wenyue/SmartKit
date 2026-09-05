# Implement Tickets Redesign — Design Discussion

Status: Complete design confirmed by the user on 2026-09-05; implementation authorized.

This record captures the user's accepted decisions and the remaining design questions for
redesigning `implement-tickets`. It does not itself replace current Skills or ADRs or establish permission for future tracker,
publication, or delivery effects; the user's final confirmation authorizes the documentation rewrite.
The user confirmed the complete proposal with “同意这个完整方案” after clarifying that a
first-pass review success also receives the completion marker. Current Skills and ADRs remain
operative until the corresponding implementation is completed.

## Accepted decisions

### Q1 — Automation boundary

The user accepted the following proposal on 2026-09-05:

- Start from the user's bounded ticket scope, considering tickets whose requirements are
  sufficiently clear and whose implementation is eligible for an Agent.
- Automatically perform selection, dependency analysis, implementation, verification, review
  repairs, and the delivery or handoff authorized for the run.
- Routine steps and transitions between individual tickets require no repeated user confirmation.
- Return to the user for a new product decision, a material scope change, or an inability to
  continue safely.
- Requirements exploration and ticket decomposition remain with their respective workflows.

Evidence: the assistant's Q1 proposal in this conversation, followed by the user's “同意”.
This acceptance settles the intended automation boundary, not the unanswered mechanics below.

### Q2 — Fixed ticket set

The user's clarification establishes that the tickets for this work are fixed.
Continuously scanning a queue and admitting newly created tickets is outside the requested design.
An existing ticket becoming executable after its prerequisites complete changes readiness, not
membership. The consolidated proposal retains the current source-freshness and stop-on-material-
change rules; fixed membership does not itself establish immutable tracker contents.

Evidence: the user's annotation on Q2: “为什么会新增票据呢？按我的理解，票据应该是固定不变的吧”.
The queue-growth scenario was introduced by the assistant and is not a user requirement.

### Q3 — Continue safe independent work (superseded by Q6)

Historical decision, no longer the target behavior: the user initially accepted:

- When one ticket needs a user decision, suspend it and its dependent tickets, retain the question,
  and continue independent tickets where this is safe.
- Before continuing, prove that the failed or suspended attempt has stopped and its residual changes
  cannot affect subsequent work.
- Pause the entire batch when worker quiescence, ownership, or safe continuation cannot be proved.

Evidence: the user's second annotation, “同意”, on the complete Q3 recommendation.
Partial-result delivery, execution isolation, and cleanup are not settled by this acceptance.

### Q4 — Sequential execution in one reusable worktree

The user rejected concurrent implementation and per-Worker worktrees.
Creating a worktree requires expensive environment preparation and linter work in the user's
projects. The redesign therefore retains one Batch Worktree and sequential ticket implementation,
reusing the established environment throughout the batch.

Evidence: the user's first annotation on Q4:
“不并发，因为我的worktree需要有较大的创建成本，需要做环境的建立，以及linter的运行等。”

This preserves ADR-0007's single-worktree and sequential-execution decisions.
The proposed concurrent implementation and serial merger design is rejected.
Q8 later accepts parallel read-only review on the same fixed state. Implementation remains
strictly sequential; independent read-only research scheduling is not changed by Q4.

### Q5 — Per-ticket review and commit; blocked work

The user explicitly requires a separate ticket review and an individual commit for every ticket
that completes. A stage-level or final batch review alone does not satisfy this requirement.
Q8 below settles Reviewer roles; Q13 settles the candidate-commit review mechanism.
Q7 below accepts an additional final cross-ticket review.

Evidence: the user's second annotation on Q5:
“每个ticket都需要单独运行ticket review，并且形成一个单独的commit”.

For a blocked ticket with existing file changes, the user considered stopping or reverting its
changes to continue other tickets, and said stopping is acceptable for simplicity.
The assistant recommends stopping the batch and retaining the current ticket's partial work and
all earlier completed-ticket commits, without automatic rollback or advancing another ticket.
Q6 below subsequently accepts the same batch-stop policy for both changed and unchanged
blocked tickets and supersedes Q3's independent-continuation choice.

Ordinary in-scope implementation, test, or review failures may enter the already-authorized repair
loop. A blocker requiring a new user decision or an inability to continue safely is the stopping
boundary. Q6 confirms this default stop policy.

The Q4 cost constraint and this direction replace the assistant's earlier parallel-isolation
recommendation. They do not authorize a rollback or a worktree cleanup operation.

### Q6 — Pause the entire batch on a material blocker

The user accepted the assistant's Q6 recommendation with “同意”.

Pause the entire batch whenever the current ticket requires a user decision or cannot continue
safely, whether or not it has modified files. Preserve the current ticket's partial work and
earlier completed-ticket commits. Do not automatically revert the partial work, skip the blocked
ticket, or start another ticket. Resume the current ticket after its blocker is resolved.

Ordinary in-scope test failures and review findings remain in the automatic repair loop while
safe correction can make progress; they are not by themselves material blockers.

This decision explicitly supersedes Q3. The design trades independent-ticket throughput during a
block for a simpler sequential execution and recovery model with no skip-and-requeue protocol.

### Q7 — Final cross-ticket review

The user accepted retaining a final whole-batch review after the per-ticket reviews and commits.

Its emphasis is cross-ticket interface consistency, regressions introduced by later tickets, and
whether the combined work satisfies the overall accepted requirements. It may reference valid
ticket-review evidence rather than repeat each ticket's report. All necessary final tests and
checks still have to pass on the final state.

Evidence: the user's annotation “同意” on the complete Q7 recommendation.
This changes the former batch-only review scheme to per-ticket review plus final cross-ticket
review. Q9 settles repair ownership and commit treatment; the consolidated proposal supplies
the final review protocol.

### Q8 — Separate implementation and review ownership

The user accepted the complete clarified Q8 recommendation with “同意”.

- The Controller schedules work, supplies accurate context, and receives results.
- Each ticket has a fresh implementation Worker in the same Batch Worktree. That Worker retains
  responsibility for implementation and review repairs within its ticket.
- Separate Standards and Spec reviewing identities assess repository standards/code quality and
  faithful implementation of the ticket's requirements respectively. The implementation Worker
  does not judge its own implementation.
- The two Reviewers may inspect the same fixed worktree state read-only in parallel without
  creating worktrees or repeating environment preparation. The implementation Worker stops
  writing while that review is in progress.
- Findings return to the original implementation Worker for repair, followed by independent
  re-review. Q13 supersedes the original review-before-commit ordering: create a candidate
  commit first and accept the ticket as completed only after required checks and review pass.

Evidence: the assistant's clarified Q8 role table and accompanying fixed-state/read-only,
repair/re-review, and commit-order proposal, followed by the user's “同意”.
Q13 settles review-to-commit ordering. The consolidated proposal specifies review invocations
and evidence reuse. Q9 below settles final cross-ticket repair ownership and commit treatment.

### Q9 — Append an independently reviewed batch-repair commit

The user accepted the clarified Q9 proposal with “采用。”

A new repair Worker handles final cross-ticket review findings. After required checks and
independent re-review pass, append an independent batch-repair commit and preserve the existing
reviewed ticket commits. Do not rewrite those ticket commits to conceal the cross-ticket repair.

Implementation, repairs, and formal review remain owned by implement-tickets. Pass the final
accepted scope, code state, verification evidence, and review reports to finish-worktree.
The finalizer validates the continued applicability of that evidence and performs its selected
outcome; it does not start another formal review merely because finalization begins.

Evidence: the assistant's clarified Q9 recommendation following the current-finalizer explanation,
and the user's “采用。”. This accepts the proposed repair ownership, extra commit, and review
boundary. Owner-supported verification of the finalizer's own effects remains required.

### Q10 — Independently accepted no-change tickets retain a commit boundary

The user accepted the full Q10 recommendation: if the complete ticket requirements are already
satisfied and no code change is required, independently verify that fulfillment and create an
empty commit carrying the ticket's identifier.

An empty diff alone does not prove fulfillment. Review must inspect the accepted requirements,
the existing implementation, and the relevant verification evidence. This needs an explicit
no-change acceptance route rather than invoking the current diff review with its unsupported
empty-diff input.

Evidence: the user's “同意” annotation on the Q10 recommendation.
The operational route and the all-no-change batch's finalization still need closure; the desired
per-ticket completion behavior and commit boundary are accepted.

### Q12 — Clean committed batch baseline

The user accepted Q12 with “同意”, then asked whether clean mode also allows reuse of Matt
code-review. The clean-baseline decision is accepted; the follow-up review question is not an
acceptance of Q11 or of a change to the review/commit order.

Implement-tickets explicitly requests clean creation from the accepted committed batch base.
Do not carry the source checkout's uncommitted changes into a new batch. Preserve the source
checkout as it stands and reuse the one prepared Batch Worktree for all tickets.
If a ticket requires uncommitted source work, resolve that prerequisite through its owner as an
accepted committed baseline rather than automatically incorporating it into a ticket commit.

This is a caller-specific choice; create-worktree retains its existing default for other callers.
Resuming the exact attributable batch worktree preserves its current partial work and does not
recreate a clean worktree over that state.

## Comparison basis

The redesign must consider both current local `implement-tickets` and the related workflows
on `mattpocock/skills` master. Upstream concepts may inform the design; parity with upstream
is not the objective. The user requires greater automation and a more explicit workflow.

The upstream `master` branch endpoint redirects to `main`. The investigated revision is
`3cca18b368ae95cdbdebbff572ccafa662551015`. The closest workflow is the Beta
`skills/in-progress/implement-spec/SKILL.md`: a provided spec and fixed associated ticket graph,
context pointers, optional shared exploration, concurrent implementers with separate worktrees,
a merger into one PR branch, and end-of-batch review.
See the [primary-source comparison](../../research/2026-09-05-matt-master-ticket-workflows.md).
The graph's ready frontier can change without adding tickets; graph structure does not by itself
require parallel implementation. These upstream mechanisms are factual references, not accepted
choices for SmartKit.

Local baseline: commit `7b20483326e1c92ffa0f633a39825abcbfff4ac1`, with existing user changes
to worktree creation and finalization inspected as current working-tree evidence.
These changes remain owned by their existing workflow.

[ADR-0007](../../adr/0007-use-one-worktree-per-ticket-batch.md) currently accepts one worktree,
sequential execution, per-ticket commit boundaries, no separate Batch journal, and one whole-batch
review. A redesign that changes these decisions must explicitly address their replacement;
existing glossary text does not independently establish design authority.

## Review interface findings and Q11 alternative not adopted

Current public [code-review](../../../skills/code-review/SKILL.md) compares a fixed point to
committed HEAD and rejects an empty diff. It has no supported staged/unstaged/untracked candidate
input. Its whole-diff Standards and Spec responsibilities cannot be narrowed to cross-ticket-only
checking while claiming to invoke that contract unchanged.

Q11 proposed an internal review procedure over uncommitted candidates, including no-change
acceptance. The user instead adopted Q13's candidate-commit/public-review route. The dedicated
no-change acceptance branch remains necessary under Q10; a second general review implementation
for nonempty ticket diffs is not part of the target design.

## Worktree baseline findings underlying accepted Q12

The user raised two interface questions rather than accepting Q11:

1. Current create-worktree carries uncommitted source state by default; how can each ticket then
   produce an independent commit without incorporating inherited changes?
2. Does public code-review require comparison with origin/HEAD?

The second premise is incorrect. Public code-review uses a caller-selected fixed point
(commit, branch, tag, or merge base), comparing it to committed HEAD. It is not restricted to
origin/HEAD. Its relevant limitations remain the absence of an uncommitted-candidate input and
its empty-diff rejection. Q11 remains unaccepted after this conditional user response.

Current [create-worktree](../../../skills/create-worktree/SKILL.md) supports both carry and an
explicit clean choice. Carry copies staged, unstaged, and untracked nonignored source state while
preserving its attribution and source state. It does not convert inherited changes into batch
ownership or commit authority. Clean creates the selected committed base without that transfer;
choosing it does not require making the original checkout clean.

Selective commits alone do not close the carry problem. The reviewed/tested state may include
the committed base, inherited uncommitted changes, and ticket changes, while a ticket-only commit
contains the base and ticket changes. If the ticket depends on inherited behavior, the commit is
not the tested result. Same-file overlap and an inherited staged index further complicate the
ownership boundary.

Accepted Q12: implement-tickets explicitly requests clean creation from the
accepted committed batch base and reuses that one environment for all tickets. Preserve dirty
source state in its original checkout. If required work depends on uncommitted source changes,
pause before batch implementation and resolve a separately authorized committed baseline through
that work's owner. Do not automatically commit, discard, or absorb inherited work, and do not
change create-worktree's default behavior for other callers.

This resolves inherited-baseline ambiguity but not the review-input problem: a ticket still has
uncommitted changes during implementation, so a review-before-commit design still needs the
supported review route. Q13 subsequently resolves review input and commit ordering for nonempty tickets.

## Accepted Q13 — Reuse public review after a candidate commit

Clean creation removes inherited uncommitted state; it does not automatically commit changes
made while implementing a ticket. Before that ticket is committed, HEAD still identifies the
previous accepted ticket (or the initial batch base), so the public HEAD-based diff omits the
current uncommitted implementation.

The user adopted the complete Q13 recommendation with “采用”.

For a nonempty ticket, perform targeted checks, create one local
candidate commit through normal hooks, and invoke public code-review from the fixed ticket base
to that candidate HEAD with the ticket's accepted requirements. Repair findings in the same
implementation Worker, amend only this unpublished, unaccepted current-ticket candidate through
normal hooks, and recheck/re-review until the final version passes. Earlier accepted ticket
commits remain unchanged. Only then accept the ticket boundary and start the next ticket.

The final branch retains one completed commit per ticket. A blocked candidate is retained as
incomplete work rather than interpreted as an accepted ticket merely because a commit exists.
The consolidated proposal below supplies the completion marker and evidence binding.

This accepted decision changes Q8's strict review-before-commit order to commit-before-review while
preserving independent review before ticket completion. It offers direct public-Skill reuse for
nonempty diffs; Q10's no-change acceptance and an all-no-change batch still need their explicit
route because public code-review rejects empty diffs. Q11 is not adopted.

## Confirmed consolidated workflow

This section assembles the confirmed decisions, supporting mechanics, and retained current
contracts. It is the accepted design input for the Skill rewrite. Current Skills and ADR-0007
remain operative until their authorized replacement.

### 1. Freeze scope and establish one environment

Retain the current tracker-owned eligibility, dependency closure, stable ordering, claim timing,
and authority rules. Resolve same-scope dependencies before freezing selection. An unsatisfied
external dependency excludes its dependent with an explicit reason; cycles, uncertain membership,
or unclear eligibility prevent selection. A proven empty selection returns nothing-to-do without
creating a worktree. Report selected tickets and exclusions so selection cannot be mistaken for
completion of every ticket in the user's broader input.

Freeze accepted requirements and their source revisions with ticket membership. Revalidate their
material freshness at the existing claim, ticket-acceptance, and finalization boundaries. A material
change pauses the batch for reconciliation; it never silently changes membership or requirements.

If a selected ticket depends on uncommitted source work, pause before batch implementation and
resolve a separately authorized committed baseline through that work's owner, preserving the
original checkout. Clean creation does not grant ownership of that prerequisite.

For a nonempty selection with its committed prerequisite resolved, request clean creation at the
accepted committed batch base through create-worktree and consume its attributable ready result. Environment preparation belongs to that
owner and its project dependency. Reuse the same environment for subsequent Workers and Reviewers.
Required project checks still run when their inputs change; environment reuse does not waive them.

### 2. Implement and independently accept one ticket

The Controller freezes ticket_base at the preceding accepted HEAD and dispatches a fresh
implementation Worker with the ticket's complete sources, project rules, dependency results,
relevant research pointers, and accepted previous commit identities. Only this Worker writes
implementation changes. Pause its writes before any independent review.

After targeted checks, the Worker creates one local candidate commit through normal hooks.
The initial candidate carries the ticket reference for source discovery but no
SmartKit-Ticket completion trailer. Verify that HEAD contains the entire intended result and
that the worktree is clean before invoking public code-review from ticket_base. Both Standards
and Spec must cover the exact candidate and complete accepted ticket requirements.

Each public invocation uses its independent Standards and Spec subagents. Reuse attributable
earlier reports as context, not as a passing verdict for changed code. Return ordinary findings
to the same implementation Worker, amend only the current unpublished/unaccepted candidate, and
repeat applicable checks and both review axes on the resulting immutable state.

After review passes, the Controller authorizes one bounded normal-hook message amendment of the
current candidate to add the existing
SmartKit-Ticket: <canonical-id> trailer. The Controller independently checks the parent, tree,
accepted diff, required checks, full review evidence, clean state, source freshness, and worker
quiescence before accepting completed-in-batch. A metadata-only amend may reuse review evidence
when its complete reviewed inputs remain equivalent; retain the original report's reviewed commit
and the explicit binding to the new commit rather than relabeling its provenance. Rerun
commit/hook-sensitive checks.
Hook-induced content changes invalidate the review and return this same candidate to repair and
review. The trailer alone never proves acceptance, including after interruption at this step.

The accepted first-parent range from ticket_base contains exactly one commit for the ticket.
Earlier accepted ticket commits remain unchanged. Only completed-in-batch unlocks the next ticket;
it does not close the tracker item or prove delivery.

### 3. Accept a ticket requiring no code change

Use a dedicated independent acceptance branch because public code-review rejects empty diffs.
Supply the two independent reviewing roles with the complete accepted requirements, relevant
existing implementation, applicable standards, and verification evidence. Require affirmative
fulfillment evidence and explicit coverage of both roles; absence of changes is not a pass.

After acceptance, create the normal-hook empty ticket commit carrying the canonical ticket
identifier. Verify that its tree equals ticket_base, relevant checks and evidence still apply,
and the Controller's remaining completion predicates hold. A hook-created content change exits
the empty branch and requires normal candidate review before ticket completion.

### 4. Verify and review the whole batch

After every selected ticket is accepted, run required whole-batch verification and invoke public
code-review from the immutable batch base with all accepted ticket/spec sources. Preserve its
full Standards and Spec coverage while emphasizing interactions, shared constraints, regressions,
and overall fulfillment. Individual reports may supply context and avoid repetitive reporting;
they do not replace examination of the combined final state.

If the final batch diff is empty, use independent requirement-based acceptance over the final
implementation and all accepted sources instead. This applies both to all-no-change tickets
and to a net-empty combination of changed tickets. Preserve individual ticket commits and check
for conflicting requirements or regressions; a net-empty diff alone proves neither acceptance
nor delivery.

For final findings, use a fresh batch-repair Worker in the same worktree. Extend the accepted
candidate-commit sequence to this repair: create a separate repair candidate, repair/amend that
unpublished/unaccepted candidate through normal hooks, and replay required verification and the
whole-batch independent review until it passes. The resulting repair commit has no ticket
completion trailer. Preserve all accepted ticket commits. A later repair after an already
accepted batch result appends its own repair commit rather than rewriting accepted history.

### 5. Pause and resume from attributable evidence

A material blocker pauses the whole batch and preserves the current worktree, partial files,
candidate commit, and earlier accepted ticket commits. Ordinary supported repairs continue
automatically while they can make progress. No-progress failures become a stop with the exact
blocker and next owner; later tickets remain untouched.

Retain the current no-Batch-journal model: recover using Git history, frozen selection and scope,
current tracker observations, retained check/review and dependency handoffs, and live Agent state.
Distinguish the accepted prefix from at most one current ticket or repair candidate plus its
owned local tail. Recheck exact worktree identity and attribution before resuming. Lost worker
responses require proving the original Worker stopped before resuming it or assigning a replacement.

A commit or trailer without adequate acceptance evidence is insufficient to reconstruct a
completed ticket. Recover immutable evidence when available; otherwise repeat missing checks and
independent review against the attributable state. Ambiguous scope, ownership, worker liveness,
or effect state stops. Recover the original tracker/finalizer attempt when its response is
missing; never repeat a possibly completed external effect to obtain a new receipt.

### 6. Finalize once using the accepted final evidence

Retain the caller-selected outcome and exact effect authority. Default to preserving the per-ticket
history; consolidation requires a separate explicit selection. Retain source boundaries for
recovery if an authorized finalizer consolidates delivery history.

Pass the final accepted scope, exact base/HEAD/tree, complete verification and review evidence,
ticket boundaries, and effect authority to finish-worktree. It validates and consumes that
evidence, owns the requested history/outcome/recovery/cleanup effects, and does not launch a
duplicate formal review. Its own operation-sensitive verification remains required.

If content, required source facts, or target movement invalidates the accepted evidence, return
to the implementation owner for the necessary synchronization, verification, and review.
Evidence may be reused only where its actual dependencies remain valid.

Only finish-worktree's authoritative-delivery classification permits the tracker owner to close
tickets. A PR, retained worktree, or review handoff is not tracker completion. For a net-empty
batch, provide requirement-based acceptance evidence; the finalizer must independently establish
that the exact authoritative target satisfies every accepted effect before Already Delivered.
If that target cannot be proved, return for target-bound verification/review or the selected
supported outcome, without inventing delivery from an empty diff.

## Trade-offs and adoption

Compared with Matt implement-spec, reuse its fixed dependency graph, context pointers, independent
two-axis public review, and final combined review. Replace parallel implementers/worktrees and the
merger with one reusable environment and sequential implementation. Add per-ticket review and
commit acceptance, explicit no-change acceptance, stop/resume ownership, and existing tracker and
finalizer effect boundaries. Do not create a draft PR unless that outcome is explicitly authorized.

The costs are two levels of review, candidate amendment and acceptance bookkeeping, and a dedicated
empty-diff branch. The gains are direct reuse of public review for ordinary changes, one final
commit per ticket, bounded Worker context, and simple whole-batch stopping. Final review and
finish-worktree consume distinct responsibilities, so finalization does not add a third review.

Authorized implementation scope:

- Revise implement-tickets and its owned references for the sequence, fresh Worker ownership,
  completion proof, empty-diff acceptance, and recovery. Keep public code-review unchanged.
- Use create-worktree's existing explicit clean interface and finish-worktree's existing evidence
  interface; neither requires a second implementation inside implement-tickets.
- Replace or explicitly supersede ADR-0007's batch-only review decision while retaining its
  one-worktree, sequential execution, source commit boundaries, and no-Batch-journal decisions.
- Synchronize changed first-party Skill mirrors through the repository's authoring workflow;
  preserve the user's independently edited worktree-lifecycle files.

Validate the rewritten workflow against: two dependent tickets; repeated review repair leaving
one ticket commit; a block with dirty files or a candidate commit; review/Worker response loss;
interruption while adding the completion trailer; hooks changing content; an already-satisfied
ticket; an all-empty and a net-empty batch; final repairs preserving earlier ticket history;
material ticket or target drift; and finalizer response loss without duplicate effects.
Run applicable repository checks and diff validation. These define the validation scope for the documentation rewrite, not a claim that the ticket
workflow has already been exercised against a live tracker and repository.

## Final confirmation

Q1, Q2, Q4–Q10, Q12, and Q13 are accepted with the supersessions recorded above.
Q3 is superseded by Q6; Q8's original commit ordering is superseded by Q13; Q11 is not adopted.
The user confirmed this complete workflow, including the supporting mechanics and retained
ownership boundaries, as the basis for the Skill rewrite. The subsequent authoring instruction
explicitly excludes TDD for this documentation task and permits a fresh, elegant organization
rather than preserving the existing prose or section order.
