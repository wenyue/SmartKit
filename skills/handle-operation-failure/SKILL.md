---
name: handle-operation-failure
description: Assess, diagnose, or design operation failure handling; use also during ordinary development when writing or materially changing a failure path or choosing failure contracts, recovery, retry, data-loss, final-handling, or remediation policy. Following a clear existing propagation policy alone does not require this workflow.
---

# Handle Operation Failure

Make a concrete operation's failure behavior coherent from its public promise to recovery or final
feedback. Work through the target's language mechanisms and actual project contracts; the outcome
may be a returned failure, an exception, or another supported completion protocol.

## Workflow

1. **Read the promise and its owners.** Inspect the operation, implementation, callers, and relevant
   contracts through the target's available code and filesystem tools. Establish success, ordinary
   absence or refusal, accepted degradation, failure, and programming-contract violations. Identify
   distinctions callers need and whether the boundary promises a closed vocabulary or permits
   unknown failures. Locate the independently initiated operation's final handling owner; for a
   library, establish the supported transfer to its caller. Discover applicable verification
   workflows from the project's agent instructions, Skill catalog, and owning test configuration.
2. **Trace the relevant paths.** Follow each in-scope outcome from its origin through translation,
   asynchronous completion, cleanup, and final handling. Include detached work, cancellation or
   interruption, consequential partial effects, and any remediation action. Check where required
   validation and invariants execute in production. Record evidence and gaps. Read
   [Failure Paths](references/failure-paths.md) when channels or ownership are ambiguous, or partial
   effects or remediation need investigation. For persisted or serialized state, read
   [Persisted Data Recovery](references/persisted-data.md).
3. **Determine each disposition.** Compare the observed behavior with the promise and caller
   decisions at the responsible boundary. Establish supported propagation, translation, cleanup,
   recovery, compensation, or final handling. For recovery, determine the valid resulting state,
   acceptable loss and its authority, retry safety and stopping bound, and the outcome if recovery
   also fails. Distinguish completing this operation from restoring future usability. Trace the
   primary failure, secondary failures, remaining effects, and useful diagnostics to their owner.
   Identify the incident's final reporter and the actual audience for feedback or human remediation;
   use impact, operational expectations, and the needed response to apply project-owned severity.
   Distinguish evidenced behavior from a proposed correction.
4. **Resolve readiness and state the judgment.** Cite evidence for each mismatch and the smallest
   coherent correction with its observable consequences. Investigate derivable facts before asking
   the collaborating user for a missing decision about disposition, acceptable loss, software or
   human ownership, or user burden; pause dependent implementation until it is resolved. An unknown
   root cause alone permits progress when existing contracts establish a safe disposition. General
   root-cause investigation uses the task's applicable diagnostic workflow. If access, tools,
   contracts, or permission are unavailable, state the gap and stop the action that depends on it.
   End without mutation when the request is assessment-only.
5. **Change and verify when authorized.** Implement at the owning boundary, preserving unrelated
   outcomes and supported contracts. Existing authorization for the design or fix remains usable;
   this Skill grants no additional remote or destructive permissions. Clarify caller obligations
   and recovery rationale only where code, types, and referenced contracts leave important meaning
   unclear, especially data-loss authority or retry safety. Verify through the responsible public
   operation or boundary using the discovered verification owners and available tools. Cover the
   meaningful success, absence or refusal, recovery, propagation, and final-feedback outcomes in
   scope, including unsupported recovery, retained state, secondary failure, cancellation or
   mid-path stops, and remediation completion or failure where applicable. A failed check is
   evidence for correction or an inconclusive result, never proof of the intended behavior.

Finish with a disposition or explicit evidence gap for every identified in-scope path. For changes,
report corrected mismatches and the proportional verification actually performed. State the scope
inspected, unresolved decisions, and untested surfaces; an evidence gap cannot count as a verified
path or completed correction.
