# Codex Harness Adaptation

Use this guidance in Codex sessions where `wait_agent` provides event-driven mailbox updates. The active task or Skill still owns delegation and required results; waiting changes neither user authorization, Rule precedence, nor completion criteria.

## Work while useful work remains; wait when idle

Continue useful parent work while it is available. When genuinely idle with child results outstanding, use `wait_agent` as an event wait. Mailbox activity can wake it early, so a longer bound need not delay receiving a result.

Choose a bound supported by the current tool and compatible with applicable waiting limits and progress-reporting requirements. Within those limits, prefer a duration that avoids busy polling. A timeout alone is no reason to shorten the next wait.

## Judge the child from evidence

A timeout establishes only that no mailbox update arrived during the interval. It does not establish child failure or blockage and does not justify interruption. Base intervention on actual child messages or status evidence.
