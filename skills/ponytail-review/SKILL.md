---
name: ponytail-review
description: >
  Quality review of a change: is the logic right, is it safe, does it hold
  under real load, is risky code tested, is it fast enough, and is every line
  needed. Reads the connected code, not only the diff. Each finding is
  explained in plain language. Use for technical-quality reviews of changes,
  commits or PRs, over-engineering reviews, or /ponytail-review. Use code-review
  for the separate project-standards and originating-spec check.
---

Review a change like the senior developer who will be paged when it breaks. Order of importance: correct, safe, holds under load, tested, fast, lean. Lean still matters: every extra line must be read, tested and fixed later. This is a report the user asked for, so give it in full.

Use [code-review](../code-review/SKILL.md) when project standards or originating-spec compliance must be checked.

## 1. Understand first

- Review what the user names: uncommitted or staged changes, a branch, a PR link, or files. Nothing named: the uncommitted changes, or the last commit if there are none.
- Read the diff, then the code it touches: callers of every changed function, the functions it calls, the tests, the README.
- Trace the supported caller and trigger: where data comes in, what is stored, what goes out. Establish the required outcome and what migration, validation, transaction, lock, or lifecycle owners already guarantee at each point. Internal values with established invariants differ from fresh input crossing a trust boundary.
- A change can break code it does not touch. When a signature, return value or behavior changes, grep every caller.
- Find the expected load in the repo (README, deploy config): one person running a script, or many users and processes at once. Judge scale against that, and say which load you assumed.

## 2. Look for

1. **Bug:** wrong result, crash, a supported edge case (empty, zero, last item, rounding, time zones), a caller broken by the change, or a fix applied in one caller while the responsible shared owner stays broken. Verify that the claimed path can occur under existing guarantees.
2. **Risk:** security holes (injection, weak randomness, secrets, missing checks at a trust boundary), data loss (errors swallowed, writes in the wrong order, missing required atomicity), or an asynchronous lifetime that loses valid new work. A supported contract and credible impact can justify protection before an incident; a hypothetical state already excluded by the owner cannot.
3. **Scale:** fine for one user, wrong for many: check-then-write races, the same work done by every process, memory or lists that only grow, a query per item, O(n^2) on big input, per-process state that must be shared.
4. **Missing test:** risky new logic (a branch, a parser, money, security, data writes, a bug fix) with no test that fails when it breaks. One good test, not coverage.
5. **Speed:** big slowdowns are problems. Small wins (work repeated in a hot loop) are suggestions; some software counts every millisecond.
6. **Lean:** code that should not exist or should be smaller.
   - delete: dead code, unused options, speculative features
   - reuse: the repo already has this helper (name the path)
   - stdlib / native: the standard library or platform already does it; a new dependency for a few lines
   - interface: examine every new function, type, parameter, flag, or public member. Establish the current need, compare an existing interface, direct call, or private owner-local solution, and weigh the knowledge and choices imposed on callers. A single caller can justify a cohesive responsibility; call count, a shorter body, testing convenience, and speculative reuse alone cannot.
   - yagni: abstractions, modes, or configuration with no supported current need
   - merge: near-copies that must change together
   - split: one function doing several unrelated jobs, so it is hard to read or test. Split by job, never by line count, and never into helpers that exist only to make a function shorter.

## 3. Check before you report

- A necessary finding needs an actual caller or supported entry, a credible trigger, the violated obligation, and its consequence. An optional improvement needs a concrete maintenance or caller burden and a worthwhile smaller alternative. No supported case, no finding.
- Re-read the path and its guarantees: the caller exists, the value can really be empty at that point, the code really is unused. A passing test or earlier decision to fix the code does not establish the original premise. If evidence disproves it, correct or withdraw the finding. If the need remains unknown, report that limit instead of inventing a defense or calling it an optional design choice.
- A shortcut marked with a `shortcut:` (or older `ponytail:`) comment that names its limit is a decision, not a complexity finding, unless the expected load already crosses it.
- Put the smallest sufficient fix with the responsible owner. Prefer deletion when it preserves supported behavior, including real trust-boundary checks and asynchronous cleanup. Adding a wrapper, mode, or public method still needs its own current purpose even when the behavioral repair is justified.
- No style taste, no "consider", no vague worries.

## 4. Output

Follow the shared language rules, including labels: short sentences, everyday words. Explain a technical term the first time you use it. The reader may never have seen this code.

Present findings first in three groups, skip empty groups:
- **Must fix:** bug, security, data loss, breaks at the expected load.
- **Should fix:** risky code without a test, real slowness, duplication, a function that mixes jobs, code that should not exist.
- **Nice to have:** small speed-ups, shorter forms.

Number findings across all groups, so the user can say "fix 2 and 5". Every finding has all four parts, each one or two short sentences. Keep the decisive caller, trigger, violated obligation or optional burden, existing guarantees, and repair owner in the Problem and Fix explanation so later repair can reassess the same premise:

2. **Orders land on the wrong day** (`billing/close_day.py:L40-52`)
   - **What this is:** At midnight this job closes the day and bills all orders of that day.
   - **Problem:** It takes "today" from the server clock, which runs in UTC. An order placed at 00:30 in Berlin is billed on the day before.
   - **Fix:** Compute the day once in the shop's time zone: `datetime.now(ZoneInfo("Europe/Berlin")).date()`. One line, nothing else changes.
   - **If we skip it:** Late orders show the wrong date, and accounting fixes them by hand.

After the findings, explain what this change does in two or three sentences. Include:
- `Verdict: no blocking findings in the reviewed scope.` or `Verdict: fix 1 and 3 first.`
- `Lean: -<N> lines possible.` when lean findings exist.
- `Not checked:` one line, if something mattered and you could not check it.

Nothing found: `No findings in the reviewed scope.`, then briefly explain the change and what you checked.

Lists findings, changes no code.
