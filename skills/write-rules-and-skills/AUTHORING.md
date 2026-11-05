# Authoring Decisions

This record preserves deliberate trade-offs that a future writer might otherwise undo at material cost. It is not part of ordinary execution or a hidden source of requirements. Guidance, metadata, executable interfaces, and other active behavior remain with their operative owners.

## Keep the role-oriented architecture

Keep the Controller, one resident Author, a common Reviewer contract with separate Quality, Change, and Correctness perspectives, and a Correctness-commissioned Runner. Keep role references separate because each identity needs a different question, evidence set, and authority; merging them would recreate the entangled context and responsibilities replaced by [ADR 0012](../../docs/adr/0012-organize-authoring-around-roles.md). Similar subjects may appear from distinct professional perspectives, but repeating the same operative rule is not intentional.

## Make redesign a visible judgment

Require Quality to use rhetorical questions every round and state whether redesign is warranted. Evaluation showed that an implicit invitation to reconsider design was easy to overlook, while a mandatory dialogue or reduction quota would add burden without improving the judgment. The questions focus attention without granting broader editing authority. [ADR 0021](../../docs/adr/0021-make-skill-redesign-an-explicit-review-decision.md) records the wider decision.

## Judge dependencies by semantic use

Treat an artifact and its owned resources as one dependency unit, and judge cross-artifact references by their required behavior. File-level cycles would mistake internal composition for architectural coupling; a ban on every name would also remove attribution, self-contained examples, and the ability to identify work subjects. Opening responsibility boundaries preserve useful routing without permitting an invocation or required read to masquerade as a redirect. Rule-led Skills follow Rules in this model because they own policy, while instruction precedence remains a separate concern.

## Make project extensions explicit

Project Skills ordinarily sit above a shared provider. Some providers deliberately call project-owned extension Skills to obtain behavior only the project can supply. Treat that as declared reverse-dependency visibility rather than pretending it follows the ordinary direction or exposing every project Skill. Checking the whole graph through the extension preserves the no-cycle guarantee even when the target uses another project Skill or a provider capability.

## Treat provided Skill dependencies as available

Separate permission to depend on a Skill from its supported availability. This avoids redundant absence branches without treating installation as permission. Generic relationship definitions live in one public reference so Authors, Reviewers, and maintainers share the contract. Provider-specific policy arrives as qualified owner input; embedding SmartKit's maintainer policy here would couple a portable writer to one provider and its repository-local workflow. Controllers and roles load what they need, keeping the entry process-oriented and standalone blueprints complete without copied common policy.

## Keep authoring records lean

Create an `AUTHORING.md` entry only for a deliberate trade-off that a future writer is likely to undo and whose accidental reversal would be costly. Keep the entry to the decision and its reason; retain alternatives or consequences only when they are worth remembering. This prevents the record from becoming routine history or a second contract while preserving the context needed to avoid an expensive mistaken "fix."

## Keep exact protocol separate from design judgment

Scope, version identity, review release, and runtime cleanup have exact boundaries because another role relies on their results. Writing decisions instead need priorities, evidence, and consequential exceptions. Keep this difference visible in the entry and role guidance: converting design advice into mandatory templates or numerical limits would narrow accepted solutions, while treating protocol boundaries as stylistic advice would break coordinated review. The document checker and semantic reviewers remain complementary for the same reason.

## Treat fixed content as an input constraint

Keep exact string fields and exact files as optional, generic constraints accepted by the Controller. Blueprints and setup are callers rather than special authoring modes, so the same source can be used independently and unrelated metadata remains editable. Reuse the evidence snapshot for accepted sources and declarations: comparing against live or Author-retyped expectations would allow drift to redefine success. A bounded field reader reports unsupported syntax as incomplete instead of approximating YAML values; semantic acceptance remains with the Reviewers.
