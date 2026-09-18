# Persisted Data Recovery

Read this reference when a failure involves a persisted file, serialized payload, schema, or
migration state. Investigate its meaning and supported recovery before selecting a disposition.

## Establish The Data Contract

Identify the owner, the data's role, recovery authority, acceptable loss, and the state required
by the accepted outcome. Establish whether the recovery promise requires changing future reads and
whether this boundary has authority to mutate storage. Gather evidence using the relevant questions:

- For derived or cached data, what source supports rebuilding it, and is absence a valid state
  while rebuilding or after accepted discard?
- For access or local state, which actor or service recreates it, and which capability remains
  unavailable until then?
- For defaultable state, are the defaults valid, and is losing the displaced choices or progress
  accepted?
- For important, user-authored, imported, or sole-copy data, is an authoritative replacement
  available? What establishes authority for the specific loss and validity of the resulting state?
  Preserve the bytes while either decision is unresolved.
- For schema or migration metadata, how does its value control interpretation of other records and
  selection of required transitions?

The evidence may support accepted degradation, reconstruction, repair, or accepted discard. Exact
reconstruction is unnecessary when the accepted contract establishes a valid state without it. A
path, format, or corruption finding alone establishes no loss authority. Carry unresolved material
decisions back to the workflow's readiness step.

## Design And Check Recovery

Locate the failing phase: reading bytes, validating syntax or meaning, or executing the repair.
Separate evidence that content is invalid from evidence that I/O failed; inspect validation at the
boundary that understands the content rather than inferring corruption from an arbitrary failure.

For example, a read-only library's contract may permit skipping corrupt records and returning an
explicitly degraded result. Check that the result preserves the skipped-record impact and useful
diagnostics for its caller, and that later reads behave as promised while the stored bytes remain
unchanged. This contract can be fulfilled without persisted repair.

For a writable application, suppose the owning parser proves that saved sign-in state is structurally
invalid, the accepted data contract permits discarding it because sign-in reconstructs that state,
and recovery promises that later startup reads will no longer encounter the corruption. Confirm
the application's authority to remove the invalid bytes and verify that removal. The operation
that required authentication still reports it unavailable. Check that the resulting signed-out
state is valid and the next read no longer encounters the same corruption. If code, types, and
referenced contracts leave the loss authority or reconstruction assumption unclear, explain that
rationale beside the recovery.

If removal fails because storage is read-only, content recovery was supported but the attempted
repair did not establish the intended state. Follow the invalid-content cause, removal failure,
affected state, and any actionable path to the final owner rather than accepting defaults as proof
of recovery. For a proposed retry, identify what could change the condition, what effects repeating
the repair can have, and its stopping bound. Contrast this with sole-copy records whose loss is
unauthorized: preserve them and the failed outcome while the owner resolves recovery authority.

A migration marker illustrates why valid syntax alone cannot establish a repair. Replacing an
invalid marker with the current version can make old records appear migrated. Inspect how the
loader derives the prior version and runs missed transitions, and establish how the proposed
recovery preserves retained records' interpretation. Include async completion, interruption after
partial writes, repeat reads, and recovery failure in verification when those paths exist. Read
[Failure Paths](failure-paths.md) if effects, actor choice, feedback, or a remediation action require
further investigation.
