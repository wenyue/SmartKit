---
name: reproduce-symptom
description: Build a runnable reproduction of a reported software failure before investigating its cause.
---

# Reproduce a Symptom

Turn a bug report into a feedback loop that exposes the reported failure. The useful result is a
signal someone can run again while investigating, not a plausible explanation for the bug.

## 1. Find a signal for this symptom

Identify the triggering input or action, expected behavior, and observed deviation from the report
and available evidence. Locate a supported way to exercise that behavior within the task's access
and permission. Prepare a disposable reproduction without changing the implementation under test.

Spend the effort on the signal. A test, command, request, or small harness can all work; choose the
simplest one that reaches the reported behavior. A request returning successfully is insufficient
when the report concerns missing rows. A browser check is useful when the failure depends on an
interaction that a direct API call skips. Observe the property that separates the failure from the
expected behavior.

Run the reproduction and inspect the actual result. A setup error is evidence about the harness,
not proof that the reported failure occurred. Correct the harness within scope or identify the
missing prerequisite. Begin simplification only after the observation matches the reported symptom.

## 2. Make it useful to run again

Tighten the loop around the failure. Remove unrelated setup, control inputs that need to stay stable,
and reduce delay that would discourage repeated use. Keep context that affects the failure: a race
that vanishes when operations are serialized has not become a better reproduction.

Simplify one suspected distraction at a time and rerun. Retain a simplification only when the signal
still exposes the reported failure. This ties the smaller case to observation instead of assuming
that a shorter script represents the same bug.

For intermittent failures, keep the attempts and observed failure rate with the conditions that
produced them. A clean run does not establish absence. Improve repeatability where possible; report
remaining variability rather than disguising it as a deterministic check. Bound repeated execution
by the task's time, resource, and access limits.

## 3. Hand off the observed case

Leave the invocation, required inputs and setup, expected result, and captured failure together.
Keep secrets out of the shared invocation and output. Include known variability and what changed
while simplifying, so the next investigator understands the signal's limits.

A completed reproduction has been run, reaches the reported behavior, and captures the actual
deviation from its expected result. If the symptom cannot be observed within the available bounds,
return the attempts and the specific missing evidence or access as an incomplete reproduction.
A theory about the cause cannot substitute for the observation. Diagnosis and a production fix
remain separate tasks.
