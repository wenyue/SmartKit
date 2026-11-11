# Authoring Decisions

## Preserve inherited state without transferring ownership

Keep default carry, staged-versus-unstaged fidelity, and the unchanged-source guarantee together. A convenient clean checkout can omit the work the user expects to continue, while a carried checkout can tempt a caller to commit inherited changes as its own. Readiness therefore verifies transfer without expanding commit scope.

## Keep workspace readiness separate from project health

The workflow verifies identity, preservation, required Agent configuration, and environment preparation; the implementation workflow owns project baseline, build, and test checks. Folding project health into workspace readiness would duplicate checks and obscure whether a non-ready result concerns workspace preparation or the code being changed.

## Establish Agent configuration before project Skill discovery

Configuration readiness belongs to the shared worktree workflow because ignored project configuration may be absent in both local-only and repository modes, including the environment preparation Skill itself. Establish required configuration before discovering that Skill; its optional absence must not conceal missing configuration. Configuration maintenance retains source, copy or restore, conflict, and exclusion mechanisms. This preparation supplies the selected worktree rather than creating continuous synchronization between checkouts, and file availability remains distinct from host activation.
