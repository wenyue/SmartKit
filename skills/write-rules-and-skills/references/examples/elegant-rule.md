# Dependency Lockfile Policy

**Strength:** Mandatory
**Scope:** Repositories that adopt this Rule, when a change alters declared dependencies.

The repository's configured package manager owns each dependency lockfile. Regenerate the lockfile
with that package manager after an in-scope manifest change, and deliver the manifest and lockfile
together.

Use the package-manager version and options declared by the repository. Accept resolution changes
that follow from the requested manifest change; investigate unrelated dependency or metadata churn
before retaining it. A frozen or clean install must accept the resulting lockfile before the change
is complete.

When the declared package manager is unavailable, its version cannot be established, or
regeneration would require unapproved network access, leave the lockfile unchanged and stop with
the exact missing prerequisite. A lockfile is never repaired by hand.

This Rule governs lockfile consistency, not dependency selection, upgrade policy, credential use,
or permission to access a registry. A more specific repository instruction may override the
regeneration command or validation, but must preserve package-manager ownership and manifest-to-
lockfile agreement.
