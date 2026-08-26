# Owner Gate

The Owner Gate decides whether accepted obligations belong in a Rule, Skill, both, or neither. It
runs before the Run Contract freezes and also supplies the parent Skill's read-only Ownership Review
exit.

## Route a more-specific authoring owner

Before classifying obligations, determine whether governing Rules or an active caller establish an
applicable more-specific authoring owner. When one applies and the current invocation lacks that
owner's completed preclassification handoff, return a handoff that names the owner and supported
route, then stop before a Run Contract, role, or candidate write. A caller-qualified invocation may
continue only when it carries the completed handoff and an explicit Adapter selection; validate that
owner route before classification.

When no more-specific owner applies, continue with this generic gate. A direct invocation may later
select the Default Fresh Role Adapter under the Role Launch contract; that default never replaces a
required owner handoff.

## Classify the obligations

Use the accepted request, preserved obligations, current artifact when one exists, broader and narrower
owners, and discoverable environment facts. Classify each independently:

- `rule` — a persistent policy that constrains decisions across triggered jobs;
- `skill` — work that starts from a trigger and produces one bounded outcome;
- `environment-owned` — a fact reliably available from code, configuration, schemas, tool output,
  or another active owner and therefore not worth caching in an artifact; or
- `ambiguous` — current evidence still supports materially different owners.

Return one complete verdict: `rule`, `skill`, `split`, `environment-owned`, or `ambiguous`.
`split` requires at least one independently owned Rule obligation and one independently owned Skill
obligation.

For `split`, stop before candidate writes and return the Rule and Skill obligations as two candidate
requests. Each request starts a separate authoring run with its own semantic model, Candidate
Versions, fingerprint, and evaluation results.

## Compare ownership

Compare the supported verdict with the requested owner and, for an existing artifact, its current
owner.

- Continue without an ownership question when they align and the verdict is `rule` or `skill`.
- When they conflict, explain the evidence, the behavioral and loading effects of each supported
  placement, and the recommended retain, move, or split result. Return `ALIGNMENT_REQUIRED` before
  roles or writes.
- Return `ALIGNMENT_REQUIRED` when the verdict is `ambiguous`. Do not use requested packaging to
  settle semantic ownership.

When the complete verdict is `environment-owned`, identify the active owner and discoverable
evidence, return a no-candidate result, and stop without writing a Rule or Skill.

The selected owner must still satisfy its Rule or Skill semantics and every applicable evaluation
stage. A user choice resolves ownership intent; it does not turn a persistent policy into a
triggered job or waive a semantic gate.

## Return an Ownership Review

For an explicitly read-only review, inspect the selected artifacts and the related owners needed to
detect duplication or displacement. Return for each artifact:

- its current and supported owner;
- each obligation classification and the complete verdict;
- the evidence, effects, recommendation, and any exact missing decision; and
- `PASS` when ownership aligns, otherwise `ALIGNMENT_REQUIRED`.

State that no file changed and stop before freezing a Run Contract or starting roles.
