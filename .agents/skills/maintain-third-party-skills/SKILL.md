---
name: maintain-third-party-skills
description: Assess or implement first-time adoption and upgrades of third-party Skills maintained by this repository, identifying selection, integration risks, and necessary local adaptations.
---

# Maintain Third-Party Skills

Evaluate what upstream Skills will make consumers do, settle necessary local adaptations, then generate and verify the repository snapshots. Preserve accepted local behavior until a change is chosen. Investigate consequential risks proactively and recommend a supported course: a clean patch application establishes mechanical compatibility, not sound adoption.

This project-local Skill serves both assessment and implementation. Assessment authorizes investigation and a proposal; a request to add or upgrade also authorizes ready implementation within its accepted scope. Neither automatically authorizes publication or installation into user environments.

## Establish the source and affected scope

Read the external-source declarations in [the Skill registry](../../../skills/registry.json), available [lock records](../../../vendor/external-skills.lock.json), and listed patches. Inspect Git state, installed destinations, and managed outputs for existing work before selecting a workspace and comparison point.

| Starting point | Required baseline |
| --- | --- |
| First adoption from a new source | No installed baseline is expected. Establish source identity, reviewed target commit, selected Skills and complete behavior, license, dependencies, and local integration. |
| Adding a Skill from an existing source | Review the new selection as first adoption. Retain the recorded baseline for existing selections and assess any revision change as their upgrade. |
| Upgrading an installed Skill | Use the lock's resolved commit as the installed upstream baseline and compare the target with it and current local adaptations. A configured tag or branch does not identify those bytes. |

A missing lock record is normal for a genuinely new source or selection. Installed content with missing or unverifiable provenance needs investigation before replacement; calling it new adoption would bypass preservation and baseline review.

The registry and patches are canonical inputs. [The updater](../../../scripts/update_external_skills.py) derives distributed Skill trees, licenses, and lock records; express adaptations through those inputs.

Identify the requested source, selection, revision, and outcome. Verify the target against current upstream releases and repository content, distinguish a release from unreleased branch work, and record its resolved commit. If the target is open, recommend a supported release or revision and explain consequential trade-offs between stability and needed unreleased work. Missing or unverifiable target evidence blocks adoption while independent investigation may continue.

The registry revision and updater's `--source` operate on an entire upstream repository. Account for every selected Skill affected by a revision change. A newly selected Skill uses that same revision; if it needs a newer one, assess all existing selections and resolve any unavoidable scope expansion before implementation.

## Find what could change the adoption decision

For first adoption, read the complete selected Skills and their owned resources at the target revision. Trace required references, scripts, assets, and other Skill dependencies. Separate capabilities needed for the goal from optional branches and establish how consumers reach each supported branch with its prerequisites. A summary or recent changelog cannot establish complete introduced behavior.

For an upgrade, read release notes and compare old and target upstream trees for all selected Skills and owned resources. Establish why each local patch exists and whether the target supplies an equivalent result. Focus on changed behavior and its dependencies while preserving necessary guarantees outside the delta.

In both cases, follow affected instructions into local Rules, Skills, callers, and tools. Address upstream-internal ambiguity or conflict when it materially impedes local adoption; unrelated upstream features need no work merely because they exist.

### Compare consequences, not just text

For every newly selected or materially changed Skill, examine these questions:

| Concern | Evidence that matters |
| --- | --- |
| Behavior and composition | Triggers, obligations, stops, delegation, and side effects, read together with applicable Rules, native discovery metadata, and actual dependencies. |
| Local adaptations | The smallest necessary local differences for adoption; for upgrade, each patch's purpose and target counterpart. Distinguish context repair, equivalent upstream behavior, and changed intent. |
| Selection and overlap | Whether capabilities complement, duplicate, or replace local ones; effects of additions, renames, moves, removals, and new requirements on callers, registry, public exposure, and maintenance. |
| Dependencies and migration | Conventions, templates, links, scripts, commands, tools, and Harness capabilities. Dependencies outside selected trees need supported delivery or access; renamed formats may break consumers despite clean patches. |
| Provenance and effects | Source identity, license and attribution, executable or network behavior, and any new access, credentials, services, recurring cost, or trust requirement. |

Establish a conflict only when applicable clauses cannot both be satisfied for the same decision. Cite precise locations, conditions, the triggering case, and its consequence; apply precedence before proposing repair. Different stages can coexist. A missing explicit Skill name does not establish missing capability when Rules and native discovery supply the route. Distinguish static interpretation from observed invocation behavior and disclose consequential uncertainty.

Judge a replacement by the outcomes and necessary authorization, verification, and recovery guarantees consumers need. Different steps alone do not justify two Skills. Explain coverage, remaining gaps, and whether they merit small integration, a distinct capability, or deferred adoption. Include the old protocol's maintenance cost without transplanting steps whose purpose has disappeared.

### Put each adaptation with its owner

Compare a caller or Rule change with a vendored patch. A sound upstream design may need local integration; a patch is justified where an accepted difference must remain in the external Skill. Context-only patch repairs fit existing authority. Retire a patch only when its accepted result is supplied elsewhere or removal is authorized; making the updater pass does not justify losing that result.

For retirement or replacement, trace remaining references, public exposure, terms, protocols, documentation, and checks. Separate required cleanup from optional simplification. Recommend bounded follow-up where the old dependency caused surrounding complexity; material expansion remains a user choice.

The assessment is ready when every selection and patch is accounted for, affected consumers and dependencies have a supported route or explicit gap, and material risks and choices are explained. Keep investigation evidence in the conversation; registry, lock, and patches remain durable provenance.

## Recommend and settle consequential choices

Lead with the scope that best serves the goal and why. Identify source and selection or baseline-to-target change, benefits, material risks, consumers, patch dispositions, migration work, and proposed verification and recovery. Prioritize what could change the choice.

For unresolved material choices, explain viable alternatives, trade-offs, recommendation, supporting evidence, and pivotal assumptions. Obtain recoverable evidence that could reverse the recommendation; otherwise identify the gap and next useful investigation or precise user input. Do the available analysis instead of asking for open-ended direction.

Ask and wait before a change to accepted scope or behavior, such as public adoption or retirement, names or activation, service or permission requirements, or broader consumer migrations. Reuse supplied decisions and authorization; routine repairs preserving the accepted result need no new approval. Assessment-only ends with the concrete proposal. Authorized adoption or upgrade proceeds once scope, behavior, prerequisites, and checks are settled.

## Apply through the updater

Retain original inputs and recorded outputs through Git evidence or isolation. Reconcile managed-output drift before updating: preserve it, determine ownership and intent, express accepted changes in the owning patch, and only then restore the corresponding recorded output. Inspect new destinations too; an existing directory is evidence to reconcile, not permission to overwrite. Unclear ownership or preservation pauses the affected update for direction.

For a new source, declare its identity, reviewed revision, license, and selection in the registry. For an existing source, change only accepted revision, selection, or paths. Take exact fields, naming constraints, and supported source and license forms from current registry and updater validation. Confirm names and destinations coexist with first-party and other external Skills.

Create ordered patches against the resolved target, preserving upstream wording outside accepted deltas and all license and copyright notices. Include necessary local invocation metadata and packaged assets in patches. Use repository owners for authorized exposure, README coverage, and consumer changes, consistently with other external Skills. Retiring a contract includes affected callers, documentation, and checks.

Run from the repository root:

```bash
python scripts/update_external_skills.py --update --source <owner/repository>
```

Use the actual registry source ID, including for a new source, and consult `--help` when needed. Selected-source updates preserve other configured sources through their lock records; a missing record is a prerequisite gap, not permission to widen scope. Omitting `--source` updates all configured sources and requires that scope to be intended. A removed source ID cannot be selected, so whole-source removal requires planning the full update. Removing a selection from a retained source removes its managed destination.

### Respect the updater's representation and transaction

The updater normalizes CRLF to LF in staged UTF-8 resources without NUL bytes before patching, then normalizes patch output before hashing. Write patches against that representation. Binary resources and upstream checkouts remain unchanged; other whitespace, including Markdown hard breaks, is preserved. Text licenses use LF too. Repository Git attributes disable newline conversion for Skill trees and licenses so recorded bytes survive host settings, even for opaque resources with text suffixes.

The updater stages and validates patches before installing Skills, licenses, and lock together. A patch conflict leaves installed outputs intact; prior input edits still need review. Investigate failures before retrying. A transaction or rollback error requires inspecting actual files and saved Git evidence rather than assuming recovery succeeded.

## Verify the applied result

Read complete added or changed Skills with required resources and trace affected invocation paths. Check intended patch behavior, discovery, document conventions, and dependencies together. Run relevant supported checks for new or changed executable behavior; textual coherence does not establish runtime behavior, so report any specific verification gap.

Run the non-mutating check:

```bash
python scripts/update_external_skills.py --check --source <owner/repository>
```

Both update and check resolve upstream sources and may require network access; `--check` is not an offline lock inspection. Compare the resulting locked commit with the reviewed target. A moved target or new delta requires reassessment. Patch extent signals maintenance burden, not correctness.

Run applicable manifest, Rule-delivery, translation, and repository checks from their current owners and [CI](../../../.github/workflows/test.yml). Synchronize mirrors where project policy requires it. Inspect every changed or removed path, generated output, license, and lock entry against accepted scope, including surprises outside the selected source. Run `git diff <comparison-point> --check`, including new untracked files.

Completion requires reviewed selections and revisions installed in repository snapshots, coherent accepted behavior and consumers, passing required checks, and preserved existing work. Report source and revision changes, adopted or retired entries, consequential patch and migration decisions, evidence, and unresolved limits. Downstream publication and installation retain their own authority.
