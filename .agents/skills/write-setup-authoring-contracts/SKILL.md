---
name: write-setup-authoring-contracts
description: Author or revise a judgment-only Setup Authoring Contract under setup-assets/blueprints; excludes generated targets and shared SmartKit artifacts.
---

# Write Setup Authoring Contracts

Create the smallest complete descriptive contract that lets setup author a future project Rule or
Skill from target-repository evidence. Apply `writing-for-agents`. This project-private Skill owns
only Setup Authoring Contracts under `setup-assets/blueprints/`; it does not author the generated
target or shared SmartKit artifacts.

## Qualify the role and contract

Read [`references/setup-authoring-contract.md`](references/setup-authoring-contract.md) completely.
Use the accepted change, current blueprint, setup catalog, governing contracts, and representative
target evidence to apply its Setup Contract Frame and judgment-only boundary.

The contract must not depend on `CONTEXT.md`, `CONTEXT-MAP.md`, or terms defined only by those
documents. Durable meaning must come from an accepted user decision, Issue, Spec, ADR, governing
contract, setup catalog, or observable implementation evidence.

Read the public [`Role Launch`](../../../skills/write-rules-and-skills/references/role-launch.md)
definition completely. Explicitly select its Default Fresh Role Adapter. Apply the Role Launch
Interface, Default Fresh Role Adapter, Preauthorized Update Envelope, Role Boundary Audit, and
workflow-finalization sections for access, authority, bounded updates, audit, and teardown.

Qualify exactly three identities: Controller, one persistent Author, and one persistent Static
Reviewer. The complete local sequence is persistent Author → applicable machine validation → one
persistent Static Reviewer; public evaluation stages do not enter this flow. Start only the Author
before machine PASS and start the Static Reviewer only afterward. If the host cannot preserve those
three identities and the loaded authority or access contracts, stop; do not replace the persistent
Author. The Author alone receives candidate writes and the Static Reviewer remains read-only. No
parallel Reviewer capacity is required.

## Author and validate

Before the lock or Author, freeze the complete accepted input and the loaded update envelope:
declare every semantic evidence or dependency slot eligible for a Context Supplement and every
candidate-owned exact access scope, path class, and operation mode eligible for expansion. Candidate
writes remain limited to the explicit allowlist under `setup-assets/blueprints/`. Record the Default
Fresh Role Adapter's post-freeze Probe as `NOT_REQUIRED` before starting a role.

Acquire the single candidate-writer lock and retain it through workflow finalization. Start one
persistent Author. Give it the complete accepted input, current contract, selected target evidence,
and explicit allowlist. The Author edits only that allowlist and decides `repair` or `decline` for
each finding. It returns exactly one status:

- `COMPLETE`: Author Change Summary, changed paths, finding dispositions, and any uncertainty
  outside the Repair Scope;
- `CONTEXT_REQUIRED`: the missing fact and why authoring needs it; or
- `ACCESS_REQUIRED`: the exact path, access mode, and reason.

For `CONTEXT_REQUIRED` or `ACCESS_REQUIRED`, fulfill only an eligible bounded update from the frozen
envelope and continue the same persistent identity. An out-of-envelope material change returns
`ALIGNMENT_REQUIRED` and requires a new run. When an eligible update is unavailable, stop with the
request status. Every stop after lock acquisition or role launch follows the finalization contract
under **Finish**. The Author does not validate or review its work.

After each Author callback, apply the loaded Role Boundary Audit and enforce the one candidate
writer. Each Author write creates a new Candidate Version; compute a compact Candidate Fingerprint
over every candidate file after the callback.

Before starting the Static Reviewer, run every applicable machine check and retain each exact
command, final exit, and relevant output. On failure, give that evidence and a bounded Repair Scope
to the same Author. After every Author change, repeat the audit and fingerprint, then use the
changed paths, Author Change Summary, and before-and-after fingerprints to decide which prior
machine results the new Candidate Version can affect. Rerun the failed check and every invalidated
or dependent check. Reuse a prior result only when the change cannot affect what it proves. Two
rounds with the same failure and no new supported approach stop as no progress. Static Review
starts only when every applicable machine check has PASS evidence for the same current Candidate
Version.

## Static review cycle

Start one fresh Static Reviewer and keep it through the correction cycle. Give it accepted
requirements, preserved obligations, governing evidence, the complete Candidate Version, and one
representative walkthrough input. It checks:

- judgment-only form: the contract describes required meaning and decisions without prescribing
  generation procedure;
- minimality: no instruction can be removed without changing a supported generation-or-stop
  outcome;
- semantic completeness: every target obligation that can change behavior is obtained or causes a
  stop; and
- representative walkthrough: one supported target input reaches exactly one generation or stop
  outcome without inventing project facts.

Each finding contains a stable ID, problem and supporting evidence, concrete counterexample,
candidate location, `critical`, `material`, or `advisory` severity, estimated Repair Scope,
affected obligation or surface, and preservation constraints. Use `N/A` with a reason when a field
does not apply. `critical` covers semantic, authority, safety, ownership, executability, or exit
failure. `material` covers a supported defect that clearly reduces information quality,
maintainability, or reliability. Both normally merit repair.
`advisory` covers smaller improvements or choices with several valid solutions; a supported repair
limited to one or two sentences or one small block is presumed worth fixing when it preserves
semantics. The Reviewer identifies the problem rather than replacement prose. The Author decides
`repair` or `decline`; the same Reviewer decides whether the finding remains worth fixing.

The Static Reviewer remains read-only. After every Reviewer callback, apply the loaded Role Boundary
Audit and confirm the Candidate Fingerprint is unchanged.

Reviewer finding → persistent Author correction → same Reviewer recheck continues until no finding
is worth fixing. After each Author write, repeat the boundary audit and fingerprint. Before the
Reviewer rechecks, apply the same-version machine invalidation decision and machine-failure
correction loop above. Two rounds with the same unresolved finding and no new supported approach
stop as no progress. Close the Static Reviewer after PASS. Do not start a Quality pair, Correctness
pair, or executable Acceptance.

## Finish

After the lock is acquired or a role starts, apply the loaded workflow-finalization contract on
every success or terminal stop. Close the persistent Author and Static Reviewer and every other
safely endable identity, then release the candidate-writer lock only after their activity ends.
Report any teardown or lock-release failure and never claim clean success for that result.

Success requires machine PASS and Static Reviewer PASS for the same Candidate Version. Report the
contract path, owner, fingerprint, machine commands and exits, review verdict, rewinds, role
boundary audit, and unresolved or untested surfaces. Hand the accepted contract to
`setup-project-agents`; leave generation, commit, push, and publication to their owners.
