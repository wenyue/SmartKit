---
name: rule-cpp
description: Use for C++ work, including requested code-policy assessment.
---

# C++ Guidelines

## Keep Interfaces and Ownership Clear

Keep public interfaces narrow and preserve existing ABI, FFI, and platform boundaries. Keep
behavior with its owner; introduce an options type only when related inputs form a stable concept.

Prefer RAII and value semantics. Where a pointer owns its resource, prefer a smart pointer over a
raw owning pointer.

## Express Failure Through the Boundary's Contract

Make expected failure part of the return contract. Reserve exceptions for failures the surrounding
boundary treats as exceptional.

## Own Shared State and Native Callbacks

Synchronize shared mutable state through one clear owner and the narrowest suitable primitive.
Preserve cleanup, cancellation, and thread-affinity requirements across native callbacks.

## Follow Repository Tools and Verify Boundaries

Let the repository formatter, compiler, and static-analysis configuration own mechanical style and
naming.

Test behavior boundaries where native ownership, failure handling, or ABI behavior can regress.
