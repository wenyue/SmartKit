---
name: maintain-project-config
description: Maintain project agent configuration shared with the project, kept only on this machine, or backed up in a separate personal configuration repository.
disable-model-invocation: true
---

# Maintain Project Config

Maintain agent configuration from the business project's evidence. In repository mode, selected files and directories form a complete backup: author the accepted snapshot, restore it to the target, then publish the exact verified scope. Local modes keep their existing authoring and synchronization routes.

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

## 2. Update before editing

Preserve staged, unstaged, untracked and unpublished work in the business project and configuration checkout. Identify which pending source changes belong to this operation; unrelated entries remain outside its scope. In repository mode, update the persistent checkout before authoring or restoring:

```text
python "<maintain>" update --target "<target-root>"
```

Continue only when repository identity, branch state and access are verified. A failed update does not establish a current source; follow the reference's recovery route rather than restoring stale content. Both local modes author the business project's canonical inputs directly and require no configuration-repository access or publication.

## 3. Author the snapshot or adopt accepted target changes

Use business-project evidence to decide what configuration should say. The configuration repository's layout is a storage fact, not evidence of the project's architecture or required checks. Review the selected paths and their complete content, including machine paths and credentials, before backing them up. Full-file backup performs no field conversion or secret filtering.

For repository authoring, edit the selected files under the entry's `files/` and its manifest when the accepted scope changes. Preserve each selected file in full, including native MCP and settings files; backup does not consult `smartkit.lock.json` or regenerate those files. Keep the local synchronization receipt outside the backup. When writing or revising a Rule or Skill, use [Write Rules and Skills](../write-rules-and-skills/SKILL.md) with the source files as its Candidate and qualified business-project evidence; preserve its author and review responsibilities.

Adoption deliberately carries accepted target content into the backup. Inspect current source and target before choosing what to replace, then use exact files or directories, or refresh the entire declared scope:

```text
python "<maintain>" adopt --target "<target-root>" --file ".cursor/mcp.json" --file ".agents/rules"
python "<maintain>" adopt --target "<target-root>" --all
```

Read `adopt --help` for current options. `--all` refreshes only the files and directories already declared in the manifest. Preserve unselected source work. Adoption saves source content; validation, restoration and publication still follow. Record the exact changed repository-relative files, including manifest changes and deletions, for the final publication.

## 4. Validate and restore

Validate the accepted configuration through its applicable checks. In repository mode, inspect the proposed target differences and restore the accepted backup:

```text
python "<maintain>" inspect --target "<target-root>"
python "<maintain>" apply --target "<target-root>"
```

In either local mode, canonical inputs already reside in the target. Continue directly through the established local synchronization route below, without `apply` or configuration-repository access.

For every differing repository application, follow the reference's complete user-choice and exact inspected-state acceptance route before writing. That route governs later restoration, automatic synchronization, and repository-only changes as well as first use. It owns whole-synchronization acceptance, keep-local outcomes, drift, the conditions for skipping content writes, and receipt advancement; use those conditions rather than treating a saved source fingerprint as agreement.

Restoring a full-file snapshot ends with exact target agreement and checks of local prerequisites. A restore-only request performs no source authoring, generation, full setup or publication. If the requested configuration change also requires deliberate local rendering, use the reference's established `sync-project` or narrower `sync-project-rules` route and its ownership checks. Adopt any intentionally changed backed-up outputs into the source and re-establish agreement before publication. Neither restoration nor maintenance establishes full setup success; unmet setup or migration prerequisites remain for the user to explicitly invoke through the owning Skill.

Verify the selected mode's Git treatment, including paths already tracked by business Git, and complete the semantic or project checks needed for the change. Preserve saved source and target progress if a later step fails; report the actual recovery state rather than claiming a cross-repository rollback.

## 5. Publish the verified source scope

Repository-mode configuration-writing operations follow the shared reference's exact-scope publication default, unless the user requests a local result. Restore-only operations, whether manual or automatic, never publish. If this operation has no accepted pending source changes and no retained verified commit of its own, finish without publication.

```text
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.cursor/mcp.json" --message "Update project configuration"
```

Repeat `--path` for every accepted source change, including manifests and deletions. Preserve unrelated index entries and working changes. Follow the reference's normal commit-hook handling and protected `publish --commit` retry route when publication fails or is uncertain; maintenance grants no force push or history rewrite.

Completion requires validated source, target agreement, applicable checks, and the established publication outcome: verified remote publication, an explicitly requested local result, or no publication needed for this operation. Local modes require no configuration-repository publication.

Report mode and source, accepted and preserved paths, validation and restoration, any deliberate rendering, Git exclusions and tracked configuration paths, and the exact commit and verified remote outcome when applicable. For incomplete work, distinguish saved source, retained commits, applied target, unmet prerequisites, and remaining remote synchronization.
