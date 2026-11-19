---
name: maintain-project-config
description: Maintain project agent configuration shared with the project, kept only on this machine, or backed up in a separate personal configuration repository.
disable-model-invocation: true
---

# Maintain Project Config

Maintain agent configuration from the business project’s evidence. Author and verify it in the actual project first. In repository mode, then back up the explicitly selected, verified files in full. Explicit restoration goes in the other direction and does not author or publish configuration.

Resolve this directory as `<skill-root>`, its containing plugin as `<plugin-root>`, and the business project as `<target-root>`. Read [Project Configuration Maintenance](references/maintenance.md) before using `<skill-root>/scripts/maintain.py` as `<maintain>`. That shared reference owns binding, backup scope, restoration, local synchronization and publication recovery. Explicit setup restoration and enabled startup synchronization consume the reference and supported commands without invoking this user-only Skill. Resolve resources from the loaded plugin, independently of the target's working directory.

## 1. Establish the requested result and source

```text
python "<maintain>" inspect --target "<target-root>"
```

Inspection is read-only. Establish the maintenance mode, selected entry, backup scope, target differences and unfinished work. An inspection-only request ends with those findings and unavailable evidence; it authorizes no update, restoration, edit or publication.

| Situation | Establish before writing |
| --- | --- |
| Unbound project | Present project shared, this machine only, and separate configuration repository together; obtain the user's mode choice before binding. |
| Explicit restoration | Follow the reference's source-selection route: reuse a valid binding with a matching successful local restoration receipt, or ask for repository, branch, and entry. A copied binding alone does not establish this checkout's source. |
| Later maintenance of this checkout | Reuse its valid binding; infer no repository identity from business remotes or other checkouts. |
| Initialization over existing configuration | Analyze actual contents and differences, propose the concrete plan, and obtain the user's replacement decision. |

## 2. Separate authoring from restoration

Preserve staged, unstaged, untracked and unpublished work in the business project and configuration checkout. For explicit restoration, follow the [restoration route](references/maintenance.md#restore-explicitly-or-synchronize-at-startup): update the source first, never use a stale snapshot, then verify Git treatment and local prerequisites and report any that remain unmet. End the restoration there; it performs no rendering, full setup or publication. A decision during restoration to save local content to the backup is a separate, explicitly authorized operation.

## 3. Author and verify in the actual project

Edit the files maintained in the business project, not the backup entry’s `files/` as a drafting area. Decide content and checks from business-project evidence; the backup layout does not establish project architecture. For a Rule or Skill, use [Write Rules and Skills](../write-rules-and-skills/SKILL.md) with the local project files as its Candidate.

Proceed with authorized local authoring and verification in known scope where the work does not depend on an upstream decision, even if the configuration repository is unavailable or a sync conflict is unresolved. Preserve existing local work, do not infer backup scope or override a user decision, and leave upstream-dependent steps pending. Neither local mode requires configuration-repository access.

If the change requires local rendering, check that the command can run under the [local rendering route](references/maintenance.md#render-local-configuration-only-when-required). Complete independently runnable checks; if required rendering or checks are blocked, preserve the local result and report the missing verification without exporting it. Verify the local result, including any rendered changes and applicable Git treatment; report configuration paths already tracked by business Git. In either local mode, finish here without `apply` or configuration-repository publication. Maintenance does not establish full setup success; unmet setup or migration prerequisites remain for the user to invoke through the owning Skill.

## 4. Back up only the verified selection

In repository mode, follow the shared reference’s [local authoring route](references/maintenance.md#back-up-verified-local-authoring) to export this operation’s exact scope. Review the complete selected files before export; keep credentials, unrelated configuration and the local synchronization receipt out of the backup. Retain the adoption result JSON for exact-scope publication.

Confirm agreement across the backup scope before recording it. Do not use restoration to remove remaining differences; preserve and report upstream drift or unrelated local work that prevents agreement. If a later step fails, report the local changes and any saved backup work separately rather than claiming a cross-repository rollback.

## 5. Publish the verified source scope

Use [exact-scope publication](references/maintenance.md#publish-an-exact-verified-scope) for authorized repository writes unless the user requests a local result. Pass the retained JSON through `--plan` when it covers the complete accepted scope. For a scope assembled from direct edits or multiple operations, use repeated `--path` as documented in the reference. Preserve unrelated index entries and working changes. On failure, follow the reference's commit-hook and retained-commit recovery routes.

Completion requires validated source, target agreement, applicable checks, and the established publication outcome: verified remote publication, an explicitly requested local result, or no publication needed for this operation. Local modes require no configuration-repository publication.

Report mode and source, accepted and preserved paths, validation and restoration, any deliberate rendering, Git exclusions and tracked configuration paths, and the exact commit and verified remote outcome when applicable. For incomplete work, distinguish saved source, retained commits, applied target, unmet prerequisites, and remaining remote synchronization.
