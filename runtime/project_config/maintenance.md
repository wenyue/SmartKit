# Project Configuration Maintenance

Shared reference for setup and explicit configuration maintenance. Resolve `<plugin-root>` from the loaded Skill installation and use `<plugin-root>/skills/setup-project-agents/scripts/workflow.py` as `<workflow>`. Resolve `<target-root>` as the business project. These resources must come from the same supported plugin distribution; an unavailable command, schema or resource leaves the dependent operation incomplete.

```text
python "<workflow>" project-config --help
```

The command help owns arguments and output details. The project schema at `<plugin-root>/setup-assets/catalog/project-config.schema.json` owns supported declarations; setup retains native rendering, ownership and full setup semantics. The commands handle source access and application mechanics, while the invoking Skill establishes intent, accepted changes and completion.

## Resolve the authoring source

The target's `.agents/config.json` records either explicit local maintenance or a repository, branch and project entry. A missing choice is readable legacy state: inspection reports that selection is required, and full setup asks once. A binding contains no machine-specific checkout path.

```text
python "<workflow>" project-config inspect --target "<target-root>"
```

Inspection is read-only. Use its source paths, target differences and retained state to establish what is available before choosing effects. Local mode keeps canonical inputs in the business project. Repository mode uses a persistent user-owned checkout, resolved by the runtime, and the entry `projects/<entry>/`. The checkout can contain the only copy of unpublished work; preserve it through failures and never treat it as a disposable session or artifact cache.

Each entry contains `manifest.json`, `config.json` and `files/`. The manifest explicitly selects individual source files; the portable config contains `skills`, `agents`, `mcp` and `settings`. Entries do not inherit from each other. Author using the business project's evidence and resolve linked support files within the selected entry; being in one private repository does not authorize changing another project.

Keep binding, successful local setup version, ownership records, credentials and runtime state with their existing owners. Select source instructions, Rules, Skills with necessary support, and custom Agent sources. Exclude setup-managed delivered plugin files, external snapshots, native adapters and generated indexes. The source `AGENTS.md` contains project instructions outside the generated `Project rules` section; setup continues to render that section. Host settings use only schema-supported structured fields, currently in `.codex/config.toml` and `.cursor/cli.json`, rather than whole host configuration files.

## Establish or deliberately change a binding

Setup owns the choice of maintenance mode and initial import. Read the command help before binding:

```text
python "<workflow>" project-config bind --help
python "<workflow>" project-config bind --target "<target-root>" --mode local
python "<workflow>" project-config bind --target "<target-root>" --mode repository --repository "<owner/repository>" --branch "<branch>" --entry "<entry>"
```

For repository mode, establish the user's personal private GitHub repository, selected branch and project entry. The remote default branch is a possible choice, not a value to assume. Reuse the same repository with a distinct entry for another project. Creating a new repository requires the user's specified identity and name and the explicit `--create-repository` flag. GitHub and Git authentication use the user's existing credential facilities; credentials do not enter the binding or portable source.

For a new entry, inspect existing target content and select accepted personal source files with repeated `--file` arguments to `bind`. Initial import preserves provenance and independent ownership; it does not claim every nearby file. For an existing entry, compare its source with the target before application. Preserve already tracked business-project files: local Git exclusions cannot remove their tracked status. Use the supported local-exclusion behavior for newly applied personal configuration, and expose any tracked-file ownership decision before taking it over.

Use `--replace-binding` only for a deliberate source switch. Compare the old source, current target and proposed source first, preserve unpublished and unadopted work, and establish which accepted content moves. A routine upgrade retains the binding.

## Update before editing

```text
python "<workflow>" project-config update --target "<target-root>"
```

The repository runtime verifies the personal private repository and selected checkout identity, uses authenticated access, and safely fetches and fast-forwards supported states. This route is distinct from setup's isolated public SmartKit and external Skill snapshot fetches. Missing tools, unavailable authentication or an unverifiable repository stops repository-dependent work.

Inspect and preserve existing staged, unstaged, untracked and unpublished work before updating. An unfinished operation, dirty checkout or divergence may be refused rather than reconciled automatically. Resolve the reported condition without discarding work or silently including it in this request. A refusal grants no reset, force push, automatic stash or history rewrite. After update, edit the selected source files and portable declarations within the accepted scope; use the applicable public authoring workflow for Rules and Skills. Initial import, authoring, guarded Agent adoption and generated setup outputs can leave accepted pending source edits in this same operation. Carry their evidence directly into validation, apply and publication; another clean-checkout update is not required between those steps.

## Apply accepted sources and protect target edits

```text
python "<workflow>" project-config apply --help
python "<workflow>" project-config apply --target "<target-root>"
```

Review the source changes and inspection's target differences before applying. Validate portable declarations and complete source files through their owning checks. Application writes canonical inputs while preserving binding and local state and respecting setup-owned surfaces. Then run the existing `sync-project` route for native outputs, or full setup when its prerequisites or the change require it. `project-config apply` does not render native adapters itself. Follow a reported full setup prerequisite under the invoking Skill; source application and local synchronization do not establish full setup success.

A first application can encounter existing target content without a prior applied-source record. Only after accepting the exact inspected differences may that application use `--accept-existing <inspect-fingerprint>`. The fingerprint limits acceptance to the inspected state; it does not authorize later drift. Subsequent target modifications require explicit adoption or another owner-approved resolution, not reuse of initial-collision acceptance.

The target's `.agents/project-config-state.json` records what source was applied for later comparison. Compare the last applied content, current source and current target when interpreting differences. Preserve both sides of a conflict. This receipt provides evidence, not new authority over setup's ownership records, generated section or delivered assets.

## Adopt selected target changes

```text
python "<workflow>" project-config adopt --help
python "<workflow>" project-config adopt --target "<target-root>" --file ".agents/rules/example.md" --field settings
```

Adoption requires the user's explicit choice of target edits to carry into the source. Inspect the last applied content, current source and current target, explain overlaps, and select only accepted files or portable fields through repeated `--file` or `--field` arguments. The example selects one Rule and the portable settings field; replace those selections with the actual accepted scope. Preserve all unselected target content and other source work. After adoption, validate, apply and verify through the ordinary path before publication.

## Publish an exact verified scope

Only an explicit maintenance-and-sync or adoption request includes the scoped commit and normal push. Setup by itself and ordinary project edits leave publication pending. Collect exact repository-relative source files changed for this request, including a changed manifest or portable config when applicable; whole directories and unrelated entry changes are not a commit scope.

```text
python "<workflow>" project-config publish --help
python "<workflow>" project-config publish --target "<target-root>" --path "projects/<entry>/files/.agents/rules/example.md" --message "Update project configuration"
```

Use repeated `--path` arguments for the complete accepted scope. Verify source and applied target agreement before publication. Commit hooks run normally: a hook-altered source must be revalidated and reapplied as needed before it can be published. Preserve preexisting staged and unselected work; an ambiguous selected path or an outgoing commit without verified scope requires resolution, not broadening the commit.

A publish failure can leave a valid local commit and an already applied target. Inspect the actual outcome first. To retry a retained verified commit, use the command's `--commit` route after confirming that the source and applied evidence still agree:

```text
python "<workflow>" project-config publish --target "<target-root>" --commit "<verified-commit>"
```

Remote advancement or divergence requires preserving the local commit and resolving the branch state before a protected retry. Normal publication must confirm that the intended commit is reachable on the selected remote branch; a successful-looking push message alone is insufficient.

Report source editing and validation, target application and local full setup, and remote publication separately. Repository-mode maintenance is complete only after its required target checks and remote confirmation succeed; local mode has no source-repository publication step. `setupVersion` changes only after successful local full setup; a subsequent push failure leaves that accurate local version intact while remote synchronization remains incomplete.
