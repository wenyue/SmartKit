# ADR 0008: Use Probe-Qualified Soft Isolation for Rule and Skill Authoring

Status: Accepted

Date: 2026-08-23

## Context

The original `write-rules-and-skills` workflow owned ordinary Rule and Skill authoring, setup
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

SmartKit separates three entry points while preserving one Acceptance Standard:

- public `write-rules-and-skills` authors and qualifies an Ordinary Rule or Skill;
- project-private `write-setup-authoring-contracts` owns Setup Authoring Contracts under
  `setup-assets/blueprints/`; and
- project-private `write-shared-rules-and-skills` owns source-context exclusion, explicit shared
  dependencies, and portability qualification for shared SmartKit Rules and Skills.

Before the first Soft-isolated Agent in each top-level authoring workflow, the controller runs one
tool-free Soft-Isolation Probe through the same fresh, no-inherited-turn launch mechanism. The Probe
must observe its prompt control while failing to observe parent-turn content, project Rule bodies,
SmartKit Rule bodies, Harness Rule bodies, or complete Skill bodies. Project entry-file content and
its Rule or Skill pointers, plus Skill catalog metadata, may remain visible, but the Probe must not
follow those pointers. An unavailable launcher, an invalid control, forbidden Ambient Context, tool
use, file reading, or delegation fails the Probe, stops the workflow, and permits no fallback. The
same protocol runs in every Harness, so an unsupported Harness fails naturally rather than entering
a Harness-specific degradation branch.

Every Soft-isolated Agent receives all semantic input through one explicit Context Packet. Required
project or SmartKit context is selected and included by the controller; the Agent never discovers it
from the workspace. Missing context returns `CONTEXT_REQUIRED` to the controller, which either stops
or constructs a complete new packet for a new fresh Agent.

All semantic Authors, Behavior Controls, Pruners, Reviewers, and Acceptance Runners are
Soft-isolated. Ordinary Rule or Skill and Setup Authoring Contract workflows remain project-aware
only in the sense that their controllers select necessary project evidence and place it in the
Context Packet. Shared packets instead exclude source-project context except for the complete
original candidate and its owned resources. The Pruner stays with its correction loop, each
Candidate Revision receives a new Reviewer, and each Acceptance case receives a new Runner.

Authors, Pruners, and Reviewers receive no tools. A shared Author receives the complete original
candidate and owned resources in its Context Packet and returns complete replacement content or an
explicit file map. The controller writes that result unchanged to the canonical paths and verifies
the resulting content before deterministic machine checks. An Acceptance Runner also receives no
tools unless the artifact's observable contract requires them; a tool-enabled case first passes a
Probe using the same effective tool policy. Soft isolation remains a verified behavioral boundary,
not a filesystem or security boundary.

Candidate Revisions live in their canonical work area. Context Packets, Probe results, semantic
ledgers, Review Packets, and Acceptance results remain in Agent context rather than persistent
files. Acceptance observes the Runner's returned result; writing a temporary file adds evidence only
when filesystem behavior is itself part of the candidate's contract, in which case the candidate's
own test environment supplies the disposable workspace. The authoring workflow owns no mandatory
`.tmp` directory.

Actual fresh-Agent Probe and Acceptance runs are the primary behavior evidence. SmartKit keeps no
dedicated authoring fixture corpus or prose-structure test suite. Repository tests retain only the
public/private distribution assertion needed to protect installation boundaries; generic repository
checks continue to cover their existing contracts.

When a candidate changes the public authoring Skill, Reviewer contract, or Acceptance Standard, an
independent Soft-isolated Reviewer first qualifies a content-frozen Proposed Standard Change. The
candidate is then judged against the Previous Accepted Standard plus that Accepted Standard Change;
the candidate cannot weaken its own grader.

## Consequences

The design keeps independent semantic judgment and explicit portability evidence while removing the
nested Git launcher, SmartKit snapshot, Cleanroom Profile, Context Manifest, candidate copyback, and
mandatory temporary workspace. The Probe establishes only launch-time context behavior; tool access
would weaken that evidence, so semantic roles are tool-free by default and exceptional tool-enabled
Acceptance is qualified separately.

This ADR partially supersedes ADR 0002's single shared workflow and ADR 0006's statement that one
Hybrid Skill owns every authoring lifecycle. Their owner gate, semantic models, pruning, machine
validation, review, Acceptance, and correction principles remain in force where this ADR does not
replace their routing or context assumptions.
