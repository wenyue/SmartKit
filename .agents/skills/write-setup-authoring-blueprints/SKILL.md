---
name: write-setup-authoring-blueprints
description: Write or revise Setup Authoring Blueprints under setup-assets/blueprints for future project Rules or Skills.
---

# Write Setup Authoring Blueprints

Write the complete set of blueprints required by accepted intent for future project Rules or Skills.
Each blueprint under `setup-assets/blueprints/**` specifies one target: its required meaning, the
project evidence needed to author it, and the future Author's authority and acceptance conditions.

A blueprint is **judgment-only**: it equips a capable Author to make those decisions while leaving
ordinary formulation and reasoning to that Author. Project evidence supplies project facts; setup
and the public writer supply generation mechanics. A required procedure in the future target still
belongs in its blueprint when the order affects the target's behavior.

Read and apply checkout-authoritative `writing-for-agents` before drafting.

## Establish the Blueprint Set

Start with the requested outcome and current authoritative evidence: accepted user decisions,
Issues, Specs, ADRs, governing contracts, target-owner sources, and observable target behavior.
Establish each source's owner and provenance. Existing blueprints and targets help find omissions
and regressions; they do not establish that the old design is complete or right. Investigate further
only for an applicable instruction or a concrete question, within granted access.

Identify each required target's purpose, actor, trigger, exact path, Rule or Skill type, and owner.
Give each target an independently explainable responsibility. Keep policy, procedures, and facts
with their existing owners, and add a target only when accepted intent requires it.

When revising an existing set, account for every behavior-changing obligation as preserve, change,
add, retire, or non-goal. An unsupported disposition remains an unresolved decision; it cannot
justify discarding the obligation.

Fix the blueprint paths before writing. Each create, replace, delete, or move needs authorization
for that exact path and operation. Reuse an existing session grant when it covers both; otherwise
stop before the affected write. Repository visibility, catalog entries, and write access establish
neither semantic authority nor permission. Preserve unrelated paths and independently owned surfaces.

## Specify the Future Target

Write from the future target reader's task: what must that reader recognize, decide, do, or stop on?
For a Rule, connect the governed condition to its required or ranked outcome and consequential
exceptions. For a Skill, explain the intended result and the choices or procedure needed to reach it.
Preserve any necessary sequence in a procedure-led target.

State the accepted meaning and the evidence that will determine its project-specific form. Keep a
condition beside its outcome, exception, and observable basis. Specify permissions, validation,
results, and stops where they affect the target's behavior. Give the future Author the knowledge
needed to express that behavior without prescribing a document template or narrating its writing
process.

For example, suppose accepted project policy requires generated surfaces to stay synchronized with
their canonical inputs. A Tools blueprint can require the future Rule to identify which changes need
synchronization, how agreement is checked, and what happens when the necessary authority is absent.
Repository scripts and their owners supply actual commands and generated paths; setup decides when
to author and register the Rule. The blueprint carries the synchronization obligation and the facts
needed to express it without guessing commands or reproducing setup's execution recipe.

Include detail here when it changes supported target meaning or a target-reader decision. Keep
setup discovery, scheduling, retries, and generation mechanics with their runtime owners. When a
responsibility boundary is uncertain, read
[setup ownership](../../../skills/setup-project-agents/references/ownership.md) for target ownership
and [generated authoring](../../../skills/setup-project-agents/references/generated-authoring.md)
for the division between setup and the public writer.

## Equip the Future Author

Specify the target-repository evidence that setup must supply, including the source owner and
provenance needed to interpret it. Distinguish accepted requirements from existing content supplied
as regression evidence. For facts that vary by project, identify how qualified project evidence
determines them. The blueprint must support authoring without invented project facts or grants.

Establish the future Author's exact Candidate and writable paths, allowed create, replace, delete,
and move operations, any other permissions or external effects, and required validation. Make each
operation's grant explicit; accepted authority may already cover several operations. Inspecting or
generating a file does not authorize changing a live target. Account for every required operation
before declaring the blueprint ready.

Describe the future authoring run's supported results and the observable conditions for returning
them. These describe whether the Author can produce an acceptable artifact; keep them distinct from
the outcomes that artifact will govern when used. Specify what missing authority, unsupported fact,
or material ambiguity stops that Author, and what evidence its handoff must carry. These acceptance
conditions supplement the public writer's result contract without replacing its workflow or
authorizing setup effects.

## Validate the Complete Set

Read the complete set against accepted intent and neighboring owners. Confirm that every required
target and behavior-changing obligation has an accepted disposition, every future Author operation
fits its grant, and each blueprint supplies the meaning and evidence its target needs. Resolve
ownership conflicts and material ambiguity before handoff.

For finite declared result protocols, check that conditions are distinguishable, that explicit
precedence resolves conditions that can coincide, and that no material gap remains. For open-ended
project situations, trace representative normal, exceptional, and insufficient-evidence cases
through the decision criteria. Identify the evidence behind each conclusion and where a missing
fact must stop authoring. These traces test usefulness without claiming coverage of every possible
project. Repair discovered gaps without turning examples into a universal field schema.

Run every applicable owner-supported deterministic non-fixing check. Record `NOT_REQUIRED` only
when qualified owner evidence establishes that no such check applies. Completion requires passing
checks, or that justified result, plus the blueprint review above. An unresolved check failure stops
completion; preserve the failure evidence and report what remains unresolved.

## Hand Off or Stop This Run

The results below belong to the current blueprint-authoring run, separately from any results being
specified inside a blueprint:

| Result | Condition |
| --- | --- |
| `ACCESS_REQUIRED` | Necessary evidence or validation is inaccessible within the grant. |
| `CONTEXT_REQUIRED` | Access is authorized, but qualified evidence cannot supply a necessary fact. |
| `HUMAN_DECISION_REQUIRED` | A material choice lies outside accepted authority. |

For missing access or context, report the exact need, why authorized discovery could not satisfy it,
the resolving owner or condition, the consequence, and the authority and observable condition for
a fresh run. For a decision, name its owner, live choices, evidence, and consequences. Resume only
in a new run after the missing input and retry authority are established; existing accepted authority
may already cover the retry.

On completion, return the exact blueprint paths and owners, supported outcomes, checks and results,
preserved constraints, and uncertain or untested surfaces. Keep this handoff separate from the
blueprints. Deliver ready inputs to `setup-project-agents`, which owns downstream generation and
setup execution, without invoking it.

This run changes only the authorized blueprints. It produces no future targets or shared SmartKit
artifacts and performs no translation, installation, publication, commit, or push.
