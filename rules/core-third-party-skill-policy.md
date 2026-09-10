# Third-Party Skill Policy

Strength: `Mandatory`

Scope: SmartKit-owned behavioral constraints for Skills supplied by third-party plugins or external
sources.

## Ticket Granularity

When `$smartkit:to-tickets` drafts tickets:

- Give each cohesive tracer-bullet slice enough work to justify independent implementation and
  review, while keeping it reliably understandable, implementable, verifiable, and repairable by
  a current frontier LLM agent within one fresh context using the available tools. Treat that
  capability as the calibration point: the context limit is a practical capacity bound, not a
  reason to fragment work that fits comfortably.
- Place a ticket boundary where it provides independently meaningful acceptance, useful parallel
  execution, separation of materially different ownership or risk, a capability or context
  boundary, or a required green boundary in an expand-contract migration.
- Keep incidental or local prefactoring in the first ticket that consumes it. Give it a separate
  ticket only when it is independently reusable, needed by multiple later tickets, materially
  risky, or beyond the reliable capability or context bound.
- Before presenting the draft for approval, rebalance it in both directions: merge undersized or
  tightly coupled adjacent candidates, and split candidates beyond reliable frontier-agent
  capacity. Finish when every ticket has coherent scope and distinct acceptance criteria and every
  boundary is justified by the factors above. Preserve the Skill's presentation and publishing
  protocol without adding a `Why separate` output field.

## Artifact Language

- When `$smartkit:wait-what` re-pitches a message, write the re-pitch in Simplified Chinese.
- When a third-party Skill creates or edits `CONTEXT.md`, write every canonical term as
  `**{English term}（{Simplified Chinese term}）**:`. Add or rename both canonical names together.
- Use context-document terms only to interpret or explain language in direct user communication.
  Style those references as normal prose without special formatting merely because they are terms.
  Do not carry a definition or name from a context document into a Rule, Skill, contract, code,
  test, schema, configuration, validation, or Acceptance input unless an independent accepted
  source establishes the same meaning. Preserve emphasis when the source or author independently
  emphasizes a reference for contrast or stress, without stacking markup. Exclude code, commands,
  identifiers, and literal syntax.
- When a third-party Skill writes an ADR under `docs/adr/`, write the ADR in English.
