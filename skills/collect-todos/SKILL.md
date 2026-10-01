---
name: collect-todos
description: Capture tasks for later in the project's declared task tracker.
disable-model-invocation: true
---

# Collect Todos

Use this Skill only when the user explicitly requests `collect-todos`.

Save deferred work with enough context for a future session to pick it up. Keep capture lightweight:
use evidence already available in the conversation and relevant project sources, then return to
the main task. Collect the tasks the user selected or an established capture instruction covers;
spotting an unrelated improvement alone does not authorize a tracker write.

## Find the project's task tracker

Read the target project's entry instructions, such as `AGENTS.md`, and follow their pointers to
task-tracker and relevant intake or triage conventions. Establish the destination, supported
operation route, and requirements for creating or supplementing tasks before writing. The project
owns its tracker, record format, labels, and workflow; use its declared remote or local tracker
rather than assuming a particular service or documentation directory.

If the declaration is missing, conflicting, unreadable, or its operation route is unavailable,
identify the missing prerequisite and pause persistence. Ask only for the decision or access needed
to proceed. Keep the unsaved tasks visible in the report; a draft in chat is not a saved todo.
Changing the destination requires the user's decision rather than a silent alternate store.

## Capture enough to resume later

Keep independently actionable outcomes separate, while keeping parts of the same work together.
Give each task a concrete title and preserve the useful context:

- The desired outcome, discovery background, and why the work is deferred.
- Known facts and relevant file, artifact, or existing task pointers.
- Confirmed scope, constraints, and acceptance conditions, when known.
- A useful next step and questions still needing investigation or a decision.

Distinguish observations from suggestions and unknowns. Link existing specifications instead of
duplicating them. Missing detail can be recorded as an open question; investigate only what is
needed to identify the task, its destination, or a likely duplicate. Capture does not require a
complete implementation plan and does not authorize doing the deferred work.

If the work is a necessary prerequisite for the main task, explain that dependency and retain its
blocking significance. Recording it for later does not make the main task ready or complete;
continue only main-task work that can proceed independently.

## Save without duplicating work

Search the configured tracker for likely matches and read their scope and status before choosing
where to save. Match the outcome and context, rather than the title alone:

- Create a task when no existing record covers the deferred outcome.
- Supplement a matching task with useful new evidence through the project's supported update or
  comment route, preserving established content and decisions.
- Reference an existing record when it already captures the task; avoid a redundant write.

Follow the project's intake conventions for new records. Preserve existing priority, assignment,
and workflow state unless the capture request or project convention requires a change. Incomplete
capture is not evidence that a task is ready for implementation.

Persist and verify tasks individually so a partial failure has a clear outcome. Read back the
created or supplemented record and check that the intended content is present at its authoritative
URL or configured local path. Verify referenced records too. A command being issued or an
unconfirmed response does not establish persistence.

If a write fails or its result is uncertain, reconcile the tracker state before repeating it.
Retry only after evidence establishes that the earlier operation ended and repetition is safe,
with a supported correction to the failure. If verification or recovery cannot establish the
result, stop affected writes and report that task as not saved or uncertain, with the reason and
what is needed next. Preserve verified results for the other tasks.

## Report the collected todos and return to the main task

Account for every task selected for capture. For each one, report a human-readable summary of what
needs doing, its outcome, and the authoritative link or local path for a verified record. Distinguish
newly saved, supplemented, already recorded, not saved, and uncertain outcomes; name what evidence
or decision is still missing for unsuccessful items. A count or list of links alone is insufficient.

When a main task is active, give this report as a progress update and resume its authorized work,
subject to any prerequisite blockers. For a standalone capture request, finish with the report.
