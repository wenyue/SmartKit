# Authoring Decisions

## A version change and a migration answer different questions

The published baseline establishes what existing projects may still contain. Comparing only with current HEAD or treating every version mismatch as migration would miss pending release changes or force unnecessary setup. The workflow therefore settles the complete release's project consequences before synchronizing version fields.

## Migration history belongs to projects that skip releases

Independent version guides and stable published identities allow one setup run to satisfy all applicable changes. Draft entries can be reconciled for the same unpublished release; published history cannot be treated as disposable release-note text.
