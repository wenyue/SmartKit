---
name: write-setup-authoring-blueprints
description: Write or revise project authoring blueprints under setup-assets/blueprints for future project Rules or Skills.
---

# Write Project Authoring Blueprints

Produce the blueprint set needed to turn accepted intent into useful project Rules and Skills. Each blueprint describes one future target: the job it must help its reader do, the project evidence that shapes it, the content that matters, and how that content should evolve on later refreshes. Blueprints support independent authoring through the public writer.

Blueprints are **judgment-only**. Give the future Author firm requirements and concrete directions for open choices; leave composition and ordinary reasoning to that Author. The Author discovers and qualifies project evidence within the invocation's authority; a caller may supply accepted inputs. The public writer owns Candidate authoring and review. A procedure that the future target must teach belongs in its blueprint when order affects behavior; invocation scheduling, script mechanics, and retries belong to their runtime owners.

Read checkout-authoritative `writing-for-agents` before writing. Follow the steps below for this blueprint-authoring run; they are not a template for the blueprints themselves.

## 1. Establish the targets and the authority to write

Recover the intended outcome from accepted user decisions and applicable project records, then qualify it against governing contracts, target-owner sources, and observable behavior. Establish source ownership and provenance so an existing example cannot silently become a requirement. Use existing blueprints and targets to find useful intent, omissions, and regressions; their presence does not establish that the old design is correct. Investigate further only to satisfy applicable instructions or answer a concrete question within the available access.

For each required target, establish its reader, purpose, trigger, Rule or Skill type, exact path, and owner. Give it a distinct responsibility, retaining policy, procedures, and facts with their proper owners. Create an additional target only when accepted intent requires one. For a revision, account for every behavior-changing obligation as preserved, changed, added, retired, or outside scope; an unsupported disposition is an unresolved decision rather than permission to drop it.

Fix the blueprint paths and operations before drafting. Each create, replace, delete, or move needs authority for that exact path and operation; reuse an existing grant when it covers both. Visibility, a catalog entry, and filesystem access supply no semantic or write authority. Preserve unrelated paths and independently owned surfaces. Proceed when the complete target set, responsibilities, and authorized blueprint operations are clear; route missing inputs through the stop conditions below.

## 2. Give each Author a direction they can use

Write from the future reader's decisions. A Rule must connect its applicable condition to required or ranked behavior, with the exceptions that change the result. A Skill must explain the intended outcome and the choices or necessary sequence that lead to it. Specify permissions, verification, results, and stops where they affect that target's behavior. Keep conditions and exceptions beside the meaning they qualify.

For each substantial part of the target, connect three things: what the reader needs to accomplish, which project evidence determines the content, and what deserves emphasis or exclusion. Name useful source directions and their owners, such as project-declared check commands, generator mappings, architectural decisions, or implementation relationships. Explain what each source resolves instead of asking the Author to "inspect the repository" or "document the tools." Project-dependent facts come from qualified project evidence, not from an illustrative command or a guessed repository layout.

For example, a Tools blueprint may need to help readers keep generated outputs synchronized. Point the Author to the project's declared generators, input/output mappings, and supported checks. Focus the resulting guidance on which source changes require regeneration, how agreement is verified, and what missing authority prevents execution. An inventory of every installed utility would obscure those decisions. The blueprint can establish this direction without choosing commands before the project evidence is available or prescribing headings for the future Rule.

The blueprint is sufficiently concrete when the Author can identify the required meaning, obtain the facts that determine its project-specific form, and choose relevant detail without inventing facts or permissions. Leave document structure and wording open unless they carry an accepted behavioral contract.

## 3. Make later refreshes useful for this content

Define refresh preferences in every blueprint. Select them according to the content's job, including different preferences for different parts of a mixed target. Neither rewriting everything nor preserving everything is a suitable default for all blueprints.

| Content | What the blueprint should direct the Author to do |
| --- | --- |
| Tool and code-structure facts | Recheck the configurations, documented ownership, or implementation relationships that establish those facts. Update changed facts and remove disproven claims; frequent changes can be appropriate even when the blueprint is unchanged. |
| Processes and durable context | Preserve still-applicable decisions, obligations, and their reasons. Identify which changes to requirements, responsibilities, or supported behavior justify revision. Retain useful stable wording when only phrasing could change. |
| A mixture of both | Distinguish the parts, such as a stable verification obligation and its changing project command. Refresh the fact without losing the obligation or preserving an obsolete command merely because the surrounding policy is stable. |

Use the current target together with fresh, qualified project evidence. Preserve valid project additions and obligations, including their conditions and exceptions. Existing text is evidence of intent, not proof that a disputed claim remains valid; resolve conflicts using the responsible owners and accepted authority. A newer blueprint likewise supplies no blanket reason to erase project decisions.

Explain what evidence warrants each kind of change and what should survive it. Where the refresh criteria reveal no relevant change or defect, retain sound content. Where they justify a revision, keep the resulting guidance accurate and coherent without accumulating duplicates. These criteria guide content decisions; they do not define invocation frequency, script behavior, or a replacement workflow for the public writer.

Proceed when every blueprint explains its expected sources of change, stable meaning, and evidence for revision with enough specificity to distinguish a useful refresh from unnecessary rewriting.

## 4. Bound the future authoring job

Specify what evidence the future Author needs and how to obtain and qualify it within the invocation's authority: project facts with ownership and provenance, the existing target and relevant project additions, and accepted requirements distinguished from content used to detect regressions. A caller may supply these inputs, but their absence from a handoff is a discovery task before it is a missing-input stop. Let the Author determine ordinary file, interface, and implementation choices from qualified evidence; require user input only for material choices beyond accepted authority. Explain how facts that remain unsupported after authorized discovery affect the ability to produce the target.

Establish that Author's exact Candidate and writable paths, the allowed create, replace, delete, and move operations, required validation, and any other permission or external effect before writing. Use the destination authorized for that invocation. Make every needed operation's grant explicit, reusing accepted authority where sufficient. Generating or inspecting an artifact supplies no authority to modify a live target.

Define observable acceptance conditions and the evidence the handoff must carry. Distinguish the future authoring run's supported results from the results the finished Rule or Skill will govern when used. Missing authority, unsupported material facts, and unresolved material choices must stop dependent authoring. These conditions supplement the public writer's result contract; they neither replace its workflow nor authorize downstream integration effects.

This step is complete when the future Author can recognize its scope, evidence-discovery responsibilities, usable result, and stopping conditions without assuming a grant or inputs from a separate workflow.

## 5. Check the set and deliver it

Review the complete blueprint set against accepted intent and neighboring owners. Every required target and behavior-changing obligation needs a supported disposition, and every future operation must fit its grant. Resolve overlapping ownership or material ambiguity before handoff.

Trace representative normal, exceptional, and insufficient-evidence cases through each blueprint. Include a repeat with unchanged evidence, a changed project fact, and an existing valid project addition. Confirm that the guidance supports retaining sound content, correcting stale facts, and preserving project intent in the relevant cases. Identify the evidence behind each conclusion and where missing facts must stop authoring. These examples test the guidance; they do not become a universal field schema or a claim of exhaustive coverage. For a finite result protocol, check that conditions are distinguishable, overlapping conditions have explicit precedence, and no material gap remains.

Run all applicable owner-supported deterministic checks without fixing mode. Use `NOT_REQUIRED` only when qualified owner evidence establishes that no such check applies. Completion requires passing checks, or that justified result, as well as the set review above. A failed or inaccessible required check prevents completion; retain the failure evidence and report the unresolved condition.

Deliver the exact blueprint paths and owners, supported outcomes, checks and results, preserved constraints, and uncertain or untested surfaces. Keep this handoff outside the blueprints. The result supports independent authoring through the public writer. Future-target authoring and downstream integration remain separate jobs under their owning workflows; this blueprint-writing run invokes neither. Change only the authorized blueprints: produce no future targets or shared SmartKit artifacts, and perform no translation, installation, publication, commit, or push.

## Stop when an input cannot support the work

Use these results for the current blueprint-authoring run, independently of any result contract being described inside a blueprint:

| Result | Condition |
| --- | --- |
| `ACCESS_REQUIRED` | Required evidence or validation cannot be accessed within the grant. |
| `CONTEXT_REQUIRED` | Access is authorized, but qualified evidence cannot establish a necessary fact. |
| `HUMAN_DECISION_REQUIRED` | A material choice exceeds accepted authority. |

For missing access or context, identify the exact need, why authorized discovery did not resolve it, the responsible owner or resolving condition, and the consequence of proceeding without it. State the authority and observable condition needed for a fresh run. For a decision, provide its owner, the available choices, supporting evidence, and consequences. Resume only in a new run once the missing input and retry authority are established; existing accepted authority may cover that retry.
