---
name: write-shared-rules-and-skills
description: Author or revise a cross-project SmartKit Rule or Skill with portability evidence; excludes project-local artifacts and Setup Authoring Contracts.
---

# Write Shared Rules and Skills

Author one cross-project SmartKit Rule or Skill without importing source-project assumptions. This
project-private Skill owns shared dependency closure, source-context exclusion, representative
target evidence, and the Soft-Isolated Role Adapter. The public `write-rules-and-skills` Skill owns
the common Authoring Protocol and ordered evaluation stages.

## Establish shared readiness

Read [`references/portability.md`](references/portability.md) completely. Establish the accepted
shared meaning, canonical candidate paths, owned resources, declared shared dependencies, preserved
obligations, representative target contexts, and every portability-specific pass condition. Reject
a project-local owner or a Setup Authoring Contract before candidate writes.

Read the public [`role-launch.md`](../../../skills/write-rules-and-skills/references/role-launch.md)
completely, then read
[`references/soft-isolated-role-adapter.md`](references/soft-isolated-role-adapter.md)
completely. Supply that Adapter, the complete shared evidence, and portability pass conditions in
the frozen Run Contract. Do not expose the shared branch or its isolation policy through the public
Skill.

## Run the common protocol

Invoke `write-rules-and-skills` with the accepted shared input and the already selected Adapter,
applying its complete protocol unchanged.

Shared portability adds no Reviewer stage. Inject the portability reference's evidence, checks, and
pass conditions into the existing Semantic Fidelity and Ownership and Agent Executability and
Behavioral Closure role contracts. Inject any required representative execution cases into the
single conditional Acceptance stage. The generic public Reviewer scopes remain unchanged.

## Finish

Portability passes only when the current Candidate Version has a qualified Soft-Isolated Role
Adapter, complete declared dependency closure, both extended Correctness verdicts, and every
required representative Acceptance case. Add those facts to the public handoff.
