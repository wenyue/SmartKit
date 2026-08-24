---
name: write-shared-rules-and-skills
description: Author or materially revise a cross-project SmartKit Rule or Skill through probe-qualified soft isolation and explicit portability evidence; excludes project-local artifacts and Setup Authoring Contracts.
---

# Write Shared Rules and Skills

Own source-context exclusion, explicit shared dependencies, and portability proof for one shared
SmartKit Rule or Skill. The public `write-rules-and-skills` Skill owns ordinary authoring, Pruning,
machine validation, Semantic Review, Acceptance, and correction. This project-private Skill supplies
the stricter shared Context Packets and shared pass conditions.

When the candidate changes the public authoring Skill, its Reviewer contract, or the Acceptance
Standard, read [`references/standard-change.md`](references/standard-change.md) completely.

## Qualify soft isolation

Apply the public Skill's Soft-Isolation Probe before constructing any semantic packet. The Probe
must run through the same fresh-Agent launch mechanism later used by the Author, Pruner, Reviewer,
and Acceptance Runners. Any project Rule body, SmartKit Rule body, Harness Rule body, complete Skill
body, inherited parent content, invalid control, tool use, file read, delegation, or unavailable
fresh launch fails the workflow without fallback.

## Construct the shared authoring input

The controller may inspect the source repository only to gather accepted intent, the complete
candidate and owned resources, public authoring guidance, explicitly selected SmartKit shared Rules
or Skills, declared shared dependencies, and portability evidence. It must exclude source-project
Rules, project-specific policy, undeclared files, author reasoning, and unrelated conversation from
every semantic packet.

Require one representative target context. Add a second materially different context only when
behavior depends on a variable project seam and direct evidence is insufficient. A context that
differs only in names or layout is not additional evidence. Every candidate dependency must appear
in the explicit packet; an undeclared dependency is a blocking portability failure.

## Invoke the public workflow

Invoke `write-rules-and-skills` as the controller and reuse the current top-level Probe `PASS`. Its
Soft-isolated, tool-free Author receives the shared authoring input and returns complete replacement
content or `CONTEXT_REQUIRED`. The controller applies returned content unchanged to the canonical
source paths and verifies it. All semantic corrections return to the Author; the controller never
edits their meaning.

Use a different Soft-isolated Pruning Agent, a new Soft-isolated Reviewer for each Candidate
Revision, and a new Soft-isolated Acceptance Runner for every case. Each role receives a complete
role-specific Context Packet and no ambient source-project evidence. Tool-enabled Acceptance remains
subject to the public Skill's matching Probe and stop rules.

## Prove portability and finish

Shared Acceptance requires the current Probe `PASS`, complete declared dependency closure, and the
representative target evidence in addition to every public gate. A Candidate Revision that depends
on an invented or source-project-only fact fails portability even if its ordinary gates pass.

Success requires the public gates and shared portability checks to pass for the same canonical
Candidate Revision. Report the Probe result, declared dependencies, representative contexts,
machine commands and exits, semantic verdicts, corrections, and untested surfaces. Keep packets and
evidence in active Agent context. Publication, commit, push, and release remain with their existing
owners.
