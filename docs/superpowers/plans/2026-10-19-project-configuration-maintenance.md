# Project Configuration Maintenance Implementation Plan

> **For agentic workers:** Implement the accepted design task by task. Keep the Git mechanism, setup integration, and Skill authoring under their respective owners. Use tests before behavior changes and the repository's public authoring workflow for Skill documents.

**Goal:** Maintain personal project Agent configuration in an authenticated private GitHub repository shared by multiple projects.

**Architecture:** A persistent repository runtime owns Git access and scoped publication. The public setup workflow owns source projection through its existing planner, transaction, configuration schema, and rendering ownership. Explicit maintenance uses that public workflow; setup freezes source evidence and saves accepted generated output to the source before target application.

**Tech Stack:** Python 3.8-compatible standard library, Git, GitHub CLI, unittest, existing setup transaction and renderers.

## 1. Configuration contract

- [x] Add failing schema/parser tests for optional maintenance (local or repository binding), malformed bindings, and project-native setting declarations.
- [x] Extend `models.py`, `catalog.py`, and `project-config.schema.json`; retain old unbound inputs.
- [x] Run `python -m unittest discover -s tests -p test_setup_catalog.py`.

## 2. Source projection and setup integration

- [x] Add failing tests in `tests/test_project_configuration.py` for source import, reserved local fields, target drift, explicit adoption, deletions, symlinks, and generated-output handoff.
- [x] Add `agents_setup/project_configuration.py`: entries contain an explicit file manifest plus portable `.agents/config.json`; compare target/source/last applied evidence before writes. Reuse `build_plan` and `apply_plan`.
- [x] Add public workflow commands for binding, checking, applying, adoption and publication. Preserve source on partial target failure and preserve target/local commit on publication failure.
- [x] Freeze source entry fingerprints in setup requests; write accepted generated files to source before applying the normal setup plan. Keep `setupVersion` with existing finish.
- [x] Render declared project settings with existing structured-field ownership and update broad local sync.
- [x] Run projection, setup workflow, rendering, and sync tests.

## 3. Private repository mechanism

- [x] Write real-local-Git tests in `tests/test_project_config_repository.py` before implementing `runtime/project_config/repository.py`.
- [x] Validate GitHub identity, private personal repository, branch and entry; connect/create persistent checkouts with existing credentials.
- [x] Fetch/fast-forward safely; commit exact paths while preserving unrelated staged content; verify hook scope and outgoing commits before normal push.
- [x] Verify remote reachability and retry retained commits without force/reset/stash.

## 4. Agent-facing entry points

- [x] Use one resident Author per Candidate with baseline capture and independent Quality, Change and Correctness review, three-round limit.
- [x] Revise `setup-project-agents` entry and affected references: separate first setup/upgrade, ask maintenance mode once, use accepted source and Git boundaries.
- [x] Add exactly one `maintain-project-config` Skill: check, maintain-and-sync, explicit adoption; register it in `skills/registry.json`.
- [x] Synchronize final English Skill documents to specified Chinese mirrors; update both READMEs.

## 5. Completion

- [x] Run required Candidate checks, plugin registry/manifests checks and `python scripts/sync_plugin_version.py --check`.
- [x] Run `python -m unittest discover -s tests -p 'test_*.py'` and scoped `git diff HEAD --check`.
- [x] Assess migration: old configs remain readable; first full setup asks only when maintenance is absent. Leave published version history unchanged unless a new release target is established.
- [x] Review the final diff preserving pre-existing staged changes. Leave this implementation uncommitted; no real GitHub repository is created or pushed as part of testing.

## Verification result

Implementation completed in the working tree on 2026-10-19. Independent Quality, Change, and Correctness reviews passed for both Skill Candidates. The complete Python 3.8 suite ran 781 tests successfully with 5 skips; the version synchronizer check, source and Chinese Candidate checks, plugin/mirror checks, and whitespace checks passed. The source-fetch fixture now includes the shared runtime, and incomplete runtime packages are explicitly refused.

Git integration exercised disposable local repositories with GitHub API behavior mocked. Live GitHub creation/publication, native Windows execution, and a complete natural-language setup session were not exercised. The plugin remains at 1.2.22; no release, installation, task commit, or real remote push was performed. Existing unbound configuration remains readable, and maintenance selection occurs on an explicit full setup when absent.
