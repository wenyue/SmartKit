---
name: rule-flutter
description: Use for Flutter framework work, including widget lifecycles, navigation, generated outputs, and requested code-policy assessment.
---

# Flutter Framework Ownership

Keep widget lifetimes, navigation, and generated outputs with their owning framework or project mechanism.

## Preserve widget and resource lifetimes

Release a `State` object's controllers, subscriptions, and listeners in `dispose()`. Leave resources managed by the project's lifecycle mechanism with that owner.

Resolve stable widget dependencies before an asynchronous gap. After the gap, verify that a captured `BuildContext` remains mounted before using it, and read changing state only after that check.

## Close routes and regenerate outputs through their owners

Close Navigator-owned dialogs, sheets, and overlays through the Navigator that owns the route, passing the return result. Account for nested Navigators when choosing that owner.

Treat generated files as outputs: change their source declarations and run the project's existing owning generator. If generation is blocked, report the missing prerequisite rather than hand-editing the outputs.
