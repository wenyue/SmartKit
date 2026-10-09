---
name: implement-spec
description: "Implement the result of /to-spec and /to-tickets in code."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

The issue tracker should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

The goal is the entire spec implemented on a single **integration branch**, handed off or delivered through the agreed route.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

## Steps

1. Read the spec and tickets to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Use `create-worktree` to prepare the integration branch in its own worktree, and proceed when it returns `ready`. If the issue tracker closes work through PRs, or the user asks for one, open a draft PR after the first merge in step 5 (a branch with no commits ahead of main can't open one), marked as closing the spec and tickets.

4. Use **implementer subagents** to implement each ticket, each in its own worktree on its own branch. Each implementer subagent:
   - uses `create-worktree` to prepare its worktree from the integration branch, and starts implementation only after a `ready` result;
   - loads and applies the `tdd` skill to build the ticket;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, merge its work to the integration branch with a **merger subagent**.

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency.

7. Once all tickets are complete, load and apply the `code-review` skill on the integration branch. Fix all issues raised by the code review in a single **implementer subagent**. Verify the final integrated result and obtain blocker-free review of that state before finalization.

8. Use `finish-worktree` to finalize the integration worktree through the agreed route. For a PR handoff, reuse the draft PR from step 3 and mark it ready after verified publication. Resolve the spec and tickets only when the issue tracker's closure conditions are met.

9. Include all **implementer subagent** worktrees in `finish-worktree`'s cleanup accounting.
