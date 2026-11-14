---
name: diagnosing-bugs
description: Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
---

# Diagnosing Bugs

Diagnose from evidence that distinguishes causes, then verify the smallest supported fix. Reuse an existing failing test or clear diagnostic evidence; use the phases below to fill real gaps, not to repeat work already done.

When exploring the codebase, read `GLOSSARY.md` (if it exists) to get a clear mental model of the relevant modules, and check ADRs in the area you're touching.

## Redact

This skill has you show commands, outputs and captured artifacts. **Redact every secret first**: write `<REDACTED>` in its place. Build loops against env vars, so the credential stays in the environment rather than in what you show. Captured artifacts carry auth headers: quote only the lines that carry the signal.

If the redacted output is not enough to diagnose the bug, say so and ask the user.

## Phase 1: Build a feedback loop

Start with the user's exact symptom and the evidence already available: a failing test, error, trace, timing measurement, or known-good comparison. Read the relevant code to understand that evidence and choose a check that could distinguish the likely causes. A repeatable pass/fail loop is usually the strongest feedback; build or reuse one when feasible, without treating its absence as a ban on investigation.

Spend effort where it improves the diagnosis. A check that exercises a nearby path but cannot detect the reported failure gives false confidence, however fast or repeatable it is.

### Ways to construct one, in roughly this order

1. **Failing test** at whatever seam reaches the bug: unit, integration, e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer) that drives the UI and asserts on DOM/console/network.
5. **Replay a captured trace.** Save a real network request / payload / event log to disk; replay it through the code path in isolation.
6. **Throwaway harness.** Spin up a minimal subset of the system (one service, mocked deps) that exercises the bug code path with a single function call.
7. **Property / fuzz loop.** If the bug is "sometimes wrong output", run 1000 random inputs and look for the failure mode.
8. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so you can `git bisect run` it.
9. **Differential loop.** Run the same input through old-version vs new-version (or two configs) and diff outputs.
10. **HITL bash script.** Last resort. If a human must click, drive _them_ with `scripts/hitl-loop.template.sh` so the loop is still structured. Captured output feeds back to you.

Prefer an existing supported check over a new harness when it exposes the same failure.

### Tighten the loop

Treat the loop as a product. Once you have _a_ loop, **tighten** it:

- Can I make it faster? (Cache setup, skip unrelated init, narrow the test scope.)
- Can I make the signal sharper? (Assert on the specific symptom, not "didn't crash".)
- Can I make it more deterministic? (Pin time, seed RNG, isolate filesystem, freeze network.)

Speed, repeatability, and unattended execution shorten the investigation, but are not fixed entry requirements. Keep a slower measurement when it is the cheapest check that captures the real behavior.

### Non-deterministic bugs

For intermittent bugs, record the conditions, attempts, and observed failures. Increase the reproduction rate with safe, bounded repetition or controlled timing when that helps distinguish causes. Stress and parallelism can alter behavior or consume resources; use them only within the task's permissions and stop when further attempts add little evidence. A low observed rate is a limit to report, not a reason to discard useful traces or claim that a finite green run proves absence.

### When a direct reproduction is unavailable

Use captured logs, traces, dumps, code paths, and version differences to form testable explanations. Label them as hypotheses until evidence distinguishes them. Choose a targeted inspection, replay, or test that could refute the leading explanation; do not change code merely because an explanation sounds plausible.

If a missing artifact or capability blocks the next useful check, state what you tried and request the specific access or redacted artifact needed. Obtain authorization before adding temporary production instrumentation. Continue independent, permitted investigation while that dependency is unresolved.

### Ready to investigate

Identify the evidence for the reported symptom, the next check, and what its possible outcomes would tell you. For a runnable loop, record the invocation and actual result, redacted. If the original failure has not been reproduced, say so; keep that limitation visible through verification rather than treating a substitute check as the original reproduction.

## Phase 2: Reproduce + minimise

When reproduction is available, confirm that it produces the user's failure rather than a nearby one. Capture the exact error, output, or timing and the conditions needed to interpret it. Repeat when needed to distinguish a real signal from noise.

Shrink a costly or confusing reproduction by removing inputs, callers, config, or steps one at a time and checking that the relevant failure remains. Stop when the remaining case usefully distinguishes causes and further reduction would add little value. Preserve the original scenario for final verification. If reproduction remains unavailable, investigate the existing evidence without claiming this phase succeeded.

## Phase 3: Hypothesise

Rank the explanations supported by the evidence. One strong explanation can justify the next check; consider alternatives when evidence is ambiguous or the check contradicts it. Do not invent hypotheses to meet a count or keep testing the first idea despite contrary evidence.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

If you cannot state the prediction, the hypothesis is a vibe: discard or sharpen it.

Share the leading explanation and alternatives when the user's knowledge or a consequential choice could change the investigation. Routine checks need no checkpoint; request a decision only when it is actually needed.

## Phase 4: Instrument

Each probe must distinguish a specific prediction from Phase 3. **Change one variable at a time** where practical so the result has an interpretable cause.

Tool preference:

1. **Debugger / REPL inspection** if the env supports it. One breakpoint beats ten logs.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end becomes a single grep. Untagged logs survive; tagged logs die.

**Perf branch.** For performance regressions, logs are usually wrong. Instead: establish a baseline measurement (timing harness, `performance.now()`, profiler, query plan), then bisect. Measure first, fix second.

## Phase 5: Fix + regression test

Write the regression test **before the fix**, but only if there is a **correct seam** for it.

A correct seam is one where the test exercises the **real bug pattern** as it occurs at the call site. If the only available seam is too shallow (single-caller test when the bug needs multiple callers, unit test that can't replicate the chain that triggered the bug), a regression test there gives false confidence.

If no correct test seam is available, record the verification gap and why the alternatives do not exercise the real bug pattern. Do not infer an architectural defect solely from missing access or environment support.

If a correct seam exists:

1. Turn the reproduction or supported bug pattern into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the original scenario when available and the relevant regression checks. If it remains unavailable, state what the test proves and what still needs verification.

## Phase 6: Cleanup

Required before declaring done:

- [ ] Re-run the original reproduction when available; otherwise state that it remains unverified. For intermittent bugs, report the tested conditions and failure counts, not a guarantee of absence.
- [ ] Regression test passes (or absence of seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix)
- [ ] Throwaway prototypes deleted (or moved to a clearly-marked debug location)
- [ ] State the supported cause, checks performed, and remaining uncertainty in the result and any commit / PR message. Distinguish a validated fix from a candidate fix or a blocked diagnosis.
