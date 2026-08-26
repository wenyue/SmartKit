# ADR 0008: Use Probe-Qualified Soft Isolation for Rule and Skill Authoring

Status: Superseded by [ADR 0009](0009-separate-authoring-protocol-from-role-launch.md)

Soft isolation remains current only as the private shared-authoring Adapter defined by ADR 0009.
The universal role policy, tool-free roles, packet-only project evidence, replacement-content
Author, and per-version Reviewer below are historical.

Date: 2026-08-23

## Context

The original `write-rules-and-skills` workflow owned Rule and Skill authoring, setup
generation contracts, and shared portability qualification. Role freshness prevented an Agent from
judging its own work but did not establish what project or plugin context a fresh Agent received.
An independent nested Git clean room could create a stronger filesystem boundary, but its launcher,
snapshots, manifests, adoption copies, and temporary lifecycle added substantial machinery that did
not improve the semantic quality of the authored artifact.

Experiments with fresh Codex subagents showed that no-turn launches received the project entry file
and Skill catalog metadata without receiving parent turns, project Rule bodies, SmartKit Rule
bodies, Harness Rule bodies, or complete Skill bodies. This supports a smaller behavioral boundary,
provided every authoring run verifies the effective launch before relying on it and supplies all
semantic context explicitly.

## Decision

This ADR introduced prompt-qualified soft isolation as a behavioral boundary rather than a nested
Git workspace or security sandbox. ADR 0009 narrows that decision to the project-private shared
authoring Adapter.

The retained boundary uses a fresh no-inherited-turn launcher, explicit role prompts, exact
allowlists, declared semantic context, persistent identities, and a Controller audit of observable
operations after every callback. Adapter qualification must establish those properties for the
current run. Shared roles receive no source-project facts outside the declared dependency closure,
and they use no network or delegation. Missing semantic context or candidate-owned access is
requested explicitly without replacing a persistent role.

The shared Author edits canonical allowlisted candidate files directly. Reviewers remain read-only,
and every executable Acceptance attempt uses a fresh case-scoped Runner in disposable isolation.
Prompt compliance is portability evidence, not a claim that the host provides a hard sandbox or a
special enforcement hook.

## Consequences

Shared authoring retains explicit independence and portability evidence without a copied candidate
tree or mandatory temporary workspace. The Default Fresh Role Adapter and the complete current
authoring workflow are defined by ADR 0009.
