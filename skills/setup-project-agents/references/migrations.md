# Project Migrations

Version-specific migration guides live in `migrations/`, beside this file, with one `<version>.md` file per release that requires migration. Use the versions selected by `start` to find and read the corresponding files from the selected source before generating project content. The machine-readable declarations in `setup-assets/catalog/migrations.json` identify releases that require project changes; a newer SmartKit release alone does not require migration. Apply every entry after the project's successful `setupVersion` through the selected source release, in order, in one full setup. No intermediate plugin installation is needed.

An existing `.agents/smartkit.lock.json` without `setupVersion` needs a full setup to establish its baseline. Preserve the existing ownership record and project content; do not guess its prior version. A project without that initialization record is not blocked by the setup check.

Keep historical necessary declarations and their guide files. Each version file explains the change and the required project action; shared Skill changes and wording-only edits do not belong here. Add new version guides to the directory without adding a release list to this entry file.
