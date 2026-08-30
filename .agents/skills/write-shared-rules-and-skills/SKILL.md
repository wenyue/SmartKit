---
name: write-shared-rules-and-skills
description: Author or revise a portable cross-project SmartKit Rule or Skill; excludes project-local artifacts and Setup Authoring Contracts.
---

# Write Shared Rules and Skills

Author one portable cross-project SmartKit Rule or Skill through the public
[`write-rules-and-skills`](../../../skills/write-rules-and-skills/SKILL.md) workflow. This Skill is
a private Adapter: it qualifies the shared request, compiles a closed Shared Input, supplies that
input unchanged at the public workflow entry, and projects the public handoff into portable
success. Read [`references/portability.md`](references/portability.md) completely before qualifying
the request.

## 1. Qualify the shared request

Perform the private qualification read-only. Resolve ownership first and apply every resolved-owner
route defined by the private model before collecting other Shared Input facts. Continue only for
one cross-project SmartKit Rule or Skill.

Establish every Shared Input field required by the private portability model. Candidate content,
source-project visibility or success, host injection, and available tools contribute no portable
authority. Portable meaning requires an independently supported owner and provenance.

When any material owner, meaning, dependency, permission, representative-target fact, validation
duty, pass condition, or completion obligation is unresolved, stop before public invocation and
return the public `ALIGNMENT_REQUIRED` payload: each missing choice, its evidence, its decision
owner, and its material consequences.

**Complete when:** one supported shared owner is qualified and every material fact or choice needed
to compile Shared Input has one accepted answer.

## 2. Compile Shared Input

Compile the accepted portable outcome and dispositions, ownership, Candidate resources and public
routes, qualified evidence, complete dependency closure, validation duties, exact operation
grants, portability completion obligations, and the smallest nonempty representative-target
portfolio that covers every materially distinct seam. Assign every stable portability ID defined
by the private model.

Representative-target resources are evidence or Acceptance inputs, never Candidate write targets.
Record evidence and proof characteristics; leave evidence selection and proof execution to the
public workflow. Close Shared Input before invoking that workflow.

**Complete when:** Shared Input is internally consistent, every dependency has a supported route,
every seam is covered by a representative target, and every portability pass condition names the
evidence characteristics capable of closing it.

## 3. Run the public workflow unchanged

Start at the public workflow entry and follow it unchanged. Supply the closed Shared Input unchanged
as ordinary accepted task/spec input governing meaning, evidence qualifications, dependencies,
validation duties, permissions, and completion inputs.

The public workflow alone owns its Candidate model and design, authoritative freeze, roles,
evidence selection, stage applicability, Quality, Machine, Correctness, Acceptance, correction,
replay, exits, and finalization. Its `CONTEXT_REQUIRED` and `ACCESS_REQUIRED` outcomes remain
bounded fallbacks for facts or access that could not be obtained through its authorized runtime.
This Adapter adds no role, stage, semantic channel, finding lifecycle, or proof authority.

**Complete when:** the public workflow returns its handoff or a terminal result. Preserve every
public terminal result unchanged.

## 4. Project portable success

Use the transient Portability Coverage Ledger defined by the private model to map every portability
ID defined there to current, public-workflow-selected closure evidence bound to the final Candidate
fingerprint.

Report portable success only when the public workflow reports success and every ledger item has
current closure at that fingerprint. Otherwise preserve the public result and report the uncovered
portability items without reinterpreting its verdicts.

On portable success, project the exhaustive per-ID closure account required by the private model
into the preserved public handoff while retaining its operation and audit records unchanged.

Keep Shared Input and the ledger in Agent context. Create no Candidate copy, workflow report, or
permanent fixture. The job grants no publication, installation, commit, push, release, translation,
or other downstream effect.

**Complete when:** the public handoff is preserved, every portability item is accounted for, and
success—when reported—is supported by public success plus complete final-fingerprint ledger
closure.
