# Generated authoring

Every full setup requests every current catalog contract, even when upstream fingerprints and
recorded outputs are unchanged. Complete this workflow before registering any request. Read the
current project evidence and generated content as authoring input; preserve qualified project intent
in the resulting set while applying the immutable upstream contracts.

## Plan the resulting set

Resolve every requested immutable Setup Authoring Contract from `source_root`. Load the public
writer at `source_root/skills/write-rules-and-skills/SKILL.md`, including its same-source references
and `writing-for-agents` dependency. An ambient or target-checkout writer is not this session's
authority. Apply that writer's **Allocate responsibility** criteria to establish one common plan
before any Rule authoring begins.

Plan the whole resulting project Rule set, including retained Rules outside the generation
requests. Derive its membership from the frozen requests, catalog, contracts, and complete current
project inputs; assume no fixed count. For each Rule, identify its responsibility, main content,
boundaries with neighboring owners, and necessary references. Include Skills wherever their
responsibilities affect this allocation. Supply applicable always-loaded project Rules and
SmartKit global Rules, plus evidence of conditional Rules that can load together in supported
usage. Establish this context through supported discovery and loading routes, not merely the
instructions visible in the current session.

The plan records ownership and loading evidence and unresolved owner dependencies. Setup owns
this batch plan and session coordination; the public writer owns each Rule or Skill's allocation
and single-definition judgment. The catalog, schema, contracts, and scripts retain their facts and
bounds. A plan cannot add a generation request, override a contract, or authorize another owner.

## Author and reconcile before registration

Invoke the pinned public writer in the target-repository context for each request, using its
Setup Authoring Contract as accepted task/spec input and `GENERATED` as the request root. Supply
the common plan, ownership and loading evidence, owner dependency state, and complete current
project content to every job, including Skill jobs. Each invocation owns exactly one Candidate
and its own frozen scope, evidence, validation, review, and result. Jobs may run sequentially.

Accept only a public-writer `COMPLETE` handoff whose exact Candidate paths already lie beneath
`GENERATED` and satisfy the request's contract. Preserve any contract-required evidence in that
handoff; a contract's readiness terminology does not replace the public writer's result. Setup
supplies no authority for downstream effects: obtain a separate grant before any such effect,
and apply the frozen-target drift rule if it changes setup-relevant target state.

Use discoveries from authoring to update the common plan. Before registration, review all
generated outputs together with the retained Rules and relevant Skill and global Rule context
against the plan and accepted contracts. Resolve coverage omissions, responsibility overlap, and
semantic duplication using the pinned writer's allocation criteria. Individual `COMPLETE`
handoffs do not establish whole-set coherence.

Route every necessary generated correction through a distinct valid invocation of the public
writer with the updated plan and a newly frozen single-Candidate scope. Reauthor affected earlier
outputs as well as later ones, obtaining fresh `COMPLETE` handoffs for every changed Candidate.
Repeat the whole-set check until all requested outputs and their current handoffs agree with the
resolved plan. Keep this reconciliation before registration; do not edit an accepted Candidate
behind its handoff or use registration to replace it.

If a required correction belongs outside the frozen generation requests, including a retained
project Rule or SmartKit global Rule, stop and cancel the session. Follow the public writer's
owner-dependency and user-assistance path to obtain the separately authorized canonical-owner
correction, then restart from the accepted state. Preserve the pinned source and installation
caches; neither is a substitute correction target. An ownership discovery never widens this
session or a writer job's frozen scope.

A writer `NEEDS_INPUT` or `BLOCKED`, or unavailable required authority, dependency, access, or role,
stops generation. Preserve and report its exact blocker and evidence, cancel through the
[session protocol](session-protocol.md#stop-and-recover), and begin a fresh session only after
resolution. Do not register partial work.

## Register the complete handoffs

Once whole-set review and every correction are complete, register each request once using its ID
and the exact paths from its current `COMPLETE` handoff:

```text
python "<skill-root>/scripts/workflow.py" register --session "<SESSION>" --request-id "<ID>" --output "<PATH>"
```

Repeat `--output` for supporting files in that handoff. Paths may be absolute beneath `GENERATED`
or target-relative beneath `.agents/`. The command validates and records one request's outputs;
it does not certify the writer's semantic handoff. Duplicate request registration is rejected
without replacing the earlier registration. Correct a registration input error and retry in the
same session only if that request remains unregistered and its claim was released. A claim cleanup
failure requires inspection of the reported session before retrying; target drift requires
cancellation and restart. If a semantic correction becomes necessary after registration begins,
cancel and restart rather than changing registered outputs. After all requests are registered,
continue to `finish`.
