---
name: write-shared-rules-and-skills
description: Author or revise one portable cross-project SmartKit Rule or Skill.
---

# Write Shared Rules and Skills

Qualify one artifact for use across its supported projects, delegate writing and review to [Write Rules and Skills](../../../skills/write-rules-and-skills/SKILL.md), and verify that the returned evidence closes its portability obligations.

The central judgment is which meaning belongs to the shared artifact and which facts belong to a target project. The public workflow owns authoring and review mechanics.

## 1. Establish what can travel

Continue with exactly one portable cross-project SmartKit Rule or Skill whose shared owner and independent provenance are supported. Establish who owns its meaning and which environments it claims to support before treating local guidance as shared policy or method.

Resolve other requests before public invocation:

| Request | Route |
| --- | --- |
| Project-local artifact, Setup Authoring Blueprint, or another resolved nonshared request | Use its supported owner. |
| Both a Rule and a Skill are needed | Return separate Rule and Skill requests for `split`. |
| `environment-owned` | Name the active owner and return no Candidate. |
| Ambiguous, incompatible, or unresolved ownership | Return public `NEEDS_INPUT` with the missing choice, evidence, decision owner, and material consequence. |

For each relied-on fact, establish owner, provenance, applicability, and limits. Admit it as portable meaning only when its cross-project owner and independent provenance support that use. Existing Candidate text is a claim to examine, not proof of its own authority.

For example, a shared requirement to run each project's required checks can travel; a source project's successful `npm test` run supports that target's command, not a command for every project. Keep the accepted requirement portable and the command with the target whose evidence establishes it.

Apply the same distinction to source-project policy, layout, packaging and discovery, host injection, available tools, and another Agent's reports. They can locate or support evidence without independently establishing portable meaning. Project and host instructions constrain the current work within their own scope; they add neither portable meaning nor Candidate permission.

## 2. Close the public authoring input

Give the public workflow one consistent input containing the knowledge needed to write and assess this artifact. Name obligations consistently enough to trace them through review and handoff, without imposing IDs or a record schema.

### Establish meaning, support, and dependencies

Make the accepted outcome, non-goals, safety boundaries, exits, and handoff explicit. Account for every inherited and new obligation as preserved, changed, added, moved, or retired. Give the Author this intended meaning rather than an old outline.

Qualify the supporting contract:

| Concern | What the public input must establish |
| --- | --- |
| Candidate and routes | Shared owner, applicability, provenance, exact resources and presence expectations, and intended public loading, discovery, distribution, and Skill-interface routes. |
| Evidence | Each source and discovery route, supported facts, represented scope, and source-project-specific limits. |
| Dependencies | Every direct and transitive Rule, Skill, tool, schema, environment capability, and host behavior: its owner, required behavior, consumers, supported shared- or target-owned route, and observable available, unavailable, and failed-use outcomes. |
| Acceptance | Validation and completion duties, accepted permissions and effects, required evidence, and observable pass, blocked, and failure conditions. |

Trace dependencies through to their consumers. Existence on the authoring machine proves neither target availability nor how a consumer reaches the dependency. Resolve material routes and failure behavior before handing off dependent work.

### Cover differences that can change behavior

Choose the smallest nonempty portfolio of representative targets covering every materially distinct applicability, dependency, permission, execution, observation, recovery, and exit seam. A seam is a difference that could change whether or how the artifact works; different project names or layouts alone do not establish one.

Two projects with the same supported check interface may exercise one case. If the artifact covers an unavailable required capability, that boundary needs evidence that the Agent recognizes it and takes the prescribed exit; another successful project does not cover it. Remove a target when all material seams remain covered without it.

For each seam, establish relevant target facts, consumed obligations and dependencies, permissions, critical success and terminal paths, recovery and mid-path stops, expected observations, and evidence characteristics. Require public Correctness to assess both portable semantic authority and representative behavior:

- **Portable semantic authority:** shared ownership, applicability, qualified evidence, complete dependency routes, and absence of operative source-project-only assumptions.
- **Representative behavior:** every material seam, critical path, and exit.

Specify what evidence must establish while leaving commands, Reviewer identities, case and validation selection, optional Runner use, and judgments to the public workflow. A representative target commits to coverage without automatically requiring execution. Close applicable validation and representative runtime inputs when needed; require closure evidence to name the final Candidate fingerprint.

### Separate target access from Candidate writes

Supply accepted permissions and effects for the public Author brief and separate freeze. Candidate writes cover exact resources only; include both endpoints of requested moves. This Skill qualifies input, while the public workflow freezes authority.

Authorize each representative-target read or execution effect separately and exactly. Keep those effects disjoint from Candidate resources: neither target authority nor Candidate authority grants the other. Resolve runtime bounds through the public workflow instead of inventing private grant classes or an execution protocol.

### Hand off only when the input is closed

The input is ready when every material fact, route, permission, pass condition, and completion obligation has one supported answer and the intended work fits the permissions. Keep it in Agent context. For a material unresolved answer, return public `NEEDS_INPUT` with the gap before invocation.

Pass the closed input unchanged and await the public workflow's result. Use its writing, review topology and identities, validation, optional Runner evidence, and judgment mechanisms without adapting or recreating them.

When rewriting this Skill, the complete pre-Author public and private contracts govern the run. Edited instructions take effect only in a later invocation.

## 3. Close portability against the returned evidence

Compare the public result with every accepted meaning, evidence source, dependency, representative seam, validation duty, and completion obligation. Keep this closure account transient in Agent context.

Close obligations only from observable public outputs bound to the current Candidate fingerprint:

- the Author's semantic change summary;
- chosen review topology and every professional perspective's final result;
- automated checks and any Runner evidence;
- remaining risks, final fingerprint, and terminal result.

An output may close several obligations when it explicitly covers the whole set. Hidden Reviewer reasoning, presumed evidence choices, and manufactured trails cannot fill gaps. The account records control and handoff facts; it is neither Candidate content, semantic authority, an additional review, nor a new public result.

**Portable success requires public `COMPLETE` and closure of every obligation on that final fingerprint.** A public `COMPLETE` lacking portability evidence remains the public result but does not establish portable success. Keep those obligations open and identify the missing fingerprint-bound outputs.

Preserve the public handoff and its `COMPLETE`, `NEEDS_INPUT`, or `BLOCKED` result. Append an exhaustive account of each obligation and the observable output closing its pass condition, or the remaining gap. Include representative-target evidence only when public output exposes it and the pass condition needs it.

Keep this account transient: create no private Candidate copy, workflow report, or permanent fixture. This Skill grants no publication, installation, commit, push, release, or other downstream effect.
