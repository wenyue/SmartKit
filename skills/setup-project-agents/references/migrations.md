# Project Migrations

Read the entries selected by `start` before generating project content. The machine-readable
declarations in `setup-assets/catalog/migrations.json` identify releases that require project
changes; a newer SmartKit release alone does not require migration. Apply every entry after the
project's successful `setupVersion` through the selected source release, in order, in one full
setup. No intermediate plugin installation is needed.

An existing `.agents/smartkit.lock.json` without `setupVersion` needs a full setup to establish its
baseline. Preserve the existing ownership record and project content; do not guess its prior
version. A project without that initialization record is not blocked by the setup check.

Keep historical necessary entries. Each entry explains the change and the required project action;
shared Skill changes and wording-only edits do not belong here.

## Project refresh and version baseline

**Release: 1.2.19.** Blueprints now distinguish frequently refreshed project facts from stable
workflow decisions. Full setup evaluates every declared artifact and project Agent, preserving
valid content instead of requiring new wording. Successful setup records its source release.

Run full setup once. Reconcile existing Rules and Skills with each blueprint's refresh guidance;
retain project additions and valid obligations. Discover custom Agents, preserve their behavior
when bringing them into canonical project configuration, and assess their model and reasoning
settings. Resolve reported conflicts, then let successful `finish` write `setupVersion`.
