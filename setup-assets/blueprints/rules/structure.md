# Structure

## Purpose and evidence

For an independent request to create or revise `.agents/rules/structure.md`, use `write-rules-and-skills` to produce one target-owned Rule titled `Structure`. The Rule ranks valid choices of location, responsibility seam, or navigation entry under applicable policy and installed SmartKit governance. Ownership, dependency permission, delivery, installation, and exposure remain with their policy owners.

Establish the target repository from the accepted request and current evidence. The Author discovers and qualifies relevant target evidence: entry guidance and applicable Rules; accepted Issues, Specs, and ADRs; callers, imports, consumers, tests, schemas, registries, generators, runtime entries, and canonical documentation routes. Reuse qualified caller-supplied evidence and discover missing facts directly; the caller need not prepare an evidence packet. Qualify sources by owner and provenance. Names, co-location, directory and package boundaries, and machine-local state are clues, not authority; existing Rule text is regression evidence, not design authority.

Classify each recommendation as preserve, change, add, retire, or non-goal. Changes, additions, retirements, and exceptions require accepted intent and qualified evidence; otherwise preserve the supported recommendation or stop.

## Choices to guide

Every recommendation resolves a real competing choice. State its condition, ranked outcome, and evidence owner, with the scope, predicate, and reason for any exception. Preserve evidenced choices that favor:

- **Locality** when one consumer retains the deciding context and keeps policy, implementation, and tests cohesive.
- **An established shared seam** when independent consumers need one stable decision or copies create coupling across owners.
- **A consumer-facing boundary** for representation that adapts upstream intent without deciding it.
- **The earliest established owner with sufficient context** for repeated downstream policy or mechanics, provided moving upstream preserves the selecting context.
- **A canonical navigation entry** that leads to the owning source without duplicating an inventory.

The relevant policy owners retain ownership, canonical-source, dependency, generation, installation, delivery, exposure, and validation policy. Keep recommendations specific to supported choices; package tours, cached layouts, generic layering, speculative architecture, and configuration or authoring procedures do not belong in this Rule.

## Refresh focus

Revisit callers, consumers, dependency boundaries, and canonical navigation entries when project structure changes. Use concrete relationships from representative implementation and tests to explain where new behavior belongs and when sharing is justified. A directory move can require a new pointer without changing the underlying responsibility or placement principle.

Preserve accepted rankings and their reasons while their evidence remains valid; revise a ranking when changed responsibilities, consumers, or accepted architectural decisions invalidate it. Retain project additions that still describe supported choices. Keep the result a decision guide, updating affected facts without turning each refresh into a directory inventory or a restatement of unchanged guidance.

## Author boundary and result

The Author may inspect target evidence, run owner-supported read-only or non-fixing checks, and create or replace `.agents/rules/structure.md` beneath the Candidate root authorized for this request. Settle that root, exact path and operation through the public writer before writing. No fixed staging directory is required. Deletion, moves, live-target writes, unrelated mutation, and external effects require separate accepted authority.

The first applicable condition determines the sole authoring result:

| Result | Discriminator |
| --- | --- |
| `ACCESS_REQUIRED` | Necessary evidence or validation is inaccessible within the grant. |
| `CONTEXT_REQUIRED` | Access exists, but a necessary fact cannot be discovered from qualified evidence. |
| `HUMAN_DECISION_REQUIRED` | Materially different rankings remain, or a required owner, exception, obligation disposition, operation, or effect lacks accepted authority. |
| `VALIDATION_FAILED` | A required check fails, or a supported choice, obligation, operation, or boundary lacks an evidenced outcome or grant. |
| `READY` | Every recommendation resolves a supported choice, each supported input selects one observable outcome without invented facts, and all applicable deterministic checks pass or are evidenced as `NOT_REQUIRED`. |

A stop names the blocker, owner, consequence, and condition for a fresh attempt. A ready handoff identifies the Candidate, target and evidence owners, obligation dispositions, checks, preserved constraints, and uncertain or untested surfaces. The complete handoff is independently usable by the caller; it grants no downstream generation, installation, publication, commit, or push.
