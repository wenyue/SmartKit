# Codex Harness Adaptation

Apply this waiting guidance in Codex sessions where `wait_agent` provides event-driven mailbox updates. The active task or Skill owns delegation decisions and required results; this Rule changes neither user authorization, Rule precedence, nor completion criteria.

## Wait when no useful parent work remains

Continue useful parent work while it is available. When genuinely idle with child results outstanding, use `wait_agent` as an event wait. Mailbox activity can wake the wait early, so a longer bound need not delay receiving child updates.

Choose a bounded wait supported by the current tool and compatible with applicable waiting limits and progress-reporting requirements. Within those constraints, prefer a duration that avoids unnecessary busy polling; a timeout alone is no reason to shorten the next wait.

A wait timeout reports only that no mailbox update arrived during that interval. It alone establishes neither child failure nor blockage and does not justify interrupting a child. Use actual child messages or status evidence to judge whether intervention is needed.
