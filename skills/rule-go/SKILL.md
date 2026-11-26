---
name: rule-go
description: Use for Go work, including requested code-policy assessment.
---

# Go Package Contracts

Keep a package's public behavior deliberate: its API, error identities, initialization, and shared state should have clear owners.

## Design APIs and initialization for production use

Let product needs shape public APIs. Tests and speculative reuse alone do not justify exported names, interfaces, or new seams.

Keep simple calls simple; use cohesive parameter structs with keyed literals when positional arguments obscure intent. Name them by role (`Request`, `Options`, `Config`), make defaults and meaningful zero values explicit, and distinguish omission only when needed. For grouped parameters, prefer plain structs; use functional options when composition or encapsulation benefits justify the added machinery.

Initialize explicitly through constructors, `main`, or package-owned setup functions rather than adding `init()` functions. Keep package globals deliberate, stable, and initialized in one place.

## Handle every error through its owning contract

Bind every returned error to a named value, check it, and either handle or propagate it through the owning contract. Discarding an error through the blank identifier loses that decision.

### Choose an error representation

Return an existing error directly when its identity and context already serve the caller. Use `fmt.Errorf` with one `%w` to add operation context when the cause belongs to the caller's inspection contract. A single `%w` supplies an `Unwrap() error` link.

Use an existing sentinel when it expresses a stable condition callers match by identity. Define a sentinel when the contract needs a new identity. Choose a custom error type when the contract needs more than an ordinary error and wrapper can supply, such as caller-inspectable fields, a distinct type for `errors.As`, or custom matching. If the type exposes a single cause, implement `Unwrap() error`.

### Match errors by identity or type

Use `errors.Is` for sentinels and `errors.As` for types, including wrapped errors. Keep messages for diagnostics. Wrapping makes the underlying error inspectable by callers. Translate implementation-only failures at the owning boundary and preserve the original error, its cause chain, and diagnostic context needed for final handling through the established reporting path.

### Preserve each relevant cause

Keep an existing representation when it preserves the promised matches, cause links, and structured details. Preserve a single-cause link when callers rely on `Unwrap() error` or `errors.Unwrap`.

Go 1.20 and later support error trees. Multiple `%w` verbs can add context while making both a sentinel and its underlying cause inspectable. `errors.Join` can retain separate relevant failures when each belongs in the returned error and must remain inspectable. Preserve any distinction the caller needs among those failures.

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
