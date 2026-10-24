---
name: write-setup-authoring-blueprints
description: Write or revise project authoring blueprints under setup-assets/blueprints for future project Rules or Skills.
---

# Write Project Authoring Blueprints

Write the blueprint set that turns accepted intent into useful project Rules and Skills. Each blueprint describes one future target: its reader's job, the project evidence that shapes it, the content that matters, and how that content should evolve. The public `write-rules-and-skills` Skill authors and reviews each future Candidate. Support standalone writer invocation and Setup's use of the same blueprint inputs.

Blueprints supply semantic requirements, task-specific acceptance, and any accepted fixed sources. Give concrete direction for open choices while leaving composition and ordinary reasoning to the future Author. That Author discovers and qualifies project evidence within the invocation's authority; a caller may supply accepted inputs. Include a procedure the future target must teach when order affects behavior. Keep invocation scheduling, script mechanics, and retries with runtime owners.

Read checkout-authoritative `writing-for-agents` before writing. The sequence below governs this authoring run; it is not an outline for every blueprint.

## 1. Establish the targets and writing authority

Recover the outcome from accepted user decisions and applicable project records, then qualify it against governing contracts, target-owner sources, and observable behavior. Establish ownership and provenance so an existing example cannot become a requirement by accident. Use old blueprints and targets to discover intent, omissions, and regressions without assuming their design is correct. Widen investigation only for applicable instructions or a concrete question within available access.

For each required target, establish reader, purpose, trigger, Rule or Skill type, exact path, and owner. Give it a distinct responsibility and keep policy, procedures, and facts with their proper owners. Add a target only when accepted intent requires it. For revisions, account for every behavior-changing obligation as preserved, changed, added, retired, or outside scope; an unsupported disposition remains unresolved.

Fix exact blueprint and supporting-resource paths and create, replace, delete, or move operations before drafting. Each needs authority covering both path and operation; reuse existing grants where sufficient. Visibility, a catalog entry, and filesystem access establish neither semantic nor write authority. Preserve unrelated paths and independently owned surfaces.

Proceed when the complete target set, responsibilities, and authorized operations are clear. Otherwise use the stop conditions below.

## 2. Give the future Author useful direction

Write from the future reader's decisions. A Rule connects an applicable condition to required or ranked behavior and consequential exceptions. A Skill explains its outcome and the choices or necessary sequence that achieve it. Specify permission, verification, results, and stops where they affect behavior, keeping conditions and exceptions beside their meaning.

For each substantial part of the target, connect:

- what its reader needs to accomplish;
- which project evidence determines the content;
- what deserves emphasis or exclusion.

Name useful source directions and owners, such as declared checks, generator mappings, architectural decisions, or implementation relationships. Explain what they resolve. A generic request to inspect the repository leaves the content decision unsupported; project facts must come from qualified evidence rather than an illustrative command or guessed layout.

For example, a Tools blueprint may guide its Author to generators, input/output mappings, and supported checks so the future Rule explains when regeneration is required, how agreement is verified, and what missing authority blocks it. An inventory of installed utilities would obscure that job. The blueprint can direct the inquiry without preselecting commands or headings.

The direction is sufficient when the Author can identify required meaning, find the facts shaping its project-specific form, and select relevant detail without inventing facts or permission. Leave structure and wording open unless they carry an accepted behavioral contract.

For a Skill blueprint, `description` is the target Skill's description and is copied unchanged. The blueprint is an authoring input with no discovery trigger of its own. Provide target `agents/openai.yaml` interface fields and packaged icons under the public writer's metadata conventions. Keep repository-specific selection and execution details in the target body. Store each fixed value or asset once and declare its source-to-target constraint through the writer's fixed-content interface. Match selected metadata fields while preserving independent fields and project additions; require whole-file identity only for resources whose complete bytes are fixed.

Keep target resources distinct from the blueprint's own authoring instructions and include the declaration and every referenced source in its usable input bundle. The public writer freezes and verifies accepted fixed content; Setup and other callers supply the same inputs without a separate authoring protocol.

## 3. Explain what should change on refresh

Every blueprint needs refresh preferences suited to its content, including different preferences for mixed content. Neither rewriting everything nor preserving everything works as a universal default.

| Content | Refresh direction |
| --- | --- |
| Tool and code-structure facts | Recheck authoritative configuration, documented ownership, or implementation relationships. Update changed facts and remove disproven claims; the blueprint itself need not have changed. |
| Processes and durable context | Preserve applicable decisions, obligations, and reasons. Identify changed requirements, responsibilities, or supported behavior that justify revision; retain sound wording when only phrasing could differ. |
| Mixed content | Separate stable obligations from changing facts, such as a verification duty and its project command. Refresh the fact without losing the duty or preserving an obsolete command. |

Use the current target with fresh qualified evidence. Preserve valid project additions and obligations with their conditions and exceptions. Existing text is evidence of intent, not proof of a disputed claim; resolve conflicts through responsible owners and accepted authority. A newer blueprint does not authorize erasing project decisions.

Explain which evidence warrants each change and what must survive it. Retain sound content when no relevant change or defect appears; make justified revisions coherent without accumulating duplicates. These preferences guide content, not invocation frequency, scripts, or a replacement for the public writer.

Proceed when each blueprint distinguishes useful refresh from unnecessary rewriting through its expected change sources, stable meaning, and evidence for revision.

## 4. Bound the future authoring job

Specify the evidence the future Author needs and how to discover and qualify it within the invocation's authority: project facts with owners and provenance, the existing target and relevant additions, accepted requirements, and regression-detection material. A caller may supply this evidence, but an incomplete handoff first calls for authorized discovery, not an immediate missing-input stop.

Let the Author make ordinary file, interface, and implementation choices from qualified evidence. Require user input for material choices beyond accepted authority. Explain how facts still unsupported after discovery prevent a usable target.

Establish the future Author's exact Candidate and writable paths, allowed create, replace, delete, and move operations, required validation, and other permissions or external effects before writing. Use the authorized destination and make each required operation's grant explicit, reusing accepted authority where sufficient. Generating or inspecting an artifact does not authorize modifying a live target.

Define task-specific acceptance and required handoff evidence. The public writer owns Author and Reviewer roles, Candidate versions, review order, and terminal results; a blueprint supplies requirements through that workflow. Keep the finished artifact's runtime results distinct from authoring completion. Missing authority, unsupported material facts, or unresolved material choices stop dependent authoring through the writer, without a second status table or integration grant.

Complete this step when the future Author can recognize scope, discovery duties, usable results, and stops without assuming separate-workflow grants or inputs.

## 5. Check the set and deliver

Review the whole set against accepted intent and neighboring owners. Every required target and behavior-changing obligation needs a supported disposition; every future operation must fit its grant. Resolve overlapping ownership and material ambiguity before handoff.

Trace representative normal, exceptional, and insufficient-evidence cases through each blueprint, including use without Setup. Include unchanged evidence on repeat, a changed project fact, and an existing valid project addition. Check that the guidance supports retaining sound content, correcting stale facts, and preserving project intent, and identify evidence and missing-fact stops. These cases test the guidance without creating a universal content schema or claiming exhaustive coverage. For a target runtime result protocol, ensure conditions are distinguishable, overlaps have explicit precedence, and no material gap remains. Check that fixed declarations reach the intended target paths and complete source bundle, preserve independent fields, and remain consistent with the target behavior.

Run applicable owner-supported deterministic checks without fixing mode. Use `NOT_REQUIRED` only when qualified owner evidence establishes that no check applies. Passing checks, or that justified result, and the set review are required for completion. Failed or inaccessible required checks prevent completion; preserve their evidence and report the unresolved condition.

Deliver exact blueprint paths and owners, supported outcomes, checks and results, preserved constraints, and uncertain or untested surfaces. Keep the handoff outside the blueprints. This run changes only authorized blueprints and their supporting resources: it authors no future targets or shared SmartKit artifacts and invokes neither future-target authoring nor downstream integration. It performs no translation, installation, publication, commit, or push; those remain separate jobs.

## Stop when the input cannot support the work

Stop dependent work when required evidence or validation is inaccessible within the grant, qualified evidence cannot establish a necessary fact, or a material choice exceeds accepted authority.

For access or context gaps, name the exact need, why authorized discovery did not resolve it, responsible owner or resolving condition, and consequence of proceeding. State the authority and observable condition needed for a fresh run. For a decision, give its owner, choices, evidence, and consequences.

Resume after the missing input and retry authority are established; existing accepted authority may cover that retry. Recheck affected evidence before claiming completion.
