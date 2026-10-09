---
name: upgrade-third-party-skills
description: Assess or perform upgrades of third-party Skills maintained by this repository, including upstream changes, local patches, and adoption decisions.
---

# Upgrade Third-Party Skills

Upgrade this repository's registered external Skills with their accepted local behavior intact.
The central comparison has three parts: what upstream changed, what our patches are meant to
preserve, and which consumers depend on the resulting instructions. A clean patch application
answers only the mechanical part of that comparison.

This is a project-local maintenance Skill. An assessment request authorizes investigation and a
proposal; an upgrade request also authorizes the ready implementation within its accepted scope.
Neither extends automatically to publishing or installing the result into user environments.

## Establish the upgrade boundary

Read the external-source entries in [the Skill registry](../../../skills/registry.json), their
records in [the lock](../../../vendor/external-skills.lock.json), and the listed patch files.
Use the lock's resolved commit as the installed upstream baseline; a configured tag or branch name
alone does not identify those bytes. Inspect Git state and managed outputs for existing work before
choosing a workspace and comparison point.

The registry and patches are inputs; distributed Skill trees, licenses, and lock are derived
through [the external Skill updater](../../../scripts/update_external_skills.py).
Keep adaptations with these owners rather than editing generated snapshots directly.

Identify the requested source, target revision, and outcome. Verify the target against current
upstream releases and repository content, distinguishing a release from unreleased branch work.
Record the resolved target commit for comparison and later verification. When the request leaves
the target open, recommend a supported release or revision and explain any consequential choice
between release stability and needed unreleased changes. Missing or unverifiable baseline or target
evidence blocks a justified upgrade; state the gap and continue only independent investigation.

The updater's `--source` selects an entire upstream repository, not one Skill. Establish every
selected Skill affected by that source revision. If the user asked for one Skill, explain any
unavoidable wider update and resolve its scope before implementing it.

## Compare the result people will actually use

Read release notes and compare the old and target upstream trees for all selected Skills and their
owned resources. Follow changed references and affected consumers far enough to establish whether
the proposed result still works. Use the actual diff to direct investigation; unrelated upstream
features need no adoption work merely because they exist.

For each materially affected Skill, establish these relationships:

| Concern | Evidence and decision |
| --- | --- |
| Workflow behavior | Compare triggers, required steps, approval and stopping conditions, delegation, and side effects. Identify where a new instruction changes accepted behavior or conflicts with applicable project or shared guidance. |
| Local adaptations | Read each patch's intended result against old upstream and current applied content, then locate its counterpart in the target. Decide whether it applies unchanged, needs context repair, is already satisfied upstream, or requires a behavioral decision. |
| Selection and discovery | Account for renamed, moved, removed, and newly required Skills or resources. Trace callers, router references, registry entries, and public exposure; a new upstream Skill is a separate adoption choice. |
| Documents and dependencies | Check affected templates, glossary names, links, scripts, commands, tools, harness capabilities, and external services. Establish migration work and availability before relying on the new route. |
| Provenance and execution | Review relevant license or attribution changes, source identity, and new executable or network behavior. Explain additional access, credentials, recurring cost, or trust requirements when the delta introduces them. |

A patch can be rebased without asking when only context changes and its accepted result survives.
If upstream now supplies that result, prove the equivalence before retiring the redundant patch.
If the new workflow makes the old adaptation ineffective or incompatible, expose that choice;
silently dropping the patch to make the updater pass loses the behavior it exists to preserve.

For example, if upstream renames a glossary format and starts looking only for the new filename,
repairing the patch path is insufficient. Locate project pointers, templates, and existing documents
that still use the old name, and settle their migration or supported compatibility before upgrading
the consumer. Likewise, an upstream Skill removal needs a decision about its supported callers and
public entry, not merely deletion of a registry row.

Finish this assessment when every selected Skill and patch is accounted for, affected dependencies
have a supported route, and remaining choices are explicit. Summarize material changes and their
evidence in the conversation; registry, lock, and patches remain the durable provenance records.

## Resolve the choices before mutation

Present the source and baseline-to-target change, expected benefits, affected files and consumers,
patch dispositions, migration work, verification, and recovery approach. Scale this account to the
delta. Separate established facts from uncertain assumptions that could change the decision.

Ask only for choices or facts that cannot be recovered and materially affect the result. Typical
cases are adopting or retiring public Skills, changing their names or activation, changing a local
adaptation's intended behavior, accepting new service or permission requirements, or expanding into
consumer migrations. Bundle related questions with concrete alternatives and their consequences.
Recommend an approach when the evidence supports it; present compatibility choices neutrally when
the governing policy requires that. Wait for the answer before dependent changes.

Reuse decisions and authorization already supplied. Do not turn a routine, behavior-preserving
patch repair into another approval checkpoint. If the user requested analysis only, stop with the
concrete proposal and needed decisions. For an authorized upgrade, proceed once the accepted scope,
remaining behavior, prerequisites, and checks are clear.

## Apply through the owning updater

Retain the pre-upgrade inputs and recorded outputs through Git evidence or an isolated workspace so
the task's changes can be recovered without discarding existing work. Account for managed-output
drift before updating: preserve it, establish its ownership and intent, express accepted changes in
the owning patch, then restore only the corresponding recorded output when that work is safely
preserved. If ownership or preservation is unclear, pause the affected update and request direction.

Change the registry revision and any accepted selection or path changes; adapt ordered patches
against the resolved target while preserving upstream wording outside the accepted local delta.
Preserve license and copyright notices. Use repository owners for any authorized changes to public
exposure or consumers; removing a contract includes its affected callers, documentation, and checks.

From the repository root, update the selected source:

```bash
python scripts/update_external_skills.py --update --source <owner/repository>
```

Use the registry's actual source ID. Confirm the current CLI with `--help` when needed. Omitting
`--source` processes all configured sources; use that scope only when intended. Removing a whole
source requires planning the full update because a removed ID is no longer accepted by `--source`.
Removing a selected Skill from a retained source makes the updater remove its managed destination.

The updater stages and validates patches before installing Skills, licenses, and lock together.
A patch conflict leaves previous installed outputs intact; input edits made before invoking it
still need review. Investigate failures before retrying. For a reported transaction or rollback
failure, inspect actual files and saved Git evidence rather than assuming recovery succeeded.

## Verify the applied result

Read the complete changed Skills with their required resources and trace affected invocation paths.
Confirm that the intended patch behavior, discovery, document conventions, and dependencies work
together. For changed executable behavior, run the relevant supported checks; if behavior cannot be
verified, report the specific gap rather than treating textual coherence as runtime evidence.

Run the updater in non-mutating check mode:

```bash
python scripts/update_external_skills.py --check --source <owner/repository>
```

Both update and check resolve upstream sources and may need network access; `--check` is not an
offline lock inspection. Check the resulting lock's commit against the reviewed target. A moved
target or newly observed delta requires reassessment. Review the reported patch extent as a signal
of local maintenance burden, not proof that the adaptation is correct.

Run applicable manifest, Rule delivery, translation, and repository checks from their current
owners and [CI configuration](../../../.github/workflows/test.yml). Synchronize mirrors when the
project's translation policy applies. Inspect every changed or removed path, generated output,
license, and lock entry against the accepted scope, including unexpected changes outside the selected
source. Run `git diff <comparison-point> --check`, covering new untracked files as well.

Completion requires the reviewed revision to be installed in repository snapshots, accepted local
behavior and affected consumers to be coherent, all required checks to pass, and existing work to
be preserved. Report source and revision changes, adopted or retired entries, meaningful patch and
migration decisions, verification evidence, and any unresolved limitation. Distinguish a completed
repository upgrade from downstream publication or installation, which retain their own authority.
