# Effect Recovery

Read this reference before the first state-changing effect or when resuming an unresolved attempt.
When selecting the read-only evidence helper for any route, read its [evidence
protocol](transfer-mechanism.md#read-only-evidence). File-transfer helper use and partial
restoration additionally follow the [transfer mechanism](transfer-mechanism.md).

## Operation receipt

Persist a small receipt outside every affected worktree. Reuse a workflow record that survives those
worktrees' removal. Record the job and route, source/target identities, accepted authority,
pre-state, intended effect and causal attempt identity. Append observations and residual state with
its continuation owner and retention/release condition. Include exact OIDs, paths and host
identities needed to distinguish completion from partial work; keep readable backups where hashes
cannot recover content.

Group operations by their retry/recovery decision: a guarded file batch or the history helper is one
attempt; push, PR creation and later removal are separate attempts. Record child effects needed to
distinguish completed, absent, in-flight and ambiguous work. Update the receipt before the next
dependent effect so a missing response cannot hide an already completed push, merge or deletion.

## Resume the incomplete effect

Re-observe through the authoritative Git/filesystem/host interface before any retry. Reconcile the
receipt with current facts: retain proven prefixes, prove an effect absent before attempting it, and
resume only the original incomplete suffix under still-valid authority and preconditions. An
ambiguous outcome remains unresolved while observation is unavailable. Never repeat a merge or PR
creation from a timeout or missing response alone. A proven push followed by PR failure resumes PR
establishment; a proven delivery followed by cleanup failure resumes cleanup.

Use the [public phase meanings](results.md) to distinguish an effect-free rejection from partial,
ambiguous or unproved effects. Recovery may resolve uncertainty and support continuation; retain the
original cause and observations, independently proven phases, and any publication fact.
