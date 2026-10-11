# Let blueprints guide refresh and declare necessary project migrations

These are the accepted design boundaries for project setup refresh and migration.
Rewrite both setup-project-agents and the project blueprint-authoring Skill from their intended
outcomes, preserving required behavior rather than their previous document structure. Setup uses
an ordered workflow with explicit work and completion conditions at each step.

Each Setup Authoring Blueprint carries its own refresh preferences, concrete authoring guidance,
focus, and relevant evidence. A blueprint collecting tools or code structure can warrant frequent
updates, while one establishing processes or durable context normally changes less often. Neither
blanket reauthoring nor blanket preservation serves both purposes. Blueprint guidance must equip
the Author with concrete reference directions while preserving judgment over formulation, consistent
with [ADR 0006](0006-preserve-agent-judgment-in-artifact-authoring.md).
The implementation scope includes updating
[the blueprint-authoring Skill](../../.agents/skills/write-setup-authoring-blueprints/SKILL.md)
to require these preferences and concrete guidance, as well as revising the existing blueprints.

Record only the SmartKit release version used by the latest successful project setup. A plugin
upgrade or failed setup does not advance that record. This reuses the plugin release identity from
[ADR 0004](0004-harness-adaptation-and-contract-versioning.md), rather than introducing an independent
configuration release version. Previously initialized projects without this record are blocked
until successful setup establishes a known baseline; do not guess their historical version.
Projects that have never used setup are not blocked merely for lacking that record.
This adds a baseline-establishment path beyond ADR 0004's historical hard cut.

Require project migration only for relevant changes to project requirements, generated results, or
their reading contract, including blueprint, configuration-format, and AGENTS.md changes. Pure
wording corrections and shared Skill changes alone do not require migration. A maintainer-facing
Skill in the SmartKit repository owns version advancement and the assessment of migration needs;
the hook consumes the declared result instead of inferring necessity from unequal version numbers.
Keep the current hook delivery and daily-check behavior. Migration guidance belongs in the setup
Skill's references and briefly states the main changes and required project actions; add migration
entries only when migration is necessary.

Retain necessary migration entries across releases. When a project skips versions, setup gathers
all applicable requirements between its recorded version and the target and satisfies them in one
upgrade, respecting required ordering without requiring installation of every intermediate plugin
release. Advance the project's setup version only after the entire upgrade succeeds.

Every full setup discovers and brings all project-defined Agents under setup management, preserving
their instructions, permissions, tool settings, and host-specific behavior. Material conflicts name
both sources, differing fields and values, consequences of the alternatives, and the user decision
needed; preserve those files and do not declare full success until the conflict is resolved.

Every full setup assesses models and reasoning settings against each Agent's role and current
availability, preferring a suitable successor with similar positioning. A tier change, material
cost increase, or change to an explicit project choice needs confirmation. Unverified model
availability keeps the existing selection and is reported without blocking other setup work;
known unusable settings stop the affected work. Local synchronization maps existing settings without
model reassessment. A new model release alone does not require project migration. The OtakuRoom
l10n Agent is an example, not evidence that its model is obsolete or permission to modify that project.
