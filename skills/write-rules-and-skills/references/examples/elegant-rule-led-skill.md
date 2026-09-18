---
name: rule-operation-failure
description: Apply failure-propagation policy when designing, writing, modifying, or reviewing operation boundaries, or assessing their failure handling.
---

# Operation Failure

Strength: `Default`

Scope: Failure propagation and translation at operation boundaries in current development work,
and requested assessment of those boundaries.

## Preserve promised outcomes

Read the operation's promise and caller decisions before changing an outcome. Keep success,
ordinary absence or refusal, contracted failure, and programming violations distinct. A failed
read is not an absent record; catching its failure does not establish success.

Use the language's mechanisms and the project's failure contract. Translate at the boundary that
owns the caller-facing contract, preserving useful causes and remaining effects. Recovery may
establish success only by fulfilling the promise or an explicitly accepted degraded or partial
outcome; restoring future usability alone is insufficient.

## Handle at the responsible boundary

Propagate unless this boundary owns recovery, cleanup, compensation, required translation, or
final handling. Faithful transfer to a library's caller is a valid outcome. Before consuming a
failure, establish who retains responsibility for completion, state, and feedback.

Capture the narrowest failure type supporting the disposition. A broad capture is appropriate only
when every captured failure can safely receive that disposition. Explain why it must be broad
and why the disposition is safe in a meaningful maintainer comment at the capture site.

Keep the primary failure distinct from recovery or cleanup failures, carrying both and any remaining
effects to their owner. Preserve owned cleanup across success, failure, cancellation, and
interruption; asynchronous work needs owned completion, not merely successful launch.

## Apply within the current work

For settled propagation, confirm the contract and transfer to the caller. When changing a handler
or translation, test the affected public boundary: distinguish success, ordinary absence, and
failure, and exercise secondary failure or cancellation where relevant. Pause dependent changes
when the required disposition or authority remains unresolved.

For a requested assessment, cover the requested boundaries and include supported findings and
evidence gaps in the existing work report. Assessment alone authorizes no edits.