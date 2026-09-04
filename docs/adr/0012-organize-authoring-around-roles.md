# Organize Rule and Skill Authoring Around Roles

Status: Accepted

Date: 2026-09-04

## Context

The public Rule and Skill authoring workflow had accumulated contract-oriented references whose
responsibilities crossed one another. The Controller had to load writing, review, lifecycle, and
failure-recovery details; Reviewers produced repeated reports; and protocol-specific terminology
made the workflow harder for both people and capable Agents to understand and maintain.

## Decision

Organize the workflow around its actual roles. The main Skill belongs to the Controller and contains
only alignment, delegation, validation, review-round management, a pointer to conditional review
orchestration, and handoff. A Controller-owned reference holds those conditional topology,
brief-correction, user-input, and runtime-evidence branches. Separate references belong to the
Author, Reviewers, and Runner. Every Reviewer loads one common contract plus its assigned
professional contract or contracts, so shared conduct has one home while professional judgment
stays separated. Reviewers follow locators to stable evidence; the Controller routes only
irrecoverable session context to the perspective that needs it. Role principles precede execution
details, common terminology is preferred, and concise concepts such as `elegant` are left to a
frontier Agent's trained judgment.

Keep three professional review perspectives: Quality, Change, and Correctness. Integrated Review
assigns one Integrated Reviewer the common contract and all three professional contracts, reporting
each perspective separately. Independent Review assigns three fresh identities the common contract
and one professional contract each. Use Independent Review for self-hosting, broad, high-risk, or
materially uncertain changes; an Integrated Reviewer may require that switch when the integrated
topology is no longer appropriate. Reviewers communicate directly with the Author. The first round
may report the full relevant problem set; later rounds tighten their threshold, and the workflow
stops after at most three rounds. The Author remains responsible for the whole Candidate and may
accept, partly accept, or decline findings with evidence-based reasons.

When static Correctness Review needs runtime evidence, a separate Runner executes and reports facts;
the same reviewing identity applying Correctness judges those facts. Preserve automated validation,
a single writer, read-only Reviewers, lightweight baseline and fingerprint checks, safe cleanup, and
concise handoff, but remove bespoke proof profiles, incident-equivalence recovery, and detailed
terminal taxonomies. The workflow returns only `COMPLETE`, `NEEDS_INPUT`, or `BLOCKED`.

ADR 0011 remains authoritative for unified discovery and evidence qualification. This decision
replaces its inherited detailed authoring-runtime shape with the role-oriented workflow above.

## Consequences

The workflow spends less context on orchestration and more on the role currently doing the work.
Human maintainers can follow the same structure that Agents execute. Review coverage remains
constant while the topology scales its independence to the task; runtime separation also remains.
Repeated low-value findings, additive patching, and protocol sediment are bounded by role ownership,
direct communication, and the three-round limit.
