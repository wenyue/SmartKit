# Self-Hosting Source Authority

**Strength:** Mandatory
**Scope:** Every task in this SmartKit repository.

This Rule owns only self-hosting copy authority. For every independently applicable SmartKit or
project Rule or Skill, use its corresponding current-checkout source when it exists:

- SmartKit Rules: `rules/*.md`
- project Rules: `.agents/rules/**`
- SmartKit Skills exposed by plugin manifests: `skills/<name>/**`
- project Skills: `.agents/skills/**`

Resolve an unqualified user reference to a SmartKit Rule or Skill as the corresponding
current-checkout source above. An explicit reference to another copy identifies that copy instead.

An installed, injected, packaged, or cached copy is a fallback only when the corresponding checkout
source does not exist. For a checkout-resolved Skill, read its complete `SKILL.md` and every
required referenced resource from the same checkout source tree.

Copy resolution preserves ordinary applicability, Rule strength and precedence, and Skill
composition. Retain every independently applicable Rule and Skill; resolving one artifact's copy
does not substitute for a distinct artifact.

`.agents/rules/01-project-policy.md` remains the sole owner of canonical ownership, contracts and
exposure, translation, and verification.
