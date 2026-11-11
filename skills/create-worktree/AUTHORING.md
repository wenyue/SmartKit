# Authoring Decisions

## Preserve inherited state without transferring ownership

Keep default carry, staged-versus-unstaged fidelity, and the unchanged-source guarantee together. A convenient clean checkout can omit the work the user expects to continue, while a carried checkout can tempt a caller to commit inherited changes as its own. Readiness therefore verifies transfer without expanding commit scope.

## Keep workspace readiness separate from project health

The workflow verifies identity, preservation, required Agent configuration, and environment preparation; the implementation workflow owns project baseline, build, and test checks. Folding project health into workspace readiness would duplicate checks and obscure whether a non-ready result concerns workspace preparation or the code being changed.

## Establish Agent configuration before project Skill discovery

Ignored configuration can be absent in both local-only and repository modes, including the environment preparation Skill itself. Establish it before Skill discovery, using the initialized source checkout regardless of where that checkout obtained its configuration. This keeps worktree preparation independent of configuration-repository restoration.

Prefer symbolic links so configuration edits share their source even when editors replace files atomically. Copies retain origin mappings for equivalent edits and safe cleanup; they do not create a background synchronization service. File availability remains distinct from host activation.
