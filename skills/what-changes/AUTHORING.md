# Authoring Decisions

## Keep the confirmation tied to the reconciled scope

The implementation question follows resolution of pending items, and an earlier execution request does not answer it. This deliberate boundary lets the user approve the actual reconstructed scope after accumulated discussion, rather than treating scattered suggestions or a partial clarification as approval of an unseen combined change.

## Preserve the difference between active suggestions and uncertain goals

An active Agent suggestion remains visible as a labeled suggestion, while an unfinished older goal goes to pending confirmation only when its status is genuinely unclear. Collapsing both into agreed requirements would overstate consent; dropping both would silently lose active work.
