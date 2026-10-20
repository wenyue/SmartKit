# Project Configuration Maintenance

This Skill owns the shared configuration maintenance contract and command interface used by setup and explicit maintenance. Resolve `<plugin-root>` from the loaded Skill installation and use `<plugin-root>/skills/maintain-project-config/scripts/maintain.py` as `<maintain>`. Resolve `<target-root>` as the business project. These resources must come from the same supported plugin distribution; an unavailable command, schema or resource leaves the dependent operation incomplete. Consuming these resources does not invoke the user-only maintenance Skill.

```text
python "<maintain>" --help
```

The command help owns arguments and output details. The project schema at `<plugin-root>/setup-assets/catalog/project-config.schema.json` owns supported declarations. Maintenance commands own source access, binding, application and local synchronization under existing ownership checks; full setup retains initialization, delivery, migrations and successful local setup version updates. The consuming workflow establishes intent, accepted changes, permission and completion.

## Resolve the authoring source

The target's `.agents/config.json` records either explicit local maintenance or a repository, branch and project entry. A missing choice is readable legacy state: inspection reports that selection is required. The consuming workflow must establish the user's choice before binding or source-dependent changes. A binding contains no machine-specific checkout path.

```text
python "<maintain>" inspect --target "<target-root>"
```

Inspection is read-only. Use its source paths, target differences and retained state to establish what is available before choosing effects. Local mode keeps canonical inputs in the business project. Repository mode uses a persistent user-owned checkout, resolved by the maintenance repository support, and the entry `projects/<entry>/`. The checkout can contain the only copy of unpublished work; preserve it through failures and never treat it as a disposable session or artifact cache.

Each entry contains `manifest.json`, `config.json` and `files/`. The manifest explicitly selects individual source files; the portable config contains `skills`, `agents`, `mcp` and `settings`. Entries do not inherit from each other. Author using the business project's evidence and resolve linked support files within the selected entry; being in one private repository does not authorize changing another project.

Keep binding, successful local setup version, ownership records, credentials and runtime state with their existing owners. Select source instructions, Rules, Skills with necessary support, and custom Agent sources. Exclude setup-managed delivered plugin files, external snapshots, native adapters and generated indexes. The source `AGENTS.md` contains project instructions outside the generated `Project rules` section; the local synchronization commands render that section. Host settings use only schema-supported structured fields, currently in `.codex/config.toml` and `.cursor/cli.json`, rather than whole host configuration files.

## Establish or deliberately change a binding

Establish the user's maintenance choice and accepted initial import before binding. The commands record that choice; an existing remote or nearby source file alone does not establish intent.

Before repository binding or update, require Git and the GitHub CLI (`gh`) to be available, with `gh` authenticated as the repository's owning personal account on the selected github.com or GitHub Enterprise hostname. An existing private repository must be accessible to that account; creation follows the explicit route below. These operations use `gh` for repository verification and authenticated Git access. If a tool or required access is unavailable, report that prerequisite and stop repository-dependent work while preserving existing state. Credentials stay in the user's credential facilities, outside the binding and portable source. Read the command help:

```text
python "<maintain>" bind --help
python "<maintain>" bind --target "<target-root>" --mode local
python "<maintain>" bind --target "<target-root>" --mode repository --repository "<owner/repository>" --branch "<branch>" --entry "<entry>"
```

For repository mode, establish the user's personal private GitHub repository, selected branch and project entry. The remote default branch is a possible choice, not a value to assume. Reuse the same repository with a distinct entry for another project. Creating a new repository requires the user's specified identity and name and the explicit `--create-repository` flag.

Use `owner/repository` for github.com, or a full credential-free HTTPS repository URL for GitHub Enterprise, such as `https://github.example/owner/repository.git`. The URL's hostname selects authentication and separates its persistent checkout from same-named repositories on other hosts. Existing `owner/repository` bindings keep their github.com identity and checkout location.

For a new entry, inspect existing target content and select accepted personal source files with repeated `--file` arguments to `bind`. Initial import preserves provenance and independent ownership; it does not claim every nearby file. For an existing entry, compare its source with the target before application. Preserve already tracked business-project files: local Git exclusions cannot remove their tracked status. Use the supported local-exclusion behavior for newly applied personal configuration, and expose any tracked-file ownership decision before taking it over.

Use `--replace-binding` only for a deliberate source switch. Compare the old source, current target and proposed source first, preserve unpublished and unadopted work, and establish which accepted content moves. A routine upgrade retains the binding.

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

The target's `.agents/project-config-state.json` records what source was applied for later comparison. Compare the last applied content, current source and current target when interpreting differences. Preserve both sides of a conflict. This receipt provides evidence, not new authority over ownership records, generated sections or delivered assets.

## Synchronize established local configuration

Use the maintenance command to render local discovery and native Agent, MCP and settings mappings after canonical inputs change:

```text
python "<maintain>" sync-project --help
python "<maintain>" sync-project --target "<target-root>"
python "<maintain>" sync-project --target "<target-root>" --check
```

This route performs no fetch, blueprint authoring or full migration. It uses established ownership records and refuses changes requiring full setup. Its check mode reports drift without writing: exit 0 means clean, exit 1 means drift, and exit 2 means the check failed. Use the same route in local mode after editing the project's canonical inputs.

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

Adoption requires the user's explicit choice of target edits to carry into the source. Inspect the last applied content, current source and current target, explain overlaps, and select only accepted files or portable fields through repeated `--file` or `--field` arguments. The example selects one Rule and the portable settings field; replace those selections with the actual accepted scope. Preserve all unselected target content and other source work. After adoption, validate, apply and verify through the ordinary path before publication.

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

Report source editing and validation, target application and local synchronization, unmet prerequisites, and remote publication separately. Repository-mode maintenance is complete only after its required target checks and remote confirmation succeed; local mode has no source-repository publication step. `setupVersion` changes only after successful local full setup; maintenance and publication preserve that value.
