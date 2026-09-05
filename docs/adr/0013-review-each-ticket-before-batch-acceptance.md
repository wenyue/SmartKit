---
status: accepted
---

# Independently accept each ticket before reviewing the combined batch

Implement a fixed dependency-ordered batch sequentially in one worktree created in clean mode from
an accepted committed base. Reuse its prepared environment: per-ticket worktrees would repeat
expensive setup, while carrying source changes would blur ownership and the tested commit boundary.

Each ticket has a fresh implementation Worker and independent Standards and Spec review. Create a
local candidate commit so the existing public code-review can inspect the complete committed diff;
repair by amending only that unpublished, unaccepted candidate. After review and required checks
pass, add the ticket completion trailer and independently prove the resulting boundary. A trailer
alone is insufficient evidence of acceptance. Already-satisfied tickets receive independent
requirement-based acceptance and an empty commit because public diff review rejects empty input.

Review and verify the combined batch before finalization, emphasizing interactions and overall
fulfillment. Final repairs use a new Worker and separate repair commit, preserving accepted ticket
commits. The implementation workflow owns formal review; finish-worktree consumes the final evidence
and owns finalization. A material blocker pauses the entire batch and preserves partial work.

This supersedes ADR-0007's batch-only review scheme while retaining one worktree, serial execution,
machine-readable ticket boundaries, and no separate Batch journal. Recovery uses attributable Git,
tracker, runtime and retained handoff evidence; missing review evidence requires renewed review,
while unprovable identity or effect state stops recovery. The additional per-ticket review and
candidate-acceptance work buy independent ticket completion without repeating environment setup.
