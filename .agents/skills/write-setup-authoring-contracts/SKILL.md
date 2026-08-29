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
ambiguity, return `ALIGNMENT_REQUIRED` before launching a role or writing the Candidate. Report the
unresolved choices, available evidence, decision owner, and consequences of each choice. Only when
every unresolved material choice is user-owned and `grilling` is available, route the user to
explicitly invoke it. The current invocation still ends with the no-effect `ALIGNMENT_REQUIRED`
result; if `grilling` closes every material branch, its shared decision becomes accepted
human-decision context for a new authoring run. Otherwise preserve the same stop. This
Controller-owned entry exit is distinct from bounded update requests and semantic-role
`HUMAN_DECISION_REQUIRED`.

Read the public
[`Frozen Job Design`](../../../skills/write-rules-and-skills/references/job-design.md) and
[`Role Runtime`](../../../skills/write-rules-and-skills/references/role-runtime.md), and
[`Evaluation Lifecycle`](../../../skills/write-rules-and-skills/references/evaluation.md)
completely. Apply Frozen Job Design's Run Contract, Job Graph, grants, Candidate identity, baseline,
invocation-final observation, expected-proof-state, standalone-boundary, source/capability-class,
and bounded-update contracts. Apply Role Runtime as the single fixed runtime and common
evidence-selection policy unchanged, including its role-authority, Role Boundary Audit,
direct-channel, callback-composition, abnormal-execution, and workflow-finalization mechanics.
Apply from Evaluation only Machine Validation; Revision Impact current closure and compatibility;
applicable proof-owner fallback and replay; and global exits. Public Quality, Correctness, and
Acceptance roles and their semantic lifecycles do not enter this workflow.

Qualify exactly these identities: the Controller, one fresh resident Author retained from first
launch through finalization, and one fresh Static Reviewer retained through its correction cycle. The local
sequence is Author → applicable Machine Validation → Static Reviewer. Start only the Author until
public Machine current closure holds for the current fingerprint, and start the Reviewer only after
that outcome. Public Quality Review, Correctness Review, and executable Acceptance do not enter this
workflow. If the host cannot preserve the identities, loaded authority and access contracts, or
schedule, stop under Role Runtime; never replace the resident Author.

Declare Static Review as Role Runtime's caller-owned evaluation extension. This Setup Skill is its
complete semantic owner: it owns the finding schema and classifications below, `repair`/`decline`
dispositions, fixed-point and PASS mappings, correction cycle, semantic status composition, and
persistent-Reviewer schedule. Public Quality and Correctness retain their Evaluation-owned
semantics and do not lend them to this workflow. Role Runtime only transports, authenticates, and
audits Static callbacks and nonsemantic control metadata; it owns none of their meaning.

Before starting the Author, complete the Run Contract and Job Graph with the accepted input and
Setup-specific grants and bounded-update envelope under Frozen Job Design, preserving the Author's
`network: none` boundary. Enumerate every necessary-fact slot eligible for a Context Supplement and
every authorized local path class, external source and capability class, and already-authorized
mode eligible for access expansion. Freeze one exact Candidate Allowlist containing only the
intended contracts under `setup-assets/blueprints/`; only the Author receives write access to it.
For each Setup Machine proof class eligible for reuse, freeze Job Design's compatibility manifest
and fallback. Static `PASS` is not compatibility-eligible because this workflow requires the same
Reviewer to recheck the complete current Candidate after every correction.

Apply Frozen Job Design's Design-close fingerprint binding, materialized Frozen Run Contract,
single freeze, post-freeze baseline capture and confirmation, persistent-mismatch outcome, and
initial expected proof state unchanged. Setup supplies the exact Allowlist and Setup-specific
inputs to those public mechanics; it adds no identity, freeze, baseline, or mismatch transition.

This step is complete when the evidence basis, judgment-only target, identities, schedule,
allowlist, grants, discovery classes, update envelope, expected operations, frozen Candidate
identity, immutable baseline, and initial expected proof state are bound without material
ambiguity.

## 2. Author the whole-Allowlist Candidate

Launch the resident Author with the complete accepted input, current blueprint or evidenced absent
creation baseline, selected evidence, writing guidance, exact allowlist, and one Authoring Scope or
bounded Repair Scope. The Author edits only that allowlist, owns Candidate meaning and finding
dispositions, and performs no validation, review, network use, or delegation.

The Author returns exactly one of Role Runtime's four statuses with its complete authoritative
payload and all three public reports. Its Operation Report is the exclusive record of exact raw
operations, affected Candidate paths, and post-write observations. The Author reports no
Controller-observed Candidate fingerprint or canonical delta. Finding dispositions remain exclusively in
the public direct-discussion lifecycle and its disposition control metadata; they do not enter the
`COMPLETE` payload.

Fulfill `CONTEXT_REQUIRED` or `ACCESS_REQUIRED` only when the request matches the frozen bounded
envelope, then continue the same Author. An unavailable eligible update preserves the request as the
stop result. A material out-of-envelope change returns `ALIGNMENT_REQUIRED` and requires a new run.
Every terminal outcome after role launch proceeds to **Finish**.

After every Author return or completed termination, apply Frozen Job Design's invocation-final
capture, fingerprint and delta binding, and expected-proof-state transitions and Role Runtime's
Operation Report reconciliation, Role Boundary Audit, and exhaustive callback composition
unchanged. Setup adds only its local Author-result sequencing and Static disposition boundary. The
step is complete only when the public admissible-`COMPLETE` transition has promoted the current
whole-Allowlist fingerprint into expected proof state.

## 3. Establish the Machine outcome for that fingerprint

Determine applicability from supported deterministic surfaces. When none exists, record Machine
`NOT_REQUIRED` for the current Candidate fingerprint and invent no check. Otherwise run every applicable
machine check without fixing the Candidate. Fingerprint the complete Allowlist immediately before
and after each command, retain both fingerprints with the exact command, final exit, and relevant
output, and invoke Frozen Job Design's standalone boundary outcome composition. A command-attributed
change returns `ROLE_BOUNDARY_VIOLATION`; every other mismatch returns `CANDIDATE_CHANGED`. Preserve
its evidence and send it neither to Author repair nor Static Review. With an exact expected proof
state match, a failure returns the command evidence and a bounded Repair Scope to the same Author.
Audit every resulting Author callback through Step 2.

For each promoted Candidate fingerprint, use its Change Summary, Operation Report, and bound
canonical baseline-to-current delta to decide which machine evidence it can affect. Rerun the
failed check and every invalidated or dependent check; reuse a result only when the change cannot
affect what it proves and the frozen mechanical discriminator admits the public Revision Impact
compatibility binding that carries the unchanged Machine conclusion to the current fingerprint.
When impact is semantic or indeterminate, use the manifest's preauthorized proof-owner route if its
frozen lifecycle permits; otherwise rerun the affected check.
The initial failure is not a round. A Machine correction round completes only after failure →
same-Author repair → rerun. The same failure across two consecutive completed rounds without new
evidence or a supported approach stops as `NO_PROGRESS`.

This step is complete when public Machine current closure holds for the current Candidate
fingerprint through same-fingerprint proof or an authorized compatibility binding. Only then launch
the Static Reviewer.

## 4. Reach a Static Review fixed point

Give the persistent read-only Reviewer the complete accepted requirements, preserved obligations,
governing evidence, complete current whole-Allowlist Candidate and its fingerprint, and one representative walkthrough
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

The Static Reviewer exposes exactly one Controller-facing result per callback:

- `PASS` means its complete independent judgment finds no finding that remains worth fixing, every
  prior finding has a frozen disposition, no selected repair awaits a write, the latest finding-set
  state is `complete`, and the verdict names the current Candidate fingerprint; it maps only to
  same-fingerprint Static closure after the required Machine outcome;
- `FINDING_READY` means exactly one complete finding with its fixed stable ID is ready for Role
  Runtime's metadata bootstrap; the final finding alone marks the finding set `complete`, while a
  later `reopened` state requires newly available supported evidence and at least one distinct ID;
  it maps only to the named Author↔Reviewer channel bootstrap;
- `CONTEXT_REQUIRED` or `ACCESS_REQUIRED` means the exact common Role Runtime request and maps only
  to its matching frozen bounded-update transition; or
- `HUMAN_DECISION_REQUIRED` means the exact common terminal payload and maps only to the immediate
  global semantic stop.

These results are mutually exclusive and exhaustive. An absent, malformed, unknown, or multiply
mapped result is inadmissible under Role Runtime. `DISCUSSION_CLOSED` is only a channel event and
never a Static result or verdict.

Critical and material findings normally merit repair. A supported advisory repair limited to one
or two sentences or one small block is presumed worth fixing when it preserves semantics. The
Reviewer identifies the problem rather than drafting replacement prose, owns each finding and
whether it remains worth fixing, and sends it through Role Runtime's direct correction channel. The
Author independently chooses `repair` or `decline` and owns every Candidate correction; the
Controller handles only the frozen control plane.

Before any Static discussion, the Reviewer completes its independent review and freezes the whole
finding set, every stable ID, and the evidence that the set is complete for the reviewed Candidate
fingerprint. It then emits every finding through Role Runtime's `FINDING_READY` bootstrap, with the
completion marker only on the final finding. Only after every callback and the final completion
marker are audited does the Controller open the declared Author↔Reviewer pair for each finding.
Each pair completes its direct exchange and audited `DISCUSSION_CLOSED` events against that same
reviewed fingerprint. The Candidate remains write-free while any channel is open; no finding may
trigger an early correction that would make another finding stale.

The caller-owned `reopened` transition is available only when newly available supported evidence
establishes at least one distinct finding for the same unchanged Candidate fingerprint. It immediately
invalidates the prior finding-set completion marker. Preserve the Candidate and finish every
currently open channel; only after their audited `DISCUSSION_CLOSED` events does the same Static
Reviewer resume private judgment on that unchanged fingerprint. The Reviewer freezes the newly
supported distinct finding set and emits each finding through `FINDING_READY`; only the final new
emission restores finding-set `complete`. Then bootstrap and close every new channel under the same
lifecycle. While the set is `reopened`, or before every current and new channel is closed, permit no
Static Repair Scope, Author write, or `PASS`.

For every finding, the Author freezes exactly one evidence-based `repair` or `decline` disposition.
`repair` selects a write; `decline` selects none. The Reviewer independently freezes whether the
claim, severity, and worth-fixing state remain upheld. The Static fixed-point state is `reached`
only when the Reviewer no longer upholds a worth-fixing claim without a write, or both peers agree
that the selected repair addresses every upheld part pending write and recheck. It is `not reached`
when the Reviewer still upholds a worth-fixing claim and the Author declines or proposes a
non-resolving repair; `not applicable` is never emitted for a Static finding. A reached no-write
outcome closes that finding. A reached selected repair enters the correction cycle. A not-reached
outcome enters the next disagreement round or `NO_PROGRESS` rule below. Only the Reviewer-owned
`PASS` mapping above closes Static Review.

After every initial and reopened finding has been emitted, finding-set completion is current, and
every channel has closed, resolve each not-reached finding through its same-fingerprint disagreement
rounds before allowing a Candidate write. Once every finding has a frozen reached disposition,
combine all selected repairs and their preservation constraints into exactly one fingerprint-bound,
full-unit Static Repair Scope. Only then invoke the same resident Author once for the complete batch
through Step 2; never split that batch by finding or leave a selected repair pending against the
superseded fingerprint. A batch with no selected repair performs no Author write.

Apply the public pre-invocation comparison, Role Boundary Audit, callback composition, and
callback-independent standalone boundaries unchanged for every Reviewer invocation and
continuation. After the batched Author correction, apply the Machine invalidation rule, perform the
applicable Machine replay, and establish the required Machine outcome for the complete new Candidate
fingerprint before the same Reviewer rechecks that complete Candidate and fingerprint. The recheck judges
the whole unit rather than only the repaired findings. The initial finding is not a round. A Static
disagreement round completes only when Author disposition → same-Reviewer reassessment remains
unresolved. The same finding across two consecutive completed rounds without new evidence or a
supported approach stops as `NO_PROGRESS`.

A Revision Impact compatibility binding never replaces this required Static whole-Candidate
recheck.

This step is complete when the same Reviewer returns whole-Candidate `PASS` bound to the current
Candidate fingerprint and public Machine current closure holds for that fingerprint. Close the
Reviewer; start no other public evaluation role.

## 5. Finish

Apply Role Runtime workflow finalization and Frozen Job Design's post-safety and final standalone
comparisons unchanged on success and every terminal stop after role launch. Setup adds no teardown
or boundary mechanics; their exact terminal and residual results govern before Setup success is
evaluated.

Success requires Static Reviewer PASS bound to the current whole-Allowlist Candidate fingerprint
and public Machine current closure for that fingerprint. Report the contract path and owner, fingerprint,
Machine outcome and any commands and exits, review verdict, rewinds, Role Boundary Audits, and
unresolved or untested surfaces, identity teardown and residual state, every observed fingerprint and
promotion state, the canonical Evaluation-owned compatibility-binding evidence whenever it was
used for Machine current closure, and the final expected-proof-state comparison. Hand the accepted contract to
`setup-project-agents`. Generation, commit, push, and publication remain outside this Skill.
