---
name: rule-flutter
description: Use for Dart or Flutter work, including requested code-policy assessment.
---

# Dart And Flutter Guidelines

## Keep Behavior and Data Shapes with Their Owners

Keep owner-local behavior as instance members by default. Keep top-level functions for framework
entry points, file-level declarations, shared algorithms, or logic with no clear owner.

Use records only for small local tuple returns where a named type would not add clarity.

## Use the Filesystem Operation's Contract

Where `dart:io` is available, normally perform needed filesystem operations directly, including
reads, writes, creation, and deletion. Let operations expose their own failures to the established
recovery or reporting owner. A later operation need not reproduce an earlier transient lookup error.

Use a preliminary filesystem query, directly or through a wrapper, only when it offers a concrete
benefit. For queries such as `existsSync` or `typeSync`, treat a negative result such as `false` or
`notFound` as ambiguous between absence and lookup failure; it may also reflect a type mismatch.
Skip or default on that result only when lookup failure and absence are equivalent for the caller,
and any possible type mismatch is acceptable.

A positive result is an observation at check time. It guarantees neither permission nor subsequent
success; state can change.

Secure initialization and overwrite guarantees through the actual operation's semantics. An absence
check provides no such guarantee; a default write can truncate existing data.

## Preserve Resource and Context Lifetimes

Release controllers, subscriptions, and listeners owned by a `State` in its `dispose()` method.
Resources managed by the project's lifecycle mechanism remain with that owner.

After an asynchronous gap, verify that a captured `BuildContext` is still mounted before using it.
Resolve stable widget dependencies before the gap and read changing state only after the mounted
check.

## Close Routes Through Their Owning Navigator

Close Navigator-owned dialogs, sheets, and overlays through the Navigator that owns their route,
passing the return result. Account for nested Navigators when selecting that Navigator.

## Maintain Generated Sources Through Their Owner

Treat generated files as outputs. Change their source declarations and run the project's existing
owning generator. If generation is blocked, report the missing prerequisite instead of hand-editing
outputs.
