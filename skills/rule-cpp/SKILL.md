---
name: rule-cpp
description: Use for C++ work, including requested code-policy assessment.
---

# C++ Boundaries and Ownership

Keep ownership visible in C++ interfaces and lifetimes, especially where native code meets another language, platform, or thread.

## Design interfaces around their owners

Preserve existing ABI, FFI, and platform boundaries while keeping public interfaces narrow. Keep behavior with its owner. Group related inputs into an options type only when they form a stable concept.

Prefer value semantics and RAII for resource lifetimes. When a pointer owns a resource, prefer a smart pointer to a raw owning pointer.

## Carry failure and lifetime contracts across boundaries

Represent expected failures in the return contract; use exceptions for failures the surrounding boundary treats as exceptional.

Give shared mutable state one clear synchronization owner and use the narrowest suitable primitive. Across native callbacks, preserve cleanup, cancellation, and thread-affinity requirements.

## Verify behavior and leave mechanics to project tools

Test boundaries where native ownership, failure handling, or ABI behavior can regress. Let the repository formatter, compiler, and static-analysis configuration govern mechanical style and naming.
