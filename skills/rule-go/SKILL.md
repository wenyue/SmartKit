---
name: rule-go
description: Use for Go work, including requested code-policy assessment.
---

# Go Guidelines

## Keep Package APIs and Initialization Deliberate

Keep public APIs product-driven. Meet test needs without exporting names, adding interfaces, or
introducing seams solely for tests or speculative reuse.

Initialize explicitly from constructors, `main`, or package-owned setup functions instead of
adding `init()` functions. Keep package globals deliberate, stable, and initialized in one place.

## Preserve Error Contracts Across Package Boundaries

Bind every returned error to a named value rather than the blank identifier, and check it. Handle
or propagate it through the owning contract.

The package's public error contract determines which errors cross its boundary. Give those errors
useful context and wrap them with `%w`; inspect them with `errors.Is` or `errors.As`. Wrapping makes
the underlying identity or type inspectable by callers, so preserve already promised inspection
behavior without unintentionally exposing implementation details as new API.

Translate implementation-only errors at the boundary that owns the public contract, retaining the
cause and diagnostic evidence required for final handling. Prefer an existing sentinel that
expresses the contracted outcome before creating a dynamic error.

Use `value, ok := x.(T)` and check `ok` when a type assertion can fail. Use `x.(T)` only when a
visible invariant guarantees the type.

Reserve `panic`, `logger.Fatal`, and `os.Exit` for top-level
startup paths where continuing is impossible.

## Honor Cancellation and Protect Shared State

Pass `context.Context` first where standard Go patterns apply. Honor its cancellation in loops and
long-running work.

Guard shared mutable state with the owning package's synchronization primitive.

## Use the Owning Package's Diagnostics

Use the owning package's logger conventions for runtime output instead of introducing `fmt.Print*`
or the standard `log` package. Make log messages name the operation and include values needed to
diagnose failure.

## Leave Mechanical Policy with Repository Tools

Let the repository formatter and linter own layout, naming, limits, imports, comments, and
suppression syntax. Change configured thresholds in their owning configuration rather than
duplicating them here.
