# Codex Harness Adaptation

Use Codex operations to carry out the active task or Skill's decisions. That workflow owns why an
Agent is delegated and what result it must produce. This Rule supplies tool adaptation; it changes
neither user authorization, Rule precedence, nor completion criteria.

## Coordinate Delegated Work

Choose the operation for the work the Agent now needs:

| Need | Operation |
| --- | --- |
| Start one concrete, independently useful task | `spawn_agent` |
| Add context without starting another turn | `send_message` |
| Give an idle Agent a new bounded task | `followup_task` |
| Stop an Agent's current work | Use `interrupt_agent` only when that work should stop. |
| Inspect current status | Use `list_agents` for an intentional inspection, not a polling loop. |

Use the task name or agent identifier returned by `spawn_agent` with subsequent Subagent operations.

### Wait when no useful parent work remains

Continue useful parent work while it is available; a completed Agent's mailbox update arrives on
the parent's next turn. When genuinely idle with live Agents, use `wait_agent` as an event
subscription. A long subscription wakes on mailbox activity with the same latency as a short one,
so shorter polling adds calls without reducing response time.

Use bounded stretches of 300000–600000 ms where the active Harness and runtime allow. When their
current limits require a shorter stretch, use a supported duration within those limits. A timeout
means only that no mailbox update arrived during the stretch; do not shorten the next stretch
merely because the previous one timed out.

## Compose Concurrent Tool Calls

Within `functions.exec`, choose how to collect results from independent calls already selected for
concurrent execution: use `Promise.allSettled` when partial results remain useful, or `Promise.all`
when every result is required. Keep calls sequential when the current tool schema or an applicable
Skill prohibits parallel execution.
