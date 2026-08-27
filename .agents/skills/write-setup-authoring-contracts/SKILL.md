---
name: write-setup-authoring-contracts
description: Author or revise a judgment-only Setup Authoring Contract under setup-assets/blueprints; excludes generated targets and shared SmartKit artifacts.
---

# Write Setup Authoring Contracts

Author the smallest complete descriptive contract that lets setup generate a future project Rule or
Skill from target-repository evidence. Apply `writing-for-agents` throughout. This project-private
Skill owns only Setup Authoring Contracts under `setup-assets/blueprints/`; generated targets and
shared SmartKit artifacts remain with their own authors.

## 1. Establish the contract and workflow

Read [`references/setup-authoring-contract.md`](references/setup-authoring-contract.md) completely.
Apply its Setup Contract Frame and judgment-only boundary using the accepted change, current
blueprint when present, setup catalog, governing contracts, and representative target evidence. For
an authorized creation path, repository-evidenced absence of a current blueprint is the explicit
baseline. Preserve supported existing semantics unless accepted intent changes them. Obtain every
fact that can change a generation-or-stop outcome; stop rather than inventing a target fact, owner,
policy, or action.

Durable meaning must come from an accepted user decision, Issue, Spec, ADR, governing contract,
setup catalog, or observable implementation evidence. `CONTEXT.md` and `CONTEXT-MAP.md` supply no
semantic authority, evidence, validation input, dependency, or durable terminology.

If the accepted input leaves material behavior, ownership, permission, validation, or exit
ambiguity, return `ALIGNMENT_REQUIRED` before acquiring a lock, launching a role, or writing the
Candidate. Report the unresolved choices, available evidence, decision owner, and consequences of
each choice. Only when every unresolved material choice is user-owned and `grilling` is available,
route the user to explicitly invoke it. The current invocation still ends with the no-effect
`ALIGNMENT_REQUIRED` result; if `grilling` closes every material branch, its shared decision becomes
accepted human-decision context for a new authoring run. Otherwise preserve the same stop. This
Controller-owned entry exit is distinct from bounded update requests and semantic-role
`HUMAN_DECISION_REQUIRED`.

Read the public [`Role Launch`](../../../skills/write-rules-and-skills/references/role-launch.md)
completely and explicitly select its **Default Fresh Role Adapter**. Apply its Role Launch
access, authority, Controller bounded-update, Role Boundary Audit, direct-channel,
abnormal-execution, and workflow-finalization mechanics. Record the Adapter Probe as `NOT_REQUIRED`
before any role starts.

Qualify exactly these identities: the Controller, one fresh resident Author retained through every
Candidate Version, and one fresh Static Reviewer retained through its correction cycle. The local
sequence is Author → applicable Machine Validation → Static Reviewer. Start only the Author before
the current version has Machine PASS or supported `NOT_REQUIRED`, and start the Reviewer only after
that outcome. Public Quality Review, Correctness Review, and executable Acceptance do not enter this
workflow. If the host cannot preserve the identities, loaded authority and access contracts, or
schedule, stop under Role Launch; never replace the resident Author.

Before acquiring the lock or starting the Author, freeze the complete accepted input and one
Setup-specific bounded update envelope. Enumerate every semantic evidence or dependency slot
eligible for a Context Supplement and every candidate-owned exact scope, path class, and operation
mode eligible for access expansion. Freeze one exact Candidate Allowlist containing only the
intended contracts under `setup-assets/blueprints/`; only the Author receives write access to it.
Acquire one exclusive candidate-writer lock. If the frozen interface establishes cleanly that no
lock was acquired and no lock state may remain, return pre-Author `LOCK_UNAVAILABLE`; if an attempt
may have left lock state, proceed to **Finish**. After acquisition and before any Author write, the
Controller fingerprints the complete Allowlist and binds that baseline to the initial Candidate
Version. Retain the lock through workflow finalization.

This step is complete when the evidence basis, judgment-only target, identities, schedule, Probe,
allowlist, update envelope, expected operations, lock interface, and pre-write fingerprint are
frozen without material ambiguity.

## 2. Author one whole-allowlist Candidate Version

Launch the resident Author with the complete accepted input, current blueprint or evidenced absent
creation baseline, selected evidence, writing guidance, exact allowlist, and one Authoring Scope or
bounded Repair Scope. The Author edits only that allowlist, owns Candidate meaning and finding
dispositions, and performs no validation, review, network use, or delegation.

The Author returns exactly one of Role Launch's four statuses with its complete authoritative
payload. `COMPLETE` also includes finding dispositions when applicable.

Fulfill `CONTEXT_REQUIRED` or `ACCESS_REQUIRED` only when the request matches the frozen bounded
envelope, then continue the same Author. An unavailable eligible update preserves the request as the
stop result. A material out-of-envelope change returns `ALIGNMENT_REQUIRED` and requires a new run.
Every stop after possible lock acquisition or role launch proceeds to **Finish**.

After every Author callback, apply the Role Boundary Audit and confirm that the Author remains the
sole candidate writer. Use the fingerprint bound to the prior Candidate Version as the before-state;
for any write, assign a new Candidate Version, fingerprint the complete Allowlist, and bind that
after-state to it. The step is complete only when an admissible `COMPLETE` describes the current
whole-allowlist version and its fingerprint.

## 3. Establish the Machine outcome for that version

Determine applicability from supported deterministic surfaces. When none exists, record Machine
`NOT_REQUIRED` for the current Candidate Version and invent no check. Otherwise run every applicable
machine check without fixing the Candidate. Fingerprint the complete Allowlist immediately before
and after each command, and retain both fingerprints with the exact command, final exit, and
relevant output. Any delta invalidates the result and stops under the Role Boundary Audit as an
unattributable Candidate change; preserve its evidence and send it neither to Author repair nor
Static Review. With an unchanged fingerprint, a failure returns the command evidence and a bounded
Repair Scope to the same Author. Audit and fingerprint every resulting Author callback.

For each new Candidate Version, use the changed paths, Change Summary, and before-and-after
fingerprints to decide which machine evidence it can affect. Rerun the failed check and every
invalidated or dependent check; reuse a result only when the change cannot affect what it proves.
The initial failure is not a round. A Machine disagreement round completes only after failure →
same-Author repair → rerun. The same failure across two consecutive completed rounds without new
evidence or a supported approach stops as `NO_PROGRESS`.

This step is complete when one current Candidate Version has either supported Machine
`NOT_REQUIRED` or PASS evidence for every applicable check. Only then launch the Static Reviewer.

## 4. Reach a Static Review fixed point

Give the persistent read-only Reviewer the complete accepted requirements, preserved obligations,
governing evidence, current whole-allowlist Candidate Version, and one representative walkthrough
input. It independently checks:

- **judgment-only form:** the contract describes required meaning and decisions without prescribing
  setup's generation procedure;
- **minimality:** removing any instruction would change a supported generation-or-stop outcome;
- **semantic completeness:** every behavior-changing target obligation is obtained or causes a
  stop; and
- **representative walkthrough:** one supported target input reaches exactly one generation or stop
  outcome without invented project facts.

Every finding contains a stable ID, problem and supporting evidence, concrete counterexample,
candidate location, severity, estimated Repair Scope, bounded repair direction, affected obligation
or surface, and preservation constraints; use `N/A` with a reason where a field does not apply.
Severity is:

- `critical` for semantic, authority, safety, ownership, executability, or exit failure;
- `material` for a supported defect that clearly reduces information quality, maintainability, or
  reliability; or
- `advisory` for a smaller improvement or a choice with several valid solutions.

Critical and material findings normally merit repair. A supported advisory repair limited to one
or two sentences or one small block is presumed worth fixing when it preserves semantics. The
Reviewer identifies the problem rather than drafting replacement prose, owns each finding and
whether it remains worth fixing, and sends it through Role Launch's direct correction channel. The
Author independently chooses `repair` or `decline` and owns every Candidate correction; the
Controller handles only the frozen control plane.

After every Reviewer callback, apply the Role Boundary Audit and confirm that the Candidate
Fingerprint is unchanged. For a finding, continue Reviewer finding → same Author correction →
applicable machine replay → same Reviewer recheck. After an Author write, repeat the whole-allowlist
audit and fingerprint, then apply the Machine invalidation rule before recheck. The initial finding
is not a round. A Static disagreement round completes only when Author disposition → same-Reviewer
reassessment remains unresolved. The same finding across two consecutive completed rounds without
new evidence or a supported approach stops as `NO_PROGRESS`.

This step is complete when the same Reviewer returns PASS for the same Candidate Version that holds
either Machine PASS or supported Machine `NOT_REQUIRED`. Close the Reviewer; start no other public
evaluation role.

## 5. Finish

Apply Role Launch workflow finalization on success and every terminal stop after a role launch,
successful lock acquisition, or acquisition that may have left lock state. End the resident Author,
the Static Reviewer, and every other safely endable identity while preserving reports and evidence.
Release the lock only after all role activity ends. A residual identity or unreleasable lock returns
`TEARDOWN_FAILED`; report the exact residual state and do not claim clean success.

Success requires Static Reviewer PASS and either Machine PASS or supported Machine `NOT_REQUIRED`
for the same whole-allowlist Candidate Version. Report the contract path and owner, fingerprint,
Machine outcome and any commands and exits, review verdict, rewinds, Role Boundary Audits, and
unresolved or untested surfaces. Hand the accepted contract to `setup-project-agents`. Generation,
commit, push, and publication remain outside this Skill.
