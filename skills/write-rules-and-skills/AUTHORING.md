# Authoring Decisions

This record preserves deliberate trade-offs that a future writer might otherwise undo at material cost. It is not part of ordinary execution or a hidden source of requirements. Guidance, metadata, executable interfaces, and other active behavior remain with their operative owners.

## Keep the role-oriented architecture

Keep the Controller, one resident Author, a common Reviewer contract with separate Quality, Change, and Correctness perspectives, and a Correctness-commissioned Runner. Keep role references separate because each identity needs a different question, evidence set, and authority; merging them would recreate the entangled context and responsibilities replaced by [ADR 0012](../../docs/adr/0012-organize-authoring-around-roles.md). Similar subjects may appear from distinct professional perspectives, but repeating the same operative rule is not intentional.

## Make redesign a visible judgment

Require Quality to use rhetorical questions every round and state whether redesign is warranted. Evaluation showed that an implicit invitation to reconsider design was easy to overlook, while a mandatory dialogue or reduction quota would add burden without improving the judgment. The questions focus attention without granting broader editing authority. [ADR 0021](../../docs/adr/0021-make-skill-redesign-an-explicit-review-decision.md) records the wider decision.

## Layer Skill dependencies but keep boundary redirects

Let Skill dependencies run one way, from the Skill that needs another to the Skill it needs, without cycles; route work to any other Skill, including one that depends on the referring Skill, only through a non-executing boundary redirect. A strict ban on peer references would remove the redirects that let a mis-selected Skill name the right owner instead of stopping without direction or doing that owner's work. Unrestricted peer invocation would instead let Skills couple to each other's content and form cycles. Direction comes from what each reference does, so reviewers can decide it from the artifacts without a layer registry. Mentions that create no relationship, such as license attribution, self-contained teaching examples, or the Skill being authored, stay outside the policy; banning every mention would remove required attribution and the ability to name a Skill being worked on.

## Treat provided Skill dependencies as available

Require unavailable or failure outcomes for tools, services, credentials, and other environment capabilities, but not for a Rule's or Skill's dependency on a Skill its supported environment is set up to provide. In SmartKit, SmartKit Skills ship with every SmartKit Rule and Skill, a project's Rules and Skills may rely on SmartKit Skills because the project presupposes SmartKit, and a project's own Skills ship with its own Rules and Skills; a missing Skill, including one from another plugin, is an environment-configuration problem. Absence branches for these Skills would never run in a supported environment, and a separate failure requirement duplicated the ordinary result handling that Correctness still walks. Keep the exemption limited to provided Skills: a Skill that supported targets may or may not provide, such as one a target project authors for a SmartKit Skill to use, needs outcomes for both presence and absence. The specific SmartKit rule for those Skills belongs to this repository's project-local `write-shared-rules-and-skills` Skill, not to this public Skill, which must not depend on a project Skill.

## Keep authoring records lean

Create an `AUTHORING.md` entry only for a deliberate trade-off that a future writer is likely to undo and whose accidental reversal would be costly. Keep the entry to the decision and its reason; retain alternatives or consequences only when they are worth remembering. This prevents the record from becoming routine history or a second contract while preserving the context needed to avoid an expensive mistaken "fix."

## Keep exact protocol separate from design judgment

Scope, version identity, review release, and runtime cleanup have exact boundaries because another role relies on their results. Writing decisions instead need priorities, evidence, and consequential exceptions. Keep this difference visible in the entry and role guidance: converting design advice into mandatory templates or numerical limits would narrow accepted solutions, while treating protocol boundaries as stylistic advice would break coordinated review. The document checker and semantic reviewers remain complementary for the same reason.

## Treat fixed content as an input constraint

Keep exact string fields and exact files as optional, generic constraints accepted by the Controller. Blueprints and setup are callers rather than special authoring modes, so the same source can be used independently and unrelated metadata remains editable. Reuse the evidence snapshot for accepted sources and declarations: comparing against live or Author-retyped expectations would allow drift to redefine success. A bounded field reader reports unsupported syntax as incomplete instead of approximating YAML values; semantic acceptance remains with the Reviewers.
