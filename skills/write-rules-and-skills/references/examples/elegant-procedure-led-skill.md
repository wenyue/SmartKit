---
name: replace-file
description: Validate a replacement for one existing file and confirm the saved result.
disable-model-invocation: true
---

# Replace One File

Replace one existing file while retaining a usable recovery copy until the result is confirmed.

## 1. Prepare and validate

**Establish the contract.** Identify the file, intended change, required checks, and authority to replace and recover it from the task and target's instructions. Choose a supported replacement method that protects intervening edits. Stop before writing if a prerequisite is missing.

**Prepare separately.** Make the replacement candidate and a readable recovery copy, including required properties. Confirm that the copy matches the original, and keep the original unchanged through preparation and validation.

**Validate the candidate.** Confirm the intended change and run every required check. On failure, keep the original in place while correcting and revalidating the candidate, or stop with the failed check. Proceed only when validation passes.

## 2. Replace and confirm

**Check for intervening edits.** Confirm that the original still matches the recovery copy, then replace it by the established method. If it changed, stop and resolve that change first.

**Verify the destination.** Read it, confirm that it matches the validated candidate, and run required checks. On replacement or verification failure, inspect the state. Restore the original only when established authority and method protect intervening work, then verify restoration. If safe recovery or verification is unavailable, preserve the recovery copy and report the known state and assistance needed.

Completion requires the destination to verify as the accepted candidate. Report a failed replacement even if recovery succeeds. Follow the target's retention requirements and task authority for the recovery copy, and identify any retained copy in the handoff.
