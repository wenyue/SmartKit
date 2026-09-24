# Apply Versioned Patches Through the External Skill Updater

Status: Accepted

Date: 2026-09-23

SmartKit uses its external Skill updater to derive selected upstream Skills from a
fixed upstream revision and version-controlled patches. This preserves upstream expression
and an inspectable local delta while allowing SmartKit-specific behavior without maintaining
a separate Markdown diff ledger. Source, revision, and license provenance remain with the
existing registry and lock owners; patch files describe the actual modifications and may carry
concise rationale.

On 2026-09-24, this ownership decision was extended to both Matt and Ponytail Skills:
Skill-specific SmartKit adaptations belong in patches to the relevant Skill or its owned
resources, including Ponytail's configuration-reading instructions. This keeps the adapted
behavior with the workflow that uses it and makes the local delta reviewable during upgrades.
Shared constraints retain one common policy owner. Migrating an override preserves its accepted
meaning and coverage; retiring a constraint requires a separate user decision.

Later on 2026-09-24, the user explicitly retired the remaining context-document consumer
restrictions: requiring an independent accepted source before reusing a glossary definition in
implementation or contracts, and requiring ordinary prose formatting for glossary terms.
These restrictions are not migrated to patches or other Rules. With the Skill-specific
adaptations already owned by patches, `core-third-party-skill-policy.md` and its registry entry
and Chinese mirror are retired. The upstream glossary guidance in `domain-modeling` remains.

Patches are applied and the resulting Skills verified before final snapshot hashes are recorded
and outputs installed. A patch-application failure preserves the previous snapshots and lock.
During an authorized upgrade, an Agent may adapt patches to changed upstream text while
preserving accepted SmartKit behavior and completing verification. New behavioral trade-offs
require a user decision; an upgrade does not authorize silently dropping a patch or changing
its intended result.

Required per-task Ponytail loading belongs to
[rule-code](../../skills/rule-code/SKILL.md#ponytail-loading), matching the coding scope of
[Ponytail](../../skills/ponytail/SKILL.md). Ponytail remains a task Skill for coding simplification;
it does not replace the cross-task principles in
[Reasoning Workflow](../../rules/core-reasoning-workflow.md) and
[Agent Personality](../../rules/core-personality.md). Off disables Ponytail's continuous
simplification while those general principles remain applicable.

The unchanged state Hook separately reaches Ponytail's
[inheritance protocol](../../skills/ponytail/SKILL.md#persistence) before every delegation,
including noncoding work and off mode. This independent route preserves delegation state without
requiring per-task Ponytail loading for ordinary noncoding work.

This decision replaces only the requirement in
[ADR 0004](0004-harness-adaptation-and-contract-versioning.md) that external snapshots retain
unmodified upstream wording. Its requirement to use the owning updater remains. Snapshots
without patches continue to retain upstream content. The selected Skills, their public names,
and their activation behavior are separate adoption decisions.
