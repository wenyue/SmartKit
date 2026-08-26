# Third-Party Skill Policy

Strength: `Mandatory`

Scope: SmartKit-owned behavioral constraints for Skills supplied by third-party plugins or external
sources.

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
