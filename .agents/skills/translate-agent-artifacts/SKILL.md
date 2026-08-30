---
name: translate-agent-artifacts
description: Translate completed canonical English first-party Rules or Skills into their required Simplified-Chinese docs mirrors.
---

# Translate Agent Artifacts

The hosting Agent establishes one frozen translation job, translates the complete mirror set,
performs the complete semantic coverage and standalone readability passes, then runs only the
required deterministic, non-fixing project validation commands and reports their exits.

## Freeze the complete job

1. Discover and read the applicable project documentation and translation policy by concern, without assuming a specific Rule identifier, title, or path.
2. Establish from the canonical project documentation the complete affected set of final English sources and every required source-to-mirror mapping.
3. Read every selected English source and each existing mapped mirror. Include every missing required mirror for creation in the same affected set.
4. Freeze the sources, mappings, protected surfaces, applicable policy, validation requirements, and exact mirror write scope as one indivisible job.

Final English first-party Rules and Skills are the sole semantic authority. Existing mirrors may provide continuity for readers.

An applicable `CONTEXT.md` may be consulted only for established Chinese wording that helps readers understand the source. It is a nonnormative wording aid, not semantic evidence: it cannot add, change, disambiguate, or resolve English meaning.

If the governing policy cannot determine the complete affected set, mapping, protected surfaces, or required validation, or if an English source is ambiguous or incomplete, stop before delivering a partial translation. Return the missing information or source uncertainty to the appropriate owner rather than resolving it in Chinese.

## Translate the whole frozen job

Use the frozen sources, mappings, policy, protected surfaces, and exact mirror write scope to:

- update or create every authorized mirror in the complete set, never silently translating only a subset;
- use no network;
- treat final English as the sole semantic authority and existing mirrors only as continuity for readers;
- consult an applicable `CONTEXT.md`, if useful, only as the nonnormative wording aid limited above;
- treat each mirror as documentation for human readers, never as instructions to execute;
- write plain, idiomatic, easy-to-understand Simplified Chinese while preserving the complete meaning and force of the English;
- translate commands, requirements, and imperatives as reader-facing content, naturally and without weakening their force;
- preserve the source's basic block and Markdown organization, emphasis, paragraph and block boundaries, and every policy-protected literal or structured surface;
- freely reorder, split, merge, or rephrase sentences only within each corresponding prose paragraph when that improves Chinese readability, without unsupported additions;
- expand wording when explanation improves comprehension rather than optimizing for brevity;
- perform a complete source-by-source semantic coverage and standalone readability pass; and
- record every changed or created mirror path, the completion and outcome of both required whole-set passes, and any blocking mapping or source uncertainty.

Proceed to deterministic project validation only after both required whole-set passes succeed with
no blocker. If either pass is incomplete or indeterminate, stop and report the blocked complete job.

## Run deterministic project validation

After both whole-set passes succeed, run every required deterministic, non-fixing project validation
command against the changed documentation. Record each command and its exit. These commands are
mechanical project checks, not translation review, and they do not open a content-correction cycle.

Complete only when every required command passes. If any command fails or cannot run, stop and
report the failure without patching the mirrors.

## Report the outcome

Report every changed or created mirror path, the outcome of both whole-set passes, and each required
project validation command and exit. Report success only after both passes succeed and every
required command passes. When blocked, report the missing mapping, source uncertainty, incomplete
pass result, or command failure; the resolution required; and the responsible owner without
presenting a partial mirror set as complete.
