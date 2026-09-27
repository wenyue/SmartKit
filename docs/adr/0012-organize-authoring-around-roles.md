# Organize Rule and Skill Authoring Around Roles

Status: Accepted

Date: 2026-09-04

Amended: 2026-09-25

## Context

The public Rule and Skill authoring workflow had accumulated contract-oriented references whose
responsibilities crossed one another. The Controller had to load writing, review, lifecycle, and
failure-recovery details; Reviewers produced repeated reports; and protocol-specific terminology
made the workflow harder for both people and capable Agents to understand and maintain.

## Decision

Organize the workflow around its actual roles. The main Skill states the intended artifact quality
and the normal collaborative path. The Controller contract owns assignment, context delivery,
topology, version consistency, validation, clarification, and handoff. Correctness owns
runtime verification within the job's frozen authority and resource bounds. Separate references
belong to the Author, Reviewers, and Runner. Every Reviewer loads one common contract plus its assigned
professional contract or contracts, so shared conduct has one home while professional judgment
stays separated. Controller, Author, and Reviewer contracts do not cross-reference one another;
the Skill entry supplies role-document navigation. Each role addresses shared subjects from its
own concerns, with its necessary evidence and handoffs. The Author receives requirements and their reasons, accepted decisions,
relevant domain evidence, and original exchanges when a summary would lose necessary meaning.
Neither a brief alone nor full conversation inheritance is a universal context requirement.

The shared glossary, `skills/write-rules-and-skills/references/shared-terms.md`, gives roles
common meanings for artifact and workflow terms, including the different kinds of Skills. It
contains terminology rather than design guidance or review criteria. Loading decisions belong to
the Author's reading-path design; their effects on the reader belong to Quality's assessment.
Several roles needing a topic does not give the glossary ownership of their methods. Coordination,
existing governance, and packaging policies retain their owners and supported loading routes.

Authors own content selection, responsibility allocation, and composition. They organize each
artifact around the task and consequential decisions its reader must handle.
Quality evaluates useful guidance and the complete reading path using the artifact's form, rather
than imposing a common outline. Representative examples clarify difficult boundaries; neither
length quotas nor compliance inventories establish good writing. Reviewers may illustrate an
evidenced problem with optional examples or suggestions, while Authors choose the repair.

Keep three professional review perspectives: Quality, Change, and Correctness. Integrated Review
assigns one Integrated Reviewer the common contract and all three professional contracts, reporting
each perspective separately. Independent Review assigns three fresh identities the common contract
and one professional contract each. Use Independent Review for self-hosting, broad, high-risk, or
materially uncertain changes; an Integrated Reviewer may require that switch when the integrated
topology is no longer appropriate. Reviewers communicate directly with the Author. The material
acceptance bar stays fixed across rounds; repeated preferences and unsupported reopened findings
do not consume further rounds. The workflow uses a finite budget, defaulting to three review rounds;
accepted extensions set a new finite bound. It reports unresolved material defects when the budget
is exhausted or progress is no longer plausible, rather than lowering the bar to pass. The Author
remains responsible for the whole Candidate and may
accept, partly accept, or decline findings with evidence-based reasons.

When Correctness needs runtime evidence, it directly commissions a separate Runner and judges the
returned observations. Correctness owns scenario selection, assessment criteria, independent
execution, and safe finalization; the Controller retains overall job authority and closure. A Runner
may delegate within the tested task's grants while keeping the outer authoring roles separate.
Preserve automated validation, a single writer, read-only Reviewers, lightweight baseline and
fingerprint checks, safe cleanup, and
concise handoff, but remove bespoke proof profiles, incident-equivalence recovery, and detailed
terminal taxonomies. The workflow returns only `COMPLETE`, `NEEDS_INPUT`, or `BLOCKED`.

ADR 0011 remains authoritative for unified discovery and evidence qualification. This decision
replaces its inherited detailed authoring-runtime shape with the role-oriented workflow above.

## Consequences

The workflow spends less context on orchestration and more on the role currently doing the work.
Human maintainers can follow the same structure that Agents execute. Review coverage remains
constant while the topology scales its independence to the task; runtime separation also remains.
Repeated low-value findings, additive patching, and protocol sediment are bounded by role ownership,
direct communication, and a finite, progress-aware iteration budget.

The 2026-09-25 amendment rebuilds each role around the decisions it owns, narrows the shared
resource, and fixes the Quality acceptance bar. More
coverage requirements had made it easier to add prose than to demonstrate useful task guidance.
The revised division gives each role a concrete editorial responsibility without adding a common
checklist. Representative authoring and reader-use observations can calibrate the workflow;
review approval alone establishes neither general reliability nor improvement over a baseline.

The 2026-09-16 amendment removes the separate review-escalation reference and the Controller's
runtime-request relay. Conditional behavior now stays with the role responsible for it. This
reduces cross-role loading and handoffs at the cost of giving Correctness bounded execution
management duties as well as evidence judgment. Independent execution remains separate from
judgment; an additional runtime-evidence reviewer would duplicate Correctness's responsibility.
