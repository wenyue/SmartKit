---
name: migrate-versioned-data
description: Migrate one set of versioned local data with a verified recovery path.
disable-model-invocation: true
---

# Migrate Versioned Data

Use this procedure when ordering matters because a failed conversion could strand or corrupt local
data.

1. Establish the source and target formats, the data in scope, required compatibility, invariants,
   recovery point, and authority to write, recover, and control consumers. Stop before mutation if
   any is unknown or exclusive access cannot be obtained.
2. Prepare a converter that transforms the declared source version, returns an already-target version
   unchanged, rejects every other version, preserves each invariant, and leaves its input unchanged
   on failure. Keep readers compatible with both formats until retirement is authorized.
3. Run the converter on a copy of representative data. Compare semantic contents, exercise malformed
   input, and convert the result again to verify that a retry leaves it unchanged. Repair the
   converter and repeat this step until every check passes.
4. Stop readers and writers through the authorized control, then prove access is exclusive. Capture
   an immutable backup, record its checksum and record count, and verify that it can be read
   independently. If any check fails, resume consumers and stop without mutating the live data.
5. Convert the scoped live data once. While ordinary access remains blocked, immediately verify its
   target version, record count, and invariants, and exercise a target read with every supported
   consumer. If any check fails, retain exclusive access and restore the backup. Resume consumers
   only after the restored source verifies; otherwise keep access blocked and request recovery
   direction. Report the failed check.
6. After every target check passes, resume consumers.
7. Retire the backup or old-format reader only when the retention and compatibility requirements
   permit it. Otherwise, hand them off with their owner and expiry condition recorded.

The migration is complete when all scoped data verifies in the target format, supported consumers
can read it, no partial conversion remains, and every retained recovery or compatibility measure has
an explicit owner and removal condition.
