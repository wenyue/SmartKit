---
name: replace-file
description: Validate a replacement for one existing file and confirm the saved result.
disable-model-invocation: true
---

# Replace One File

Replace one existing file while retaining a usable recovery copy until the result is confirmed.

1. Establish the exact file, intended change, required checks, and authority to replace and recover
   it from the task and target's own instructions. Choose a supported replacement method that
   protects intervening edits. Stop before writing if these prerequisites cannot be established.
2. Prepare the replacement separately. Preserve a readable recovery copy of the original, including
   properties the target requires, and confirm that it matches the original. Keep the original
   file unchanged while preparing and validating the candidate.
3. Validate the candidate against the intended change and required checks. A failed check leaves the
   original in place: correct the candidate and validate again, or stop with the failed check.
   Proceed only with a candidate that passes every required check.
4. Confirm the original still matches the recovery copy, then replace it using the established
   method. If it has changed, stop and resolve that change before attempting replacement.
5. Read the destination and confirm that it matches the validated candidate and passes the target's
   required checks. If replacement or this verification fails, inspect the resulting state and
   restore the original only where the established authority and method protect intervening work.
   Verify any restoration. If safe recovery or its verification is unavailable, preserve the
   recovery copy, stop, and report the known state and the assistance needed.

Replacement is complete only when the destination verifies as the accepted candidate. Report a
failed replacement even if recovery succeeds. Retain or remove the recovery copy according to the
target's retention requirements and the task's authority; identify any retained copy in the handoff.
