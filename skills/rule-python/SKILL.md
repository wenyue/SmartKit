---
name: rule-python
description: Use for Python work, including requested code-policy assessment.
---

# Python Contracts and Runtime Behavior

Use types to explain the supported runtime contract. An annotation should clarify what the program already means, while validation and resource handling make that meaning hold at runtime.

## Establish behavior before refining types

Preserve behavior in annotation-only changes. If typing exposes an ambiguous runtime case, establish its meaning from code, tests, or project policy rather than choosing new behavior to satisfy the checker. Before a supported behavior change in that branch, add and run a focused test establishing current behavior.

Use annotation and generic syntax supported by the repository's declared Python range, and import typing helpers only when needed.

## Make interfaces and states explicit

Annotate parameters and return values at public or reusable boundaries. Choose the return annotation for the function's actual contract:

| Function | Return annotation |
| --- | --- |
| Side-effect-only function | `-> None` |
| Coroutine function | The value produced after awaiting |
| Async generator function | An async iterator or generator type |

Name parameters unless the contract is genuinely open or forwards arguments and therefore needs `*args` or `**kwargs`. Make parameters keyword-only when a signature has several independently optional values.

Use `Protocol` for structural APIs and dataclasses or typed domain types for data shapes. Represent finite states with `Literal`, enums, or named types rather than boolean flags or an implicit `None` sentinel for meaningful state combinations. A cache that distinguishes "not loaded" from "loaded and absent", for example, needs explicit states instead of one `None` value for both.

Return one stable shape from each function. Use a named result, enum, or exception when outcomes have distinct meanings.

## Validate dynamic inputs and state mutation permissions

Keep `Any` at genuinely dynamic or untyped boundaries, then validate or narrow it before passing values into typed domain logic. Validate external mappings, serialized data, and untyped provider values before constructing typed domain values: an annotation alone does not perform that validation.

Use reflection, monkey patching, and metaprogramming only when a runtime boundary is inherently dynamic, and isolate them at that boundary.

Accept read-only collection abstractions such as `Mapping`, `Sequence`, and `Iterable` when mutation is not part of the contract. Require a mutable type when callers must permit mutation. These interfaces describe available operations; a read-only interface does not make the underlying object immutable.

## Keep local flow easy to follow

Declare variables near first use, annotate ambiguous or empty initial values, and keep nullable values on the narrowest practical path. Give each value name one role and one type rather than reusing it for different values.

Keep functions focused and the main path shallow. Handle invalid, absent, and no-op inputs early with the contract's return or exception outcome; an early exit must preserve that distinction.

## Preserve failure meaning and runtime enforcement

Raise precise domain or integration exceptions for expected failures. Preserve useful cause context when translating errors across a boundary.

Catch broad exceptions only at a boundary that owns the failure policy. Re-raise or translate any failure it cannot safely contain.

Use assertions for internal invariants, not user input or recoverable runtime failures. Because assertions can be disabled, keep production-required validation, control flow, side effects, and invariant enforcement effective without them.

## Carry ownership through deferred work

Capture stable dependencies before asynchronous or callback boundaries; read changing state when its current value is required.

Give every acquired resource one cleanup owner and make ownership transfer explicit. On every path that retains ownership, guarantee cleanup with a context manager, `try/finally`, or an owner lifecycle method.

## Leave mechanical policy to repository tools

Let the repository formatter, linter, and type-checker configuration own their mechanical policy.
