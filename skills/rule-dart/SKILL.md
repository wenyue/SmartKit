---
name: rule-dart
description: Use for Dart code, including Dart in Flutter and requested code-policy assessment.
---

# Dart Language Contracts

Apply these conventions to Dart language and library decisions.

## Choose an error representation

Use a concrete `Exception` for operational failures reported by throwing. Prefer an existing exception whose semantics fit the contract. Define a typed exception when callers need a stable category or fields beyond what an existing type provides. Use `Error` for a programming contract or invariant violation.

## Match failures by type

Prefer specific `on` clauses scoped to the operation whose failure the caller can handle. Use types or documented fields for programmatic classification and reserve exception messages for diagnostics. `on Exception` broadly intercepts its subtypes, and `on Object` and an untyped `catch` also intercept `Error` and arbitrary thrown objects.

Let programming defects propagate through operational recovery. If a documented or verified external-input API signals invalid input with a concrete `Error`, handle it only around that call and preserve the failed outcome with valid state.

## Preserve the error and its stack

Use `rethrow` inside a catch to propagate the original error and stack. To forward a captured error outside its catch, capture the `StackTrace` with the second catch parameter and pass the original object and trace to `Error.throwWithStackTrace` where the supported SDK provides it. When translating a failure, preserve the original object as separate cause evidence where needed. A replacement thrown with the captured stack carries the trace of the original throw, while the original object carries the failure's type and data.

## Place behavior and data shapes deliberately

Use instance members for owner-local behavior by default. Reserve top-level functions for framework entry points, file-level declarations, shared algorithms, or logic with no clear owner. Use records only for small local tuple returns where a named type would not add clarity.

## Let the filesystem operation establish its outcome

Where `dart:io` is available, normally perform the needed read, write, creation, or deletion directly. Let that operation expose its own failure to the established recovery or reporting owner; a later operation need not reproduce an earlier transient lookup error.

Use a preliminary query, directly or through a wrapper, only for a concrete benefit. Interpret queries such as `existsSync` and `typeSync` within their limits:

| Result | Meaning and permitted use |
| --- | --- |
| Negative, such as `false` or `notFound` | May mean absence, lookup failure, or a type mismatch. Skip or default only when absence and lookup failure are equivalent for this caller and any possible type mismatch is acceptable. |
| Positive | Describes the observation at check time. It guarantees neither permission nor later success, because state can change. |

Obtain initialization and overwrite guarantees from the actual operation's semantics. Checking absence cannot provide them, and a default write can truncate existing data.
