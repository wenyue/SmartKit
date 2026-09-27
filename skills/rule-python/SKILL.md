---
name: rule-python
description: Use for Python work, including requested code-policy assessment.
---

# Python Guidelines

## Preserve Behavior While Adding Types

Keep annotation-only changes behavior-preserving. When typing exposes an ambiguous runtime case,
establish its meaning from code, tests, or project policy instead of selecting new behavior to
satisfy the type checker. Before making a supported behavior change in such a branch, add and run
a focused test that establishes its current behavior.

Use annotation and generic syntax supported by the repository's declared Python range. Import
typing helpers only when needed.

## Make Signatures and States Express the Contract

Annotate parameters and return values at public or reusable boundaries, including `-> None` for
side-effect-only functions. Annotate coroutine functions with the value produced after awaiting;
annotate async generator functions with an async iterator or generator type.

Name parameters unless the contract is genuinely open or forwards arguments and therefore needs
`*args` or `**kwargs`. Make parameters keyword-only when a signature has several independently
optional values.

Use `Protocol` for structural APIs and dataclasses or typed domain types for data shapes. Represent
finite states with `Literal`, enums, or named types. Do not encode meaningful state combinations
as boolean flags or an implicit `None` sentinel. For example, if a cache distinguishes "not loaded"
from "loaded and absent", make those states explicit rather than giving both the same `None` value.

Return one stable shape from each function. Use a named result, enum, or exception when outcomes
have distinct meanings.

## Make Dynamic Data and Mutation Boundaries Explicit

Keep `Any` at genuinely dynamic or untyped boundaries, then validate or narrow it before passing
values into typed domain logic. Validate external mappings, serialized data, and untyped provider
values before constructing typed domain values: an annotation alone does not perform that validation.

Use reflection, monkey patching, and metaprogramming only when a runtime boundary is inherently
dynamic, and isolate them at that boundary.

Accept read-only collection abstractions such as `Mapping`, `Sequence`, and `Iterable` when mutation
is not part of the contract. Require a mutable type when callers must permit mutation. These
interfaces describe available operations; a read-only interface does not make the underlying object
immutable.

## Keep Local Values and Control Flow Clear

Declare variables near first use, annotate ambiguous or empty initial values, and keep nullable
values on the narrowest practical path. Give each value name one role and one type rather than
reusing it for different values.

Keep functions focused and the main path shallow. Handle invalid, absent, and no-op inputs early
with the contract's return or exception outcome; an early exit must preserve that distinction.

## Keep Failure Meaning and Production Checks Intact

Raise precise domain or integration exceptions for expected failures. Preserve useful cause context
when translating errors across a boundary.

Catch broad exceptions only at a boundary that owns the failure policy. Re-raise or translate any
failure it cannot safely contain.

Use assertions for internal invariants rather than user input or recoverable runtime failures.
Assertions can be disabled, so production-required validation, control flow, side effects, and
invariant enforcement must remain effective without them.

## Preserve Lifetimes Across Deferred Work

Capture stable dependencies before asynchronous or callback boundaries; read changing state when
its current value is required.

Give every acquired resource one cleanup owner and make ownership transfer explicit. On every
path that retains ownership, guarantee cleanup with a context manager, `try/finally`, or an owner
lifecycle method.

## Leave Mechanical Policy with Repository Tools

Let the repository formatter, linter, and type-checker configuration own their mechanical policy.
