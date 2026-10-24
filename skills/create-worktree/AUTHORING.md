# Authoring Decisions

## Preserve inherited state without transferring ownership

Keep default carry, staged-versus-unstaged fidelity, and the unchanged-source guarantee together. A convenient clean checkout can omit the work the user expects to continue, while a carried checkout can tempt a caller to commit inherited changes as its own. Readiness therefore verifies transfer without expanding commit scope.

## Keep workspace readiness separate from project health

The workflow verifies identity, preservation, and required environment preparation; the implementation workflow owns project baseline, build, and test checks. Folding project health into workspace readiness would duplicate checks and obscure whether a non-ready result concerns workspace preparation or the code being changed.
