# Dart And Flutter Guidelines

Strength: `Default`

Scope: Dart and Flutter public surfaces, records, filesystem operations, widget lifecycle,
asynchronous context use, Navigator-owned routes, and generated sources.

## Public Surface And Ownership

- Keep owner-local behavior as instance members by default.
- Keep top-level functions for framework entry points, file-level declarations, shared algorithms,
  or logic with no clear owner.

## Records

- Use records only for small local tuple returns where a named type would not add clarity.

## Filesystem Operations

- Where `dart:io` is available, normally perform needed filesystem operations directly, including
  reads, writes, creation, and deletion. Let operations expose their own failures to the established
  recovery or reporting owner; a later operation need not reproduce an earlier transient lookup
  error.
- Use native `exists`/`existsSync` or `type`/`typeSync` only when a preliminary check offers a concrete
  benefit. A positive is a valid observation at check time under the queried API's semantics, but
  guarantees neither permission nor subsequent success; state can change. A negative may reflect
  absence, a type mismatch, or a lookup failure. Skip or default on a negative only when that remains
  acceptable if lookup failed rather than the object being absent.
- Secure initialization and overwrite guarantees through the actual operation's semantics, not an
  absence check; a default write can truncate existing data.

## Flutter Lifecycle

- Release controllers, subscriptions, and listeners owned by a `State` in its `dispose()` method;
  resources managed by the project's lifecycle mechanism remain with that owner.
- After an asynchronous gap, verify that a captured `BuildContext` is still mounted before using
  it. Resolve stable widget dependencies before the gap and read changing state only after the
  mounted check.

## Navigator Routes

- Close Navigator-owned dialogs, sheets, and overlays through the Navigator that owns their route,
  passing the return result; account for nested Navigators when selecting that Navigator.

## Generated Sources

- Treat generated files as outputs. Change their source declarations and run the project's
  existing owning generator. If generation is blocked, report the missing prerequisite instead of
  hand-editing outputs.
