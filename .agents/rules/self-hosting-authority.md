# Self-Hosting Source Authority

## Select Each Artifact's Source

For every independently applicable SmartKit or project Rule or Skill, use its corresponding
source in the current checkout when it exists:

- SmartKit Rules: `rules/*.md`
- project Rules: `.agents/rules/**`
- SmartKit Skills exposed by plugin manifests: `skills/<name>/**`
- project Skills: `.agents/skills/**`

Resolve unqualified user references to SmartKit Rules or Skills to these checkout sources.
An explicit reference to another copy selects that copy instead.

Use an installed, injected, packaged, or cached copy as a fallback only when the corresponding
checkout source does not exist. A failed read does not establish absence: an existing source can
be inaccessible or unreadable. When required content remains unavailable, report it and stop
dependent work under core governance's loading requirements.

For a Skill resolved to the checkout, read its complete `SKILL.md` and every required referenced
resource from that same source tree.

## Preserve Policy Responsibilities

Source selection leaves ordinary applicability, Rule precedence, and Skill composition
unchanged. Retain every independently applicable Rule and Skill; selecting one artifact's copy does
not replace a distinct artifact.

`.agents/rules/project-policy.md` remains the sole owner of canonical ownership, contracts and
exposure, translation, and verification.
