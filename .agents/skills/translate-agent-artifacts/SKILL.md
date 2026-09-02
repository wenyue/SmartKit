---
name: translate-agent-artifacts
description: Synchronize required Simplified-Chinese docs mirrors after additions, changes, moves, or retirements of canonical English first-party Rules or Skills are complete.
---

# Translate Agent Artifacts

The hosting Agent establishes one frozen translation job, translates the complete mirror set,
performs the complete semantic coverage and standalone readability passes, then runs only the
required deterministic, non-fixing project validation commands and reports their exits.
This Skill grants only the frozen mirror operations and required deterministic validation; it
grants no commit, push, publication, release, installation, or other downstream delivery or effect.

## Freeze the complete job

1. Discover and read the governing project translation and verification policy by concern, without assuming a specific Rule identifier, title, or path.
2. Establish from the accepted English-change handoff and current repository change evidence the complete affected set of added, changed, moved, or retired canonical English sources, including the exact source endpoints of every move.
3. Discover the current environment-owned sources for mirror mappings, protected surfaces, and owner-required validation. Establish every required final source-to-mirror mapping and every obsolete mapping; read every affected final English source and existing affected mirror; and include every missing required mirror for creation, both mirror endpoints corresponding to a source move, and every obsolete mirror for removal.
4. Freeze the governing policy, source changes, mappings, protected surfaces, validation requirements, and exact mirror update, create, move, and removal scope as one indivisible job. Name both mirror endpoints of every move.

Final English first-party Rules and Skills are the sole semantic authority. Existing mirrors may provide continuity for readers.

An applicable `CONTEXT.md` may be consulted only for established Chinese wording that helps readers understand the source. It is a nonnormative wording aid, not semantic evidence: it cannot add, change, disambiguate, or resolve English meaning.

If the governing policy, accepted change evidence, and current environment-owned sources cannot establish the complete affected set, final or obsolete mappings, protected surfaces, required validation, or exact move endpoints, or if an English source is ambiguous or incomplete, stop before delivering a partial translation. Return the missing information or source uncertainty to the appropriate owner rather than resolving it in Chinese.

## Translate the whole frozen job

Use the frozen source changes, mappings, policy, protected surfaces, and exact mirror operation scope to:

- update, create, move, or remove every authorized mirror needed to make the complete set match the final English source set, never silently processing only a subset;
- use no network;
- treat final English as the sole semantic authority and existing mirrors only as continuity for readers;
- consult an applicable `CONTEXT.md`, if useful, only as the nonnormative wording aid limited above;
- treat each mirror as documentation for human readers, never as instructions to execute;
- write plain, idiomatic, easy-to-understand Simplified Chinese while preserving the complete meaning and force of the English;
- translate commands, requirements, and imperatives as reader-facing content, naturally and without weakening their force;
- preserve the source's basic block and Markdown organization, emphasis, paragraph and block boundaries, and every policy-protected literal or structured surface;
- freely reorder, split, merge, or rephrase sentences only within each corresponding prose paragraph when that improves Chinese readability, without unsupported additions;
- expand wording when explanation improves comprehension rather than optimizing for brevity;
- perform a complete final-source-by-final-source semantic coverage and standalone readability pass; and
- record every changed, created, moved, or removed mirror path, including both endpoints of each move, the completion and outcome of both required whole-set passes, and any blocking mapping or source uncertainty.

Proceed to deterministic project validation only after both required whole-set passes succeed with
no blocker. If either pass is incomplete or indeterminate, stop and report the blocked complete job.

## Run deterministic project validation

After both whole-set passes succeed, run every required deterministic, non-fixing project validation
command against the changed documentation. Record each command and its exit. These commands are
mechanical project checks, not translation review, and they do not expand the frozen translation
authority.

Complete only when every required command passes. If a command fails or cannot run, correct each
cause within the frozen mirror operation scope. After any correction, repeat both required whole-set
passes and rerun every required command. If no such in-scope correction can resolve the failure,
stop and report it without claiming completion.

## Report the outcome

Report every changed, created, moved, or removed mirror path, including both endpoints of each move,
the outcome of both whole-set passes, and each required project validation command and exit. Report
success only after both passes succeed and every required command passes. When blocked, report the
missing mapping, source uncertainty, incomplete pass result, or command failure; the resolution
required; and the responsible owner without presenting a partial mirror set as complete.
