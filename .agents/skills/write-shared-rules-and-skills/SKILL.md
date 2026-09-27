---
name: write-shared-rules-and-skills
description: Author or revise one portable cross-project SmartKit Rule or Skill.
---

# Write Shared Rules and Skills

Make guidance that remains justified across its supported projects. The difficult part is deciding
which meaning can travel with the artifact and which facts belong to a particular target.

This Skill qualifies one shared artifact, delegates its writing and review to
[`write-rules-and-skills`](../../../skills/write-rules-and-skills/SKILL.md), and checks the returned
evidence against its portability obligations. Keep authoring and review mechanics with that public
workflow.

## 1. Establish what can be shared

Continue with exactly one portable cross-project SmartKit Rule or Skill whose shared owner and
independent provenance are supported. Establish who owns its meaning and which environments it
claims to support before treating a useful local instruction as shared policy or method.

Resolve requests outside that scope before invoking the public workflow:

| Request | Route |
| --- | --- |
| Project-local artifact, Setup Authoring Blueprint, or another resolved nonshared request | Route to its supported owner. |
| Both a Rule and a Skill are needed | Return separate Rule and Skill requests for `split`. |
| `environment-owned` | Name the active owner and return no Candidate. |
| Ambiguous, incompatible, or unresolved ownership | Return `NEEDS_INPUT` through the public route, identifying the missing choice, relevant evidence, decision owner, and material consequence. |

### Separate portable meaning from target facts

For each fact the artifact relies on, establish its owner, provenance, applicability, and limits.
Admit it as portable meaning only when its cross-project owner and independent provenance support
that use. Existing Candidate text is a claim to examine, not evidence of its own authority.

Suppose an accepted shared requirement is to run each project's required checks before reporting
completion. A source project uses `npm test`. Its successful run supports that target's check route;
it does not establish the command for every project. Carry the accepted requirement into the shared
artifact and retain the command as a target fact within its supported scope.

The same distinction applies to source-project policy, repository layout, packaging and discovery,
host injection, tool availability, and information relayed by another Agent. They can locate or
support evidence; none establishes portable meaning by itself. Project and host instructions still
constrain the current work within their scope. They do not add portable meaning or permission to
the Candidate.

## 2. Prepare the public authoring input

Give the public workflow the knowledge it needs to write and assess this particular artifact.
Resolve the following concerns into one consistent input. Name obligations consistently enough to
trace them through review and handoff; choose a presentation that serves the task without imposing
obligation IDs or a record schema.

### Define the intended contract and its support

Make the accepted outcome, non-goals, safety boundaries, exits, and handoff clear. For every inherited
or new obligation, say what is to be preserved, changed, added, moved, or retired. This is the meaning
the Author must carry forward, rather than an outline copied from the old document.

Alongside that meaning, establish:

- **The Candidate's place:** shared owner, applicability, provenance, exact resources and presence
  expectations, and intended public loading, discovery, distribution, and Skill-interface routes.
- **The evidence behind it:** each source and its discovery route, the facts it supports, the scope
  it represents, and the limits specific to its source project.
- **The dependencies it consumes:** every direct and transitive Rule, Skill, tool, schema,
  environment capability, or host behavior; each one's owner, required behavior, consumers, supported
  shared- or target-owned route, and observable outcomes when available, unavailable, or failing in
  use.
- **The acceptance boundary:** validation and completion duties, accepted permissions and effects,
  the evidence needed to assess them, and observable pass, blocked, and failure conditions.

Trace dependencies through to their consumers. A tool's existence on the authoring machine does
not establish its availability to another project, and naming a dependency does not establish how
an Agent reaches it. Resolve each material route and its failure behavior before handing off work
that relies on it.

### Choose targets for differences that matter

Supply the smallest nonempty portfolio of representative targets that covers every materially
distinct applicability, dependency, permission, execution, observation, recovery, and exit seam.
A seam is a difference that could change whether or how the artifact works. Different project
names or directory layouts alone do not establish one.

For example, two projects that expose the same supported check interface may cover the same case.
A project where that required capability is unavailable exercises a different boundary if the
artifact claims to cover it: the Agent must recognize the limitation and take the prescribed exit.
A second successful project cannot establish that behavior. Choose cases for such differences;
a target is redundant when removing it leaves every material seam covered.

For each seam, establish the relevant target facts, consumed obligations and dependencies,
permissions, critical success and terminal paths, recovery and mid-path stops, expected observations,
and evidence characteristics. Require the public Correctness perspective to cover both:

- **Portable semantic authority:** shared ownership, applicability, qualified evidence, complete
  dependency routes, and absence of operative assumptions that hold only in the source project.
- **Representative behavior:** every material seam, critical path, and exit.

Specify what the evidence must establish. Leave commands, Reviewer identities, case selection,
validation selection, optional Runner use, and judgments to the public workflow. A representative
target is a coverage commitment, not by itself a demand to execute it. Close applicable validation
and representative runtime inputs when needed, and require the eventual closure evidence to identify
the final Candidate fingerprint.

### Keep target access separate from Candidate edits

Provide accepted permissions and effects for the public Author brief and the public job's separate
freeze. Candidate mutation is limited to its exact resources; retain both endpoints of any requested
move for that write-scope freeze. This Skill supplies the qualified input, while the public workflow
freezes authority under its own contract.

Each representative-target read or execution effect needs separate, exact authorization. Keep those
effects disjoint from Candidate resources: target authorization grants no Candidate mutation, and
Candidate mutation authority grants no target access or effects. Resolve applicable runtime bounds
through the public workflow rather than inventing private grant classes or a second execution
protocol.

### Hand off a closed input

The input is ready when every material fact, route, permission, pass condition, and completion
obligation has one supported answer and the intended work fits those permissions. Keep it in Agent
context. If a material answer is missing, return the public `NEEDS_INPUT` result before invocation,
identifying what remains unresolved.

Pass that closed input unchanged to the public workflow and await its result. Use its mechanisms
for writing, review topology and identities, validation, optional Runner evidence, and judgment
without adapting or recreating them here.

When rewriting this Skill itself, the pre-Author public and private contracts govern the whole run.
The edited text takes effect only in a later invocation.

## 3. Close the portable handoff

Check what the public workflow actually returned against what the shared artifact had to establish.
Maintain a transient closure account in Agent context covering every accepted meaning, evidence
source, dependency, representative seam, validation duty, and completion obligation.

Close an obligation only from observable public outputs bound to the current Candidate fingerprint:

- the Author's semantic change summary;
- the selected review topology and each professional perspective's final result;
- automated validation results and Runner evidence when present;
- remaining risks, final fingerprint, and terminal result.

One output can close a set of obligations when it explicitly covers that whole set. Hidden Reviewer
reasoning, presumed evidence selection, and a manufactured trail cannot supply missing evidence.
The account records control and handoff facts; it is not Candidate content, semantic authority, an
additional review, or a new public result.

**Portable success requires both public `COMPLETE` and closure of every obligation on its final
Candidate fingerprint.** A public `COMPLETE` without the necessary portability evidence remains the
public result, but does not establish portable success. Keep the unsupported obligations open and
report exactly which fingerprint-bound outputs are missing.

Preserve the public handoff and its `COMPLETE`, `NEEDS_INPUT`, or `BLOCKED` result. Append an exhaustive
account naming each obligation and the observable output that closes its pass condition, or the gap
that keeps it open. Include representative-target evidence only when a public output exposes it and
the pass condition needs it.

Keep this account transient. Create no private Candidate copy, workflow report, or permanent fixture.
This Skill grants no publication, installation, commit, push, release, or other downstream effect.
