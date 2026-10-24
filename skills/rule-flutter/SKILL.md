---
name: rule-flutter
description: Use for Dart or Flutter work, including requested code-policy assessment.
---

# Dart and Flutter Ownership

Keep behavior, failure decisions, and lifetimes with the component that owns them. Apply the same principle to file operations, widget resources, navigation, and generated code.

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

## Preserve widget and resource lifetimes

Release a `State` object's controllers, subscriptions, and listeners in `dispose()`. Leave resources managed by the project's lifecycle mechanism with that owner.

Resolve stable widget dependencies before an asynchronous gap. After the gap, verify that a captured `BuildContext` remains mounted before using it, and read changing state only after that check.

## Close routes and regenerate outputs through their owners

Close Navigator-owned dialogs, sheets, and overlays through the Navigator that owns the route, passing the return result. Account for nested Navigators when choosing that owner.

Treat generated files as outputs: change their source declarations and run the project's existing owning generator. If generation is blocked, report the missing prerequisite rather than hand-editing the outputs.
