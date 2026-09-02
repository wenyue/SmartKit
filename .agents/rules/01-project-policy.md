# Project Policy

**Strength:** Mandatory  
**Scope:** Project-owned generated, delivered, or installed surfaces; setup-managed state;
current-contract removal; public exposure; and verification of those changes. The canonical
ownership, contracts and exposure, and verification obligations below do not apply to work owned by
`.agents/skills/write-shared-rules-and-skills/**` or
`.agents/skills/write-setup-authoring-contracts/**`.

## Canonical ownership

Each affected generated, delivered, or installed surface must have one canonical owner. Change its
canonical input and use the owning generator or synchronizer. Preserve these source mappings:

- `VERSION` -> `scripts/sync_plugin_version.py`
- `mcp/registry.json` -> `scripts/sync_mcp_adapters.py`
- `agents/registry.json` or `agents/source/` -> `scripts/sync_agent_adapters.py`
- `rules/registry.json` -> `scripts/sync_cursor_rule_adapters.py --update`

Setup-managed writes and deletions must remain within declared ownership, preserve unrelated or
user-owned state and secrets, and stop on an ownership or digest conflict.

## Contracts and exposure

Removing a current contract must remove its retired implementation, documentation, tests, and
handling together. Add compatibility only when an accepted current contract requires it.

Deliver and expose surfaces through their declared owners and routes. A target state must not become
canonical plugin authority, and public manifests must expose only declared public surfaces.

## Verification

After changing a project-owned English Rule or Skill, use `smartkit:translate-agent-artifacts` to
synchronize its Simplified-Chinese documentation mirror.

Run proportionate, non-fixing checks required by the affected owners and surfaces, review generated
diffs, and run `git diff <comparison-point> --check`. Required checks must pass before completion or
success is reported. If a required check fails or cannot run, correct any in-scope cause and rerun it;
otherwise, stop and report the failure or blocker without claiming completion.
