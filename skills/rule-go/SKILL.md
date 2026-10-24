---
name: rule-go
description: Use for Go work, including requested code-policy assessment.
---

# Go Package Contracts

Keep a package's public behavior deliberate: its API, error identities, initialization, and shared state should have clear owners.

## Design APIs and initialization for production use

Let product needs shape public APIs. Tests and speculative reuse alone do not justify exported names, interfaces, or new seams.

Initialize explicitly through constructors, `main`, or package-owned setup functions rather than adding `init()` functions. Keep package globals deliberate, stable, and initialized in one place.

## Handle every error through its owning contract

Bind every returned error to a named value, check it, and either handle or propagate it through the owning contract. Discarding an error through the blank identifier loses that decision.

The package's public error contract determines which errors cross its boundary. Give those errors useful context and wrap them with `%w`; inspect them with `errors.Is` or `errors.As`.

Choose what the caller can inspect deliberately. Wrapping exposes the underlying identity or type, so retain promised inspection behavior without unintentionally adding implementation details to the public API. Translate implementation-only errors at the boundary that owns that contract, preserving the cause and diagnostic evidence needed for final handling. Prefer an existing sentinel that expresses the contracted outcome before creating a dynamic error.

### Keep runtime checks and termination deliberate

Use `value, ok := x.(T)` and check `ok` when a type assertion can fail. Use `x.(T)` only when a visible invariant guarantees the type.

Reserve `panic`, `logger.Fatal`, and `os.Exit` for top-level startup paths where continuing is impossible.

## Honor cancellation and synchronize shared state

Where standard Go patterns apply, pass `context.Context` first. Make loops and long-running work honor cancellation.

Guard shared mutable state with the owning package's synchronization primitive.

## Diagnose through the owning package

Use the owning package's logger conventions for runtime output rather than introducing `fmt.Print*` or the standard `log` package. Name the operation and include the values needed to diagnose failure.

## Leave mechanical policy to repository tools

Let the repository formatter and linter own layout, naming, limits, imports, comments, and suppression syntax. Change configured thresholds in their owning configuration rather than duplicating them here.
