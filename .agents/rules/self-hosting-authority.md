# Self-Hosting Source Authority

Select the authoritative copy separately for every applicable SmartKit or project Rule and Skill. Source selection does not replace another artifact's responsibility.

## Prefer the corresponding checkout source

When it exists, use the artifact's source in the current checkout:

| Artifact | Checkout source |
| --- | --- |
| SmartKit Rule | `rules/*.md` |
| Project Rule | `.agents/rules/**` |
| SmartKit Skill exposed by plugin manifests | `skills/<name>/**` |
| Project Skill | `.agents/skills/**` |

Resolve an unqualified user reference to a SmartKit Rule or Skill to that source. An explicit reference to another copy selects that copy instead.

For a checkout-selected Skill, read its complete `SKILL.md` and every required referenced resource from the same source tree.

## Distinguish absence from a failed read

Use an installed, injected, packaged, or cached copy as a fallback only when the corresponding checkout source does not exist. A failed read does not establish absence: an existing source can be inaccessible or unreadable.

If required content remains unavailable, report the gap and stop dependent work under core governance's loading requirements.

## Keep ownership and composition unchanged

Source selection leaves ordinary applicability, Rule precedence, and Skill composition intact. Retain every independently applicable Rule and Skill; selecting one copy does not replace a distinct artifact.

`.agents/rules/project-policy.md` remains the sole owner of canonical ownership, contracts and exposure, translation, and verification.
