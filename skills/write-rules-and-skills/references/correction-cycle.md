# Correction Cycle

## Findings

Every finding contains:

- stable ID;
- problem and supporting evidence;
- concrete counterexample;
- candidate location;
- severity: `critical`, `material`, or `advisory`;
- estimated Repair Scope;
- affected obligation or surface; and
- preservation constraints.

Use `N/A` with a reason for an inapplicable field. A Reviewer identifies the problem and evidence,
not replacement prose.

`critical` covers semantic, authority, safety, ownership, executability, or exit failure.
`material` covers a supported defect that clearly reduces information quality, maintainability, or
reliability. Both normally merit repair. `advisory` covers smaller improvements or choices with
several valid solutions; a supported repair limited to one or two sentences or one small block is
presumed worth fixing when it preserves meaning. The Author decides repair or decline; the same
Reviewer decides whether any finding remains worth fixing.

## Reviewer callback results

Each Quality or Correctness Reviewer callback, and each Acceptance Reviewer callback that judges
the Candidate, returns exactly one result: `PASS`, findings, `CONTEXT_REQUIRED`, or
`ACCESS_REQUIRED`. `CONTEXT_REQUIRED` names the missing fact or content and its use;
`ACCESS_REQUIRED` names the exact path, access mode, and reason. Neither request is a finding or
`PASS`, and neither transfers finding or verdict authority to the Controller. After a successfully
finalized Acceptance observation fails or cannot conclusively satisfy the frozen pass conditions,
the Acceptance Reviewer may instead return the Acceptance-only `fixture/environment defect` or
`ambiguous` classification defined in [`acceptance.md`](acceptance.md). The Reviewer owns that
classification; the Controller performs only the prescribed attempt orchestration from its
complete operative payload and resumes the same Reviewer with fresh Runner evidence. A `candidate
defect` returns findings under the four-result contract.

The Controller may fulfill a request only through the frozen Role Launch preauthorized update
envelope, then resumes the same persistent Reviewer. A material or out-of-envelope request returns
`ALIGNMENT_REQUIRED` and requires a new run. When an eligible update cannot be supplied, stop with
the applicable request status rather than replacing the Reviewer. A caller-owned Adapter may
further restrict eligible updates under its frozen contract.

## Persistent correction loop

For each Reviewer:

1. The Reviewer inspects the current Candidate Version and returns one of the four Candidate
   callback results above; handle any context or access request under that contract and resume the
   same Reviewer, and let only findings or `PASS` enter the remaining loop. Acceptance-only
   execution classifications follow their attempt-orchestration contract instead.
2. The Controller sends mutually consistent findings as one Repair Scope to the persistent Author.
3. The Author repairs supported findings directly, leaves declined findings unchanged, and returns
   dispositions and an Author Change Summary.
4. The same Reviewer receives the current Candidate Version, its own previous findings, and the short
   disposition payload defined in [`author.md`](author.md), but no chain-of-thought, intended prose,
   diff, or unrelated rationale.
5. Repeat until the Reviewer finds nothing worth fixing.

When supported findings appear incompatible, the Controller returns the conflict to their
responsible Reviewers for evidence or scope clarification; it does not select candidate meaning.
The Author then repairs or declines each clarified finding. If complete accepted evidence still
supports materially different outcomes, stop before another write with `ALIGNMENT_REQUIRED`, naming
the exact choice and decision owner. Two rounds with the same unresolved finding or conflict and no
new supported approach stop as no progress.

A review unit is the current stage's parallel Reviewer pair or the singular Acceptance Reviewer for
the current case. Both members of a parallel pair remain retained through the pair's correction
cycle. Every in-cycle Author change invalidates both local verdicts, and both Reviewers recheck the
complete Candidate Version. Close the pair only when both report PASS for the same Candidate
Version. A singular Acceptance Reviewer closes only at case PASS; when replay scheduling requires
closure after Stage-local PASS, the Acceptance contract records that current case PASS first. Later
invalidation of a closed review unit starts fresh Reviewer identities.

## Scope Transfer Notes

A Reviewer may attach Scope Transfer Notes as callback-level metadata independently of its callback
result. A note is neither a finding field nor a callback result, and it does not affect the
originating Reviewer's verdict. Each note contains the observation, evidence, location, and intended
owner. The Controller routes it once:

- to the other current Reviewer immediately;
- to a later stage before that stage's first verdict or action; or
- to an earlier passed stage after the current stage obtains local PASS.

The receiving Reviewer decides whether the note supports a finding. For a Controller-owned stage,
the Controller performs its existing action and uses that stage's evidence contract. A note that
may affect a passed stage invalidates that stage and follows the normal rewind; it does not create a
new semantic owner.

## Candidate Versions and rewinds

Each Author write creates a new Candidate Version. The Controller computes a compact fingerprint
over every candidate file before and after the write and enforces a single-writer lock. Reviewers,
Runners, and machine checks must not modify the candidate.

After an Author change, the same Reviewer or retained pair first rechecks the complete current
Candidate Version and obtains case- or pair-level local PASS. The Controller then compares the
Author Change Summary, changed paths, and fingerprint with earlier passed evidence. Return to the
earliest passed stage whose proof may no longer hold and start fresh Reviewers there; preserve
unaffected evidence. Inspect only a targeted diff when the compact signals are insufficient. A
future stage has not yet produced evidence and cannot be invalidated.
