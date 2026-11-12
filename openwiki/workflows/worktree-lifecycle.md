---
type: workflow
title: Worktree preparation and delivery
description: How SmartKit preserves inherited changes, prepares a linked checkout, and verifies the selected delivery or retention outcome.
tags: [worktrees, git, carry, delivery, recovery]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:28:05.666Z
sources:
  - id: openwiki-source-40233148014fc0db31f0eed6
    resource: repo://skills/create-worktree/scripts/prepare_configuration.py
  - id: openwiki-source-0d8b813831372d5ef0b6d05a
    resource: repo://skills/create-worktree/SKILL.md
  - id: openwiki-source-dbf8b736ac3ff33674b2c56e
    resource: repo://skills/finish-worktree/references/history.md
  - id: openwiki-source-ee4e69a52eb2685dcce4fb99
    resource: repo://skills/finish-worktree/SKILL.md
generated: { by: "smartkit", at: "2026-11-12T04:28:05.666Z" }
---

# Worktree preparation and delivery

[Create Worktree](../../skills/create-worktree/SKILL.md) verifies repository topology, checkout identity, and an immutable base. It reuses an existing task checkout when its branch, history, local changes, and ownership fit. A new checkout defaults to carrying source HEAD with staged, unstaged, and untracked nonignored state preserved as separate layers. Clean creation is an explicit choice. Both modes verify that the source stayed intact. Carry verification compares index semantics, bytes, file types, and modes. [Carry tests](../../tests/test_create_worktree_carry.py)

## Readiness after creation

Configuration readiness follows the chosen storage mode. Shared configuration arrives through Git or carry. Personal modes prepare selected, missing paths from the corresponding project directory in a verified checkout of the same repository. The helper rejects tracked or independently owned destinations, records origins, and links the selected files where supported or copies them when required. Environment preparation and host activation are separate readiness checks. A copied marker or receipt cannot prove that a capability works from the linked checkout. [Configuration helper](../../skills/create-worktree/scripts/prepare_configuration.py) · [Configuration tests](../../tests/test_worktree_configuration.py)

## Delivery and cleanup

[Finish Worktree](../../skills/finish-worktree/SKILL.md) verifies one selected outcome. It can retain the workspace, hand off by PR, fast-forward an authorized local target, return edits to another checkout while preserving its HEAD and index, or remove explicitly discarded work. The implementation workflow owns change verification. Evidence of an equivalent result already present on the target can establish delivery without a new commit.

Checkpoint Commits support intermediate recovery. When consolidation is expressly authorized, history preparation limits it to a task-owned, unpublished range, preserves a recovery ref, and verifies the replacement commit has the exact accepted tree. A commit hook changing that tree sends the result back for review. Cleanup inventories ignored and untracked data as well as tracked state, and retains a workspace when protected work or unique evidence would otherwise be lost. [History preparation](../../skills/finish-worktree/references/history.md) · [Worktree lifecycle glossary](../../contexts/worktree-lifecycle/GLOSSARY.md) · [Transfer tests](../../tests/test_finish_worktree_transfer.py)
