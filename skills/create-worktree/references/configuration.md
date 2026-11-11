# Worktree Configuration

This supported reference covers configuration preparation, later edits, and source lifetime. Resolve `<prepare>` as `scripts/prepare_configuration.py` beside this Skill, from the loaded SmartKit installation. Reading this reference does not invoke worktree creation.

## Prepare from the initialized source

Use Git-shared (`local`) configuration already supplied by checkout or carry. For `local-only` and `repository`, select required configuration and supporting files from the accepted, initialized source checkout. Both use the same local preparation; configuration-repository access is unnecessary. A setup marker alone does not establish source or host readiness.

Select exact files or configuration directories, such as `.agents/config.json`, `.agents/rules`, and `.agents/skills`, rather than the whole `.agents` tree with its worktree-local state. Review checkout-specific paths and required consumers before preparation. Keep exclusive access to the selected source and target during the operation.

```text
python "<prepare>" --help
python "<prepare>" prepare --source "<source-project>" --target "<target-project>" --path ".agents/config.json" --path ".agents/skills"
```

The helper prefers symbolic links and falls back to regular copies when the platform denies linking. Copies prune Git metadata, known caches and dependency directories, and worktree-local synchronization state before traversal; required source files must remain within the selected scope. Existing target content is preserved. The helper records each path's actual method and source in the worktree's private Git directory and narrowly excludes prepared paths from business Git without changing the index.

If a required host consumer cannot use a link, prepare that affected path with `--copy`. It can replace only a recorded link that still points to its accepted source.

```text
python "<prepare>" prepare --source "<source-project>" --target "<target-project>" --path ".agents/config.json" --copy
```

A failure retains its origin record and partial paths. Inspect them before retrying; matching copied files are retained, missing files are added, and conflicts require resolution. Successful preparation establishes selected file availability; verify actual instruction, Skill and host usability before declaring the worktree ready.

## Edit configuration at its recorded source

Before editing project Agent configuration in a linked worktree, inspect its origins. The command reports every project's mappings within that worktree; an absent record reports no mappings, while an invalid record fails rather than guessing a source.

```text
python "<prepare>" inspect --target "<worktree-or-project>"
```

Verify the recorded source and current link targets before editing. For linked paths, edit the resolved source file and preserve the link, including when an editor replaces files atomically. For copied paths, review current source and target contents, apply the same intended edit to both in the same operation, and verify both before reporting completion. This includes additions, renames and deletions beneath a recorded directory. Preserve unrelated differences; a conflict or unavailable source leaves the configuration edit incomplete. Paths outside the recorded scope retain their ordinary ownership.

Before renaming or deleting a recorded root, inspect origins across registered worktrees and include every affected link or copy mapping in the accepted change; otherwise retain the current paths. Rename the source and affected target paths, retarget symbolic links, and rename each key in the reported `record` under `projects[<project-relative-path>].paths`, retaining its method and local Git exclusion. After a deletion, remove the affected keys and emptied project entries. Write records atomically, preserving other entries, then inspect again and verify all affected locations before completing the edit.

## Preserve sources during cleanup

Keep a linked source checkout available while another worktree depends on it. Before removing a worktree, inspect origins in the repository's registered worktrees, including nested project mappings, and resolve any links that depend on the checkout being removed. Preserve copied configuration changes not yet reflected in their source before removing their worktree. An origin record establishes the relationship, not that copies still agree or that discarding differences is authorized.
