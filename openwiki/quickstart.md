---
type: quickstart
title: SmartKit repository quickstart
description: A maintainer's map of SmartKit's native plugin delivery, project configuration, workflows, and runtime checks.
tags: [quickstart, smartkit, architecture, maintenance]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:28:05.666Z
sources:
  - id: openwiki-source-927d2fc110b7f44c655a6628
    resource: repo://.agents/rules/self-hosting-authority.md
  - id: openwiki-source-4f2678f93d3fd3835f9f2909
    resource: repo://.github/workflows/test.yml
  - id: openwiki-source-3cb9558874c8cd84b2519171
    resource: repo://GLOSSARY-MAP.md
generated: { by: "smartkit", at: "2026-11-12T04:28:05.666Z" }
---

# SmartKit repository quickstart

WenYue SmartKit provides shared Rules, Skills, hooks, MCP declarations, and project setup for Codex, Cursor, GitHub Copilot, and Qoder on Windows and Linux. The repository is both the canonical plugin source and a self-hosting project with its own maintainer guidance. Installation and host prerequisites are in the [README](../README.md#install-the-plugin).

For a SmartKit Rule or Skill referenced without a specific copy, this checkout's corresponding source takes priority when it exists. The selected Skill and required references come from the same source tree. The project entry locates maintainer Rules. The glossary map locates terms and accepted decisions across SmartKit, Authoring Evaluation, and Worktree Lifecycle. [Project entry](../AGENTS.md) · [Self-hosting authority](../.agents/rules/self-hosting-authority.md) · [Glossary map](../GLOSSARY-MAP.md) · [ADRs](../docs/adr/)

## Find the relevant system

| Task | Page |
| --- | --- |
| Change a native plugin manifest, registry, adapter, or vendored Skill | [Plugin distribution](architecture/plugin-distribution.md) |
| Trace how Rules load or restore after compaction | [Rule delivery](architecture/rule-delivery.md) |
| Follow project setup, a migration, or generated file ownership | [Project setup](configuration/project-setup.md) |
| Choose configuration storage or inspect restore and publication behavior | [Storage and synchronization](configuration/storage-and-sync.md) |
| Trace startup checks, CodeGraph readiness, or session evidence | [Session readiness and diagnosis](operations/session-readiness.md) |
| Inspect local diff hosting, artifact previews, or login startup | [Local web service](operations/local-web.md) |
| Understand linked checkout preparation, delivery, and cleanup | [Worktree lifecycle](workflows/worktree-lifecycle.md) |
| Trace a Rule or Skill from design through acceptance | [Artifact authoring](workflows/artifact-authoring.md) |
| Inspect pinned review evidence, PR delivery, and Viewed state | [Human review](workflows/human-review.md) |
| Retrieve repository context or refresh the Wiki | [OpenWiki integration](integrations/openwiki.md) |

## Verify against the owning surface

The repository CI verifies synchronized versions, runs the Python unittest suite on Linux and Windows, and checks whitespace. Focused suites identify failures at individual boundaries, such as plugin manifest wiring, setup transactions, and web service ownership. The generated Wiki links those contracts and tests. [CI workflow](../.github/workflows/test.yml) · [Tests](../tests/)
