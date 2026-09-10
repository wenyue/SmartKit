# Dart And Flutter Guidelines

Strength: `Default`

Scope: Dart and Flutter ownership, data shape, state, lifecycle, UI, routing, models, generation,
and analysis boundaries.

## Baseline Applicability

- Treat `flutter_hooks`, `riverpod`, `go_router`, and `freezed` as the standard Flutter baseline.
- Apply each library section independently according to whether its dependency or generated surface
  exists; a task that adds or migrates the dependency takes its present branch.

## Public Surface And Ownership

- Keep owner-local behavior as instance members by default.
- Keep top-level functions for framework entry points, file-level declarations, shared algorithms,
  or logic with no clear owner.

## Data Shape

- Use records only for small local tuple returns where a named type would not add clarity.

## Flutter Hooks

- When hooks are present, use `HookWidget` for widget-local hook lifecycle and
  `HookConsumerWidget` when the same widget also consumes `riverpod`.
- Prefer built-in hooks for standard Flutter controllers and lifecycle. Introduce an owner-local
  custom hook when the same non-trivial lifecycle is reused.
- Call hooks unconditionally and in a stable order at the top level of `build()` or another custom
  hook. Set hook keys to the values whose change must recreate the owned state or resource.
- Pair a disposable resource created by `useMemoized` with cleanup in `useEffect`, or own both
  creation and disposal in one custom `HookState`.
- When hooks are absent, release owned controllers, subscriptions, and listeners in
  `State.dispose()`.

## `riverpod`

- Use `riverpod` for state shared beyond one widget or whose established feature or service owner is a
  provider. Keep widget-lifetime state and disposable UI resources in their owning widget or hook,
  even with a non-trivial lifecycle.
- When provider generation is configured, declare new providers with the project's `riverpod`
  annotations and generated provider pattern.
- Watch reactive state and dependencies during build, read them from event handlers, and listen
  only for side effects. Use `select` with `ref.watch` or `ref.listen` when only one part of a state
  object matters.
- Treat provider `build()` as reactive; it may run again whenever dependencies change.
- Immediately after creating each disposable provider resource, and before any `await`, register
  its `onDispose` callback. Use that callback only to release captured resources; keep state
  assignment, provider reads, and `Ref` access outside it.
- Let page-scoped and parameterized providers dispose with their consumers by default. Use
  `keepAlive: true` for services and repositories whose lifetime must not depend on one screen.
- After an asynchronous gap, verify that the provider is still mounted before using its
  lifecycle-bound state. Resolve stable dependencies before the gap; read changing provider state
  after the mounted check.
- When `riverpod` is absent, preserve the application's established state owner. Keep local state in
  widgets and use its existing shared-state mechanism rather than introducing a second one.

## GoRouter

- When `go_router` is present, use it for page navigation. When typed route generation is
  configured, declare typed routes and navigate with their generated route objects rather than raw
  path strings.
- Reuse the application's navigation facade, mounted-context resolution, guards, redirects, and
  failure reporting before calling lower-level router APIs directly.
- Use `go` when replacing the current location and `push` when adding a page that may return a
  result.
- Keep authentication, access, leave-admission, and navigation feedback decisions in their
  established route owner instead of duplicating them in callers.
- Use `Navigator.of(context).pop(result)` for dialogs, sheets, and overlays owned by Navigator.
- When `go_router` is absent, use the application's established Router or Navigator API and do not
  introduce a parallel routing system for one page.

## `freezed`

- When `freezed` is present, use it for immutable value, domain, and state types that need structural
  equality, `copyWith`, serialization support, or sealed variants.
- Use one immutable data case for one product state and a sealed union when variants have different
  data or behavior. Add JSON generation only at a real serialization boundary.
- Keep derived properties and domain behavior on the source type when its `freezed` declaration
  supports a private constructor.
- Keep persistence models separate from domain models when storage details, mutability, or schema
  compatibility differ; convert at the repository boundary.
- Keep framework-owned types, controllers, identity-bearing mutable objects, and types owned by
  another schema or generator in their native representation.
- When `freezed` is absent, use immutable Dart classes and sealed types, or the application's
  established model generator. Implement equality, copying, and serialization only when callers
  require them.

## Async Boundaries

- After an asynchronous gap, verify that a captured `BuildContext` is still mounted before using
  it.
- Resolve stable widget dependencies before the gap and read changing state only after the mounted
  check.

## Generated Sources

- Treat generated provider, route, serialization, `*.g.dart`, and `*.freezed.dart` files as
  outputs. Change their source declarations and run the project's owning generator.
