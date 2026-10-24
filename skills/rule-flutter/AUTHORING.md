# Authoring Decisions

## Distinguish a lookup from the requested operation

Keep filesystem query results separate from operation guarantees. Negative queries can hide lookup failures, and positive queries can become stale; simplifying this guidance to "check whether the file exists first" would silently change failure behavior and overwrite safety. The entry permits useful queries while leaving success and initialization guarantees with the actual operation.
