# Design Judgments from Different Evidence

These fictional excerpts illustrate individual judgments and their effects on the next decision. Use [Report Format](../references/report-format.md) for the complete item and report.

## When an extra result wrapper can be removed

A service's `stop()` must return the same future on repeat calls, including re-entry from its cleanup callback. The PR adds a completer to make the result available before cleanup. The reviewer verifies that this mutex always defers the callback, even when idle, so `stop()` can cache the mutex's future before any re-entry and return it on every call. That evidence supports **Reasonable** for the behavior and **Optional improvement** to remove the extra completion bookkeeping. If the callback could run inline, direct caching after the call would leave a re-entry window.

## When an adapter earns its boundary

The only shared loading step for two configuration readers calls a third-party loader whose fixed interface takes a current-schema file and returns validated settings. The application still supports files saved in the previous schema, so a new application adapter converts them before calling the loader. Checks confirm the same settings and error behavior for both readers. Compatibility supports **Reasonable**. The shared adapter supports **Elegant** because converting inside the loader would require widening the library's schema contract and converting in each reader would duplicate the mapping. If all supported inputs already used the current schema and the adapter only forwarded calls, calling the loader directly could be an **Optional improvement**.

## When uncertainty affects the next decision

A parser starts rejecting a value the old version accepted. The new test proves rejection, and the supported input policy remains unresolved. Mark reasonableness **Uncertain**, name the missing policy decision and possible compatibility effect, and keep advancement pending until the correctness evidence is resolved.

In a separate review, M12 adds implicit context while preserving verified callback order and error handling. Source and checks establish supported behavior, and the reason for this extra mechanism remains open. Pass is pending and all other delivery prerequisites are satisfied.

> ⚖️ **Reasonable** · The changed path preserves the confirmed callback order and failure behavior.\
> 🎨 **Uncertain** · Implicit context makes ownership harder to follow, and the design constraints needed to judge whether it can safely be simplified are missing.

⚠️ M12's callback ownership is harder to follow, and the need for implicit context remains unverified. Continue the selected delivery with the warning.
