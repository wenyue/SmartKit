---
name: upgrade-third-party-skills
description: Assess or perform upgrades of third-party Skills maintained by this repository, identifying adoption risks, trade-offs, and recommended adaptations.
---

# Upgrade Third-Party Skills

Guide adoption of upstream changes while preserving accepted local behavior until a change is chosen. Investigate risks and consequential choices before the user has to identify them, then recommend a supported approach. Compare what upstream changed, why local adaptations exist, and what the combined instructions will make consumers do. A clean patch application establishes only mechanical compatibility.

This is a project-local maintenance Skill. An assessment request authorizes investigation and a proposal; an upgrade request also authorizes the ready implementation within its accepted scope. Neither extends automatically to publishing or installing the result into user environments.

## Establish the upgrade boundary

Read the external-source entries in [the Skill registry](../../../skills/registry.json), their records in [the lock](../../../vendor/external-skills.lock.json), and the listed patch files. Use the lock's resolved commit as the installed upstream baseline; a configured tag or branch name alone does not identify those bytes. Inspect Git state and managed outputs for existing work before choosing a workspace and comparison point.

The registry and patches are inputs; distributed Skill trees, licenses, and lock are derived through [the external Skill updater](../../../scripts/update_external_skills.py). Keep adaptations with these owners rather than editing generated snapshots directly.

Identify the requested source, target revision, and outcome. Verify the target against current upstream releases and repository content, distinguishing a release from unreleased branch work. Record the resolved target commit for comparison and later verification. When the request leaves the target open, recommend a supported release or revision and explain any consequential choice between release stability and needed unreleased changes. Missing or unverifiable baseline or target evidence blocks a justified upgrade; state the gap and continue only independent investigation.

The updater's `--source` selects an entire upstream repository, not one Skill. Establish every selected Skill affected by that source revision. If the user asked for one Skill, explain any unavoidable wider update and resolve its scope before implementing it.

## Discover what could change the adoption decision

Read release notes and compare the old and target upstream trees for all selected Skills and their owned resources. Follow changed instructions into affected local Rules, Skills, callers, and tools. Use those relationships to find risks and useful simplifications; a changelog alone cannot show what the combined system will do. Focus on upstream interactions with local behavior and patches. Upstream-internal conflicts or ambiguities need attention only when they materially impede local adoption; unrelated upstream features need no adoption work merely because they exist.

For each materially affected Skill, investigate the consequences of the delta:

| Concern | What could change the decision |
| --- | --- |
| Behavior and composition | Changes to triggers, obligations, stopping conditions, delegation, or side effects can alter accepted behavior. Read applicable Rules, native discovery metadata, and actual dependencies together before deciding what is missing or incompatible. |
| Local adaptations | Establish each patch's purpose from old upstream and current applied content, then find its counterpart in the target. Distinguish context repair, an equivalent upstream implementation, and a change to the intended behavior. |
| Selection and overlap | Trace renamed, moved, removed, and newly required entries through callers, registry, and public exposure. Compare new capabilities with existing local ones; additions and replacements can change both coverage and maintenance cost. |
| Dependencies and migration | Check changed document conventions, templates, links, scripts, commands, tools, and harness capabilities. A renamed format can leave callers or existing documents unusable even when the patch applies. |
| Provenance and effects | Check source identity, relevant license or attribution changes, and new executable or network behavior. Expose additional access, credentials, services, recurring cost, or trust requirements. |

Establish a conflict only when applicable clauses cannot both be satisfied for the same decision. Cite both precise source locations, their conditions, the triggering scenario, and its consequence; apply governing precedence before proposing a repair. Instructions for different stages can coexist. Likewise, a missing explicit Skill name does not prove missing capability: check whether applicable Rules and native discovery already supply the required route. Distinguish a supported static reading from observed invocation behavior, and identify consequential uncertainty.

Evaluate replacement by the outcomes and necessary guarantees consumers depend on, including accepted authorization, verification, and recovery boundaries. Different steps alone do not justify retaining two Skills. Explain what the replacement covers, what remains unsupported, and whether the gap merits a small integration, keeping a distinct capability, or deferring adoption. Include the maintenance cost of preserving the old protocol; preserve its necessary guarantees without transplanting steps that no longer serve them.

Choose the owner of each adaptation from the responsibility that needs to change. A local caller or Rule may need revision to compose with a sound upstream design; a patch belongs where an accepted local difference must remain in the vendored Skill. Compare those options before adding patch burden. Context-only patch repair can proceed within existing authorization. Retire a patch only after establishing that its accepted result is supplied elsewhere or its removal is authorized; dropping it merely to make the updater pass loses the behavior it exists to preserve.

For a proposed retirement or replacement, trace remaining consumers and assumptions: references, public exposure, terms, protocols, documentation, and checks. Separate cleanup required by that choice from optional simplification of surrounding workflows. Recommend bounded follow-up work when the old dependency was their reason for complexity; material expansion remains a user choice.

The assessment is ready when every selected Skill and patch is accounted for, affected consumers and dependencies have a supported route or an explicit gap, and material risks and choices are explained. Keep evidence in the conversation; registry, lock, and patches remain the durable provenance records.

## Recommend a course and settle consequential choices

Lead with the recommended adoption scope and why it serves the user's goal. Identify the source and baseline-to-target change, benefits, material risks, affected consumers, patch dispositions, migration work, and proposed verification and recovery. Prioritize consequences that could change the decision rather than giving every diff equal weight.

For each unresolved material choice, present viable alternatives, their trade-offs, and a grounded recommendation. State the evidence and any assumption on which it turns. If missing evidence could reverse the recommendation, obtain it when recoverable; otherwise name the gap and next useful investigation or precise user input needed. Do not substitute an open-ended request for direction for analysis the Agent can perform.

Ask and wait before dependent changes when the choice changes accepted scope or behavior, such as adopting or retiring a public Skill, changing names or activation, accepting new service or permission requirements, or expanding consumer migrations. Reuse decisions and authorization already supplied; routine repairs that preserve the accepted result need no new approval checkpoint. For analysis only, finish with the concrete proposal and remaining decisions. For an authorized upgrade, proceed once the accepted scope, behavior, prerequisites, and checks are clear.

## Apply through the owning updater

Retain the pre-upgrade inputs and recorded outputs through Git evidence or an isolated workspace so the task's changes can be recovered without discarding existing work. Account for managed-output drift before updating: preserve it, establish its ownership and intent, express accepted changes in the owning patch, then restore only the corresponding recorded output when that work is safely preserved. If ownership or preservation is unclear, pause the affected update and request direction.

Change the registry revision and any accepted selection or path changes; adapt ordered patches against the resolved target while preserving upstream wording outside the accepted local delta. Preserve license and copyright notices. Use repository owners for any authorized changes to public exposure or consumers; removing a contract includes its affected callers, documentation, and checks.

From the repository root, update the selected source:

```bash
python scripts/update_external_skills.py --update --source <owner/repository>
```

Use the registry's actual source ID. Confirm the current CLI with `--help` when needed. Omitting `--source` processes all configured sources; use that scope only when intended. Removing a whole source requires planning the full update because a removed ID is no longer accepted by `--source`. Removing a selected Skill from a retained source makes the updater remove its managed destination.

The updater stages and validates patches before installing Skills, licenses, and lock together. A patch conflict leaves previous installed outputs intact; input edits made before invoking it still need review. Investigate failures before retrying. For a reported transaction or rollback failure, inspect actual files and saved Git evidence rather than assuming recovery succeeded.

## Verify the applied result

Read the complete changed Skills with their required resources and trace affected invocation paths. Confirm that the intended patch behavior, discovery, document conventions, and dependencies work together. For changed executable behavior, run the relevant supported checks; if behavior cannot be verified, report the specific gap rather than treating textual coherence as runtime evidence.

Run the updater in non-mutating check mode:

```bash
python scripts/update_external_skills.py --check --source <owner/repository>
```

Both update and check resolve upstream sources and may need network access; `--check` is not an offline lock inspection. Check the resulting lock's commit against the reviewed target. A moved target or newly observed delta requires reassessment. Review the reported patch extent as a signal of local maintenance burden, not proof that the adaptation is correct.

Run applicable manifest, Rule delivery, translation, and repository checks from their current owners and [CI configuration](../../../.github/workflows/test.yml). Synchronize mirrors when the project's translation policy applies. Inspect every changed or removed path, generated output, license, and lock entry against the accepted scope, including unexpected changes outside the selected source. Run `git diff <comparison-point> --check`, covering new untracked files as well.

Completion requires the reviewed revision to be installed in repository snapshots, accepted local behavior and affected consumers to be coherent, all required checks to pass, and existing work to be preserved. Report source and revision changes, adopted or retired entries, meaningful patch and migration decisions, verification evidence, and any unresolved limitation. Distinguish a completed repository upgrade from downstream publication or installation, which retain their own authority.
