# Project Configuration Maintenance

This Skill owns the shared configuration maintenance contract and command interface used by setup and explicit maintenance. Resolve `<plugin-root>` from the loaded Skill installation and use `<plugin-root>/skills/maintain-project-config/scripts/maintain.py` as `<maintain>`. Resolve `<target-root>` as the business project. These resources must come from the same supported plugin distribution; an unavailable command, schema or resource leaves the dependent operation incomplete. Consuming these resources does not invoke the user-only maintenance Skill.

```text
python "<maintain>" --help
```

The command help owns arguments and output details. The project schema at `<plugin-root>/setup-assets/catalog/project-config.schema.json` owns supported declarations. Maintenance commands own source access, binding, application and local synchronization under existing ownership checks; full setup retains initialization, delivery, migrations and successful local setup version updates. The consuming workflow establishes intent, accepted changes, permission and completion.

## Resolve the authoring source

The target's `.agents/config.json` records the selected maintenance mode and, for repository mode, its repository, branch and project entry. Present these three user-facing choices together, in the user's language; do not ask the user to combine separate source-location and Git-tracking switches.

| User-facing mode | Stored mode | Authoring source and Git treatment |
| --- | --- | --- |
| Project shared | `local` | Canonical inputs stay in the business project for sharing through its Git repository. SmartKit adds no personal configuration exclusions. |
| This machine only | `local-only` | Canonical inputs stay in the business project; configuration paths are excluded from business Git locally. No configuration repository or GitHub access is required. |
| Separate configuration repository | `repository` | Canonical inputs live in a personal private GitHub repository; target configuration paths are excluded from business Git locally. |

Existing `local` bindings retain project-shared meaning, and existing `repository` bindings retain their source. A missing choice is readable legacy state: inspection reports that selection is required. Establish the user's choice before binding or source-dependent changes. A binding contains no machine-specific checkout path. Selecting project-shared mode does not itself stage, commit or push business-project files.

```text
python "<maintain>" inspect --target "<target-root>"
```

Inspection is read-only. Its binding and source results do not audit Git exclusions; verify those separately when checking the selected mode. Use available source paths, target differences and retained state to establish what is available before choosing effects. Both local modes use the business project's canonical inputs without opening a configuration repository. Repository mode uses a persistent user-owned checkout, resolved by the maintenance repository support, and the entry `projects/<entry>/`. The checkout can contain the only copy of unpublished work; preserve it through failures and never treat it as a disposable session or artifact cache.

Each entry contains `manifest.json`, `config.json` and `files/`. The manifest explicitly selects individual source files; the portable config contains `skills`, `agents`, `mcp` and `settings`. Entries do not inherit from each other. Author using the business project's evidence and resolve linked support files within the selected entry; being in one private repository does not authorize changing another project.

Keep binding, successful local setup version, ownership records, credentials and runtime state with their existing owners. Select source instructions, Rules, Skills with necessary support, and custom Agent sources. Exclude setup-managed delivered plugin files, external snapshots, native adapters and generated indexes. The source `AGENTS.md` contains project instructions outside the generated `Project rules` section; the local synchronization commands render that section. Host settings use only schema-supported structured fields, currently in `.codex/config.toml` and `.cursor/cli.json`, rather than whole host configuration files.

## Establish or deliberately change a binding

Establish the user's maintenance choice and accepted initial import before binding. The commands record that choice; an existing remote or nearby source file alone does not establish intent.

Before repository binding or update, require Git and the GitHub CLI (`gh`) to be available, with `gh` authenticated as the repository's owning personal account on the selected github.com or GitHub Enterprise hostname. An existing private repository must be accessible to that account; creation follows the explicit route below. These operations use `gh` for repository verification and authenticated Git access. If a tool or required access is unavailable, report that prerequisite and stop repository-dependent work while preserving existing state. Credentials stay in the user's credential facilities, outside the binding and portable source. Read the command help:

```text
python "<maintain>" bind --help
python "<maintain>" bind --target "<target-root>" --mode local
python "<maintain>" bind --target "<target-root>" --mode local-only
python "<maintain>" bind --target "<target-root>" --mode repository --repository "<owner/repository>" --branch "<branch>" --entry "<entry>"
```

Both local modes accept no repository arguments or source-file import selections. For repository mode, establish the user's personal private GitHub repository, selected branch and project entry. The remote default branch is a possible choice, not a value to assume. Reuse the same repository with a distinct entry for another project. Creating a new repository requires the user's specified identity and name and the explicit `--create-repository` flag.

Use `owner/repository` for github.com, or a full credential-free HTTPS repository URL for GitHub Enterprise, such as `https://github.example/owner/repository.git`. The URL's hostname selects authentication and separates its persistent checkout from same-named repositories on other hosts. Existing `owner/repository` bindings keep their github.com identity and checkout location.

For a new entry, inspect existing target content and select accepted personal source files with repeated `--file` arguments to `bind`. Initial import preserves provenance and independent ownership; it does not claim every nearby file. For an existing entry, compare its source with the target before application.

Use `--replace-binding` only for a deliberate mode or source switch. Compare the old source, current target and proposed source first, preserve unpublished and unadopted work, and establish which accepted content moves. A repository source must converge with the target before replacing its binding; resolve pending differences through apply, explicit adoption or the owner's accepted recovery before retrying. Switching modes neither deletes the old source nor authorizes discarding target work. A routine upgrade retains the binding.

## Keep personal configuration out of business Git

Machine-only and repository modes maintain local Git exclusions for their target configuration, including canonical inputs, local configuration state and generated outputs discovered through the supported configuration and ownership records. Use the maintenance commands' exclusion handling after binding, repository application and local synchronization; full setup also maintains it through its completion route. Keep these exclusions in the target worktree's Git `info/exclude`, resolved by Git, with target-relative paths correctly anchored within the business repository, including a nested monorepo project. Preserve shared `.gitignore` files and unrelated local exclusions.

Local exclusions affect untracked files only. Preserve and report configuration paths already tracked by the business repository; choosing a personal mode grants no automatic untracking or history rewrite. Explain that those paths remain eligible for business-repository commits until the user separately chooses how to handle them. If the target has no Git worktree, report exclusions as not applicable rather than claiming a Git change.

When switching to project-shared mode, retire only the verified SmartKit-managed exclusion block for this target. Preserve and report any other rules that still ignore its configuration, including older exclusions whose ownership cannot be established. Project-shared mode restores normal Git eligibility where the tool owns the exclusion; it cannot promise that unrelated ignore rules will track those files. Inspection and `--check` never repair exclusions or write Git state. Treat a failed exclusion update as incomplete mode enforcement and report any configuration changes already saved.

Check actual Git treatment for the relevant target-relative configuration paths, for example:

```text
git -C "<target-root>" --literal-pathspecs ls-files -- "<configuration-path>"
git -C "<target-root>" check-ignore -v -- "<configuration-path>"
```

The first command lists tracked paths; the second identifies the matching ignore rule for an untracked path, with exit 1 meaning no match. Use these observations and the maintenance commands' tracked-path reports to describe the mode's actual effect; do not infer that an empty tracked-path list proves exclusions were installed.

## Update before editing

```text
python "<maintain>" update --target "<target-root>"
```

The repository support verifies the personal private repository and selected checkout identity, uses authenticated access, and safely fetches and fast-forwards supported states. This persistent checkout is distinct from isolated public SmartKit and external Skill snapshots. Missing tools, unavailable authentication or an unverifiable repository stops repository-dependent work.

Inspect and preserve existing staged, unstaged, untracked and unpublished work before updating. An unfinished operation, dirty checkout or divergence may be refused rather than reconciled automatically. Resolve the reported condition without discarding work or silently including it in this request. A refusal grants no reset, force push, automatic stash or history rewrite. After update, edit the selected source files and portable declarations within the accepted scope; use the applicable public authoring workflow for Rules and Skills. Initial import, authoring, guarded Agent adoption and generated setup outputs can leave accepted pending source edits in this same operation. Carry their evidence directly into validation, apply and publication; another clean-checkout update is not required between those steps.

## Apply accepted sources and protect target edits

```text
python "<maintain>" apply --help
python "<maintain>" apply --target "<target-root>"
```

Review the source changes and inspection's target differences before applying. Validate portable declarations and complete source files through their owning checks. Application writes canonical inputs while preserving binding and local state and respecting independently owned surfaces. `apply` does not render native adapters itself; follow it with the local synchronization route below. Source application and local synchronization do not establish full setup success.

A first application can encounter existing target content without a prior applied-source record. Only after accepting the exact inspected differences may that application use `--accept-existing <inspect-fingerprint>`. The fingerprint limits acceptance to the inspected state; it does not authorize later drift. Subsequent target modifications require explicit adoption or another owner-approved resolution, not reuse of initial-collision acceptance.

Only repository mode uses the target's `.agents/project-config-state.json` to record what source was applied for later comparison. Compare the last applied content, current source and current target when interpreting differences. Preserve both sides of a conflict. This receipt provides evidence, not new authority over ownership records, generated sections or delivered assets. Neither local mode needs an application baseline; a deliberate binding switch retires the obsolete receipt through the binding command rather than manual deletion.

## Synchronize established local configuration

Use the maintenance command to render local discovery and native Agent, MCP and settings mappings after canonical inputs change:

```text
python "<maintain>" sync-project --help
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project --target "<target-root>" --check
```

This route performs no fetch, blueprint authoring or full migration. It uses established ownership records and refuses changes requiring full setup. Its check mode reports drift without writing: exit 0 means clean, exit 1 means drift, and exit 2 means the check failed. Use the same route in either local mode after editing the project's canonical inputs.

When only the `AGENTS.md` generated `Project rules` section needs updating, use the narrower route, which does not require full setup ownership:

```text
python "<maintain>" sync-project-rules --help
python "<maintain>" sync-project-rules --target "<target-root>"
python "<maintain>" sync-project-rules --target "<target-root>" --check
```

Honor any reported prerequisite or ownership conflict. If full setup or migration is required, retain saved source and target progress, report what remains incomplete and wait for the user to explicitly invoke the owning Skill. Maintenance neither invokes full setup automatically nor reaches it through another workflow or callback. Reinspect source and target state before resuming dependent work after the prerequisite is satisfied.

## Adopt selected target changes

```text
python "<maintain>" adopt --help
python "<maintain>" adopt --target "<target-root>" --file ".agents/rules/example.md" --field settings
```

Adoption is a repository-mode operation and requires the user's explicit choice of target edits to carry into the source. Inspect the last applied content, current source and current target, explain overlaps, and select only accepted files or portable fields through repeated `--file` or `--field` arguments. The example selects one Rule and the portable settings field; replace those selections with the actual accepted scope. Preserve all unselected target content and other source work. After adoption, validate, apply and verify through the ordinary path before publication.

## Publish an exact verified scope

Only an explicit maintenance-and-sync or adoption request includes the scoped commit and normal push. Setup by itself and ordinary project edits leave publication pending. Collect exact repository-relative source files changed for this request, including a changed manifest or portable config when applicable; whole directories and unrelated entry changes are not a commit scope.

```text
python "<maintain>" publish --help
python "<maintain>" publish --target "<target-root>" --path "projects/<entry>/files/.agents/rules/example.md" --message "Update project configuration"
```

Use repeated `--path` arguments for the complete accepted scope. Verify source and applied target agreement and a clean local synchronization check before publication. Commit hooks run normally: a hook-altered source must be revalidated, reapplied and synchronized as needed before it can be published. Preserve preexisting staged and unselected work; an ambiguous selected path or an outgoing commit without verified scope requires resolution, not broadening the commit.

A publish failure can leave a valid local commit and an already applied target. Inspect the actual outcome first. To retry a retained verified commit, use the command's `--commit` route after confirming that the source and applied evidence still agree:

```text
python "<maintain>" publish --target "<target-root>" --commit "<verified-commit>"
```

Remote advancement or divergence requires preserving the local commit and resolving the branch state before a protected retry. Normal publication must confirm that the intended commit is reachable on the selected remote branch; a successful-looking push message alone is insufficient.

Report source editing and validation, target application and local synchronization, Git-exclusion status and tracked configuration paths, unmet prerequisites, and remote publication separately. Repository-mode maintenance is complete only after its required target checks and remote confirmation succeed; neither local mode has a source-repository publication step. `setupVersion` changes only after successful local full setup; maintenance and publication preserve that value.
