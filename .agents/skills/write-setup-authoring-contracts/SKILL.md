---
name: write-setup-authoring-contracts
description: Author or revise a judgment-only Setup Authoring Contract under setup-assets/blueprints; excludes generated targets and shared SmartKit artifacts.
---

# Write Setup Authoring Contracts

Author the smallest complete set of Setup Authoring Contracts under `setup-assets/blueprints/`.
This Skill owns only those contracts; generated targets and shared SmartKit artifacts remain with
their owners. Apply `writing-for-agents` throughout.

## 1. Establish the contract basis

Establish the contract from accepted user decisions, Issues, Specs, ADRs, governing contracts, the
setup catalog, the current blueprint when present, and observable target implementation evidence.
`CONTEXT.md` and `CONTEXT-MAP.md` supply no semantic authority, evidence, validation input,
dependency, or durable terminology. The setup controller and future Author may inspect the target
repository directly within their authorized access. Preserve supported existing blueprint semantics
unless accepted intent changes them. Preserve supported existing target semantics unless accepted
intent explicitly changes or retires them. Stop rather than invent a target fact, owner, policy, or
action.

For each exact intended contract path under `setup-assets/blueprints/`, establish from governing
evidence a Setup Contract Frame containing:

- the exact future target path, Rule or Skill semantic type, and target owner;
- the target-repository evidence setup must inspect and make available to the future Author;
- every behavior-changing target obligation, including preserved and changed obligations and
  non-goals;
- the paths the future Author may write, its other permissions, and the surfaces setup must
  validate;
- the conditions that distinguish supported target outcomes; and
- the exact material ambiguity, missing authority, or unsupported fact that stops generation.

If material behavior, ownership, permission, validation, or exit ambiguity remains, return
`ALIGNMENT_REQUIRED` before writing. Include every unresolved choice, its available evidence,
decision owner, and material consequences. Do not invoke `grilling`.

**Complete when:** the evidence supports an unambiguous scope for every contract and every
behavior-changing obligation has an accepted value or an explicit stop condition.

## 2. Write the contract

Write only the exact intended contract paths under `setup-assets/blueprints/`. For each contract,
express its established Setup Contract Frame as the meaning and evidence that setup must establish.
Keep related branches beside their triggers and give each outcome an observable discriminator.

Keep the contract judgment-only and minimal. Describe meaning and evidence, not how setup searches,
orders work, calls tools, writes files, retries, or implements generation. Leave implementation
facts with their owners, and do not generate the future Rule or Skill. Do not copy the future Rule
or Skill's procedure into the contract: a contract for a procedure-led target
remains descriptive while requiring the generated target to express the supported procedure.

**Complete when:** every supported generation-or-stop outcome follows from its contract without an
invented project fact, and removing any instruction would change a supported outcome.

## 3. Check and review

Run existing applicable deterministic non-fixing checks. If none exist, record `NOT_REQUIRED`.
Correct in-scope failures and rerun the affected checks.

Then statically review the complete contract set for:

- **judgment-only form:** it specifies required meaning and decisions without prescribing setup's
  generation procedure;
- **minimality:** every instruction changes a supported generation-or-stop outcome;
- **semantic completeness:** every behavior-changing obligation is established or causes an
  explicit stop; and
- **representative walkthrough:** for each contract, one supported target input reaches exactly one
  generation or stop outcome without invented project facts.

If an applicable check or review issue cannot be corrected within the exact intended contract
paths, stop with a blocked result. Report the check or criterion, evidence, blocker or owner, and
attempted corrections. If the issue exposes new material ambiguity, return `ALIGNMENT_REQUIRED`
with the Step 1 report instead. Neither outcome completes Step 3 or reaches handoff.

Repair every supported review issue, then repeat the complete review. If the same deterministic
check failure or static-review issue survives two correction attempts without new evidence or a
supported approach, stop as `NO_PROGRESS` and report the failed check or criterion and attempted
corrections.

**Complete when:** all applicable checks pass or are `NOT_REQUIRED`, and the complete current
contract set passes all four review criteria.

## 4. Finish

After Step 3 completes, report for each contract its path and owner, applicable checks and results,
four-criterion review result, and any non-blocking unresolved or untested surfaces. Report the
contracts as ready for `setup-project-agents`, the downstream owner; do not invoke that Skill or
generate downstream targets. Commit, push, and publication remain outside this Skill.
