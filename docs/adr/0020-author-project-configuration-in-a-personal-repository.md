# Author project configuration in a personal repository

Status: Accepted source-authority decision

Personal project configuration needs to remain outside business repositories and be recoverable across machines. One user-owned private GitHub repository will hold configuration sources for multiple target projects, covering agent instructions, Skills, custom Agents, MCP declarations, and project-level Harness settings. The user selected authoring in that configuration repository and applying its sources to target projects over authoring in targets and exporting changes.

For projects using the configuration repository, setup continues inspecting the business project and writes revised source configuration in the configuration repository before applying it to the target. Target `.agents/config.json` holds the binding and target-local setup state; applying portable configuration preserves those fields.

Setup guidance distinguishes first setup from upgrades. First setup presents three complete choices: Project shared (configuration in the business repository), This machine only (local configuration excluded from business Git), or Separate configuration repository (a personal private GitHub source with target configuration excluded from business Git). Local exclusions use Git's `info/exclude`, preserving shared `.gitignore` rules and already tracked files. An existing project without a recorded mode is asked once during its first upgrade to this capability; later upgrades retain the recorded choice. Existing local bindings retain project-shared behavior.

Maintenance runs on explicit invocation. Invoking maintenance and synchronization includes updating the source working copy, editing source configuration, validating and applying it, committing the scoped changes, and pushing normally. Successful publication is required for complete maintenance; partial local success must be distinguished from remote synchronization.

First use supports connecting an existing personal private GitHub repository or creating one with the user-specified identity and name. Target-side edits can be explicitly adopted into the source repository after inspecting their differences, followed by the ordinary validation, application and publication workflow.

The managed-asset protection in [ADR 0001](0001-skill-snapshots-and-mcp-configuration.md) remains an application constraint. Complete workflow and acceptance details are in the [project configuration maintenance design](../superpowers/specs/2026-10-19-project-configuration-maintenance-design.md).
