# Generated Authoring

Use this for every full setup, before any request is registered. Every current catalog blueprint is
requested even when upstream fingerprints and recorded outputs are unchanged. Setup must establish
that the resulting project set works together; individual writing results do not establish that
property.

## Establish the pinned inputs and responsibilities

Resolve each requested immutable Setup Authoring Blueprint from the session's `source_root`. Load
the public writer at `source_root/skills/write-rules-and-skills/SKILL.md`, keeping all required
same-source references and its `writing-for-agents` dependency pinned to that source. An ambient or
target-checkout writer is not this session's authority.

Setup owns the whole-set responsibility and loading plan. The public writer owns one Candidate's
writing, scoped design, validation, review and result. Blueprints supply required target meaning;
catalog, schema and scripts own their factual bounds and mechanics. Planning cannot add a generation
request, override a blueprint or authorize another owner's changes.

Read complete current project inputs and existing generated content as evidence. Preserve qualified
project intent while applying immutable blueprints. Derive the resulting membership from frozen
requests, catalog and blueprints, including retained project Rules outside the requests. Include
related Skills wherever their responsibilities affect the set; assume no fixed artifact count.

## Plan coverage and loading across the set

Before any Rule authoring, establish which owner carries each required responsibility and how a
reader will reach it. For each Rule, identify its purpose, main content, neighboring boundaries and
necessary references. Bring relevant Skills into the same plan so a Rule does not redefine a
procedure or fact owned elsewhere.

Account for applicable always-loaded project Rules and SmartKit global Rules, together with
rule-led Skills that can load in supported usage. Establish those routes through supported discovery
and loading evidence. Instructions visible in the current conversation alone do not prove that a
future reader receives them.

Use the following distinctions to resolve allocation:

- **Coverage:** every required obligation needs a responsible artifact or an established external
  owner reachable when needed. Preserve its conditions and exceptions; a reference that loads too
  late does not cover the decision.
- **Responsibility:** keep policy, task procedures and project facts with their canonical owners.
  Generated and retained artifacts must agree about where one responsibility ends and another
  begins. A blueprint requirement cannot be reassigned or omitted merely to simplify the set.
- **Overlap:** distinguish useful context from duplicate operative definitions. Two artifacts can
  discuss one subject for different reader decisions; trouble arises when they independently
  prescribe the same meaning or give incompatible directions. Resolve the owner and supported
  reference, retaining the meaning needed by each reader.
- **Loading:** unconditional baseline policy belongs in the supported direct Rule route; conditional
  policy needs a discoverable rule-led Skill with sufficient entry information and timely pointers.
  Check the actual combined loading case, not just each file in isolation.

Record the resolved responsibilities, ownership/loading evidence and unresolved owner dependencies
in the common plan. This is Setup's qualification of the set, not a document template. Leave each
writer room to organize and express its Candidate within that plan and blueprint. A discovery that
changes neighboring responsibilities comes back to Setup for reconciliation; it does not widen the
writer's frozen scope.

## Obtain complete single-Candidate handoffs

Invoke the pinned public writer in the target-repository context for each request. Supply its Setup
Authoring Blueprint as accepted task/spec input and `GENERATED` as the request root. Every job,
including a Skill job, receives the common plan, ownership and loading evidence, owner-dependency
state and complete current project content. Each invocation owns exactly one Candidate with its own
frozen scope, evidence, validation, review and result. Jobs may run sequentially.

Consume only a public-writer `COMPLETE` whose exact Candidate paths already lie beneath `GENERATED`
and satisfy that request's blueprint. Retain blueprint-required evidence in the handoff. A blueprint's
readiness terminology does not replace the public writer's result.

Authoring supplies no authority for downstream effects. Obtain a separate grant before such an
effect, and apply the frozen-target drift rule if it changes setup-relevant target state. A writer
`NEEDS_INPUT` or `BLOCKED`, or missing required authority, dependency, access or role, stops generation.
Preserve the precise blocker and evidence, cancel under [Stop and Recover](session-protocol.md#stop-and-recover),
and start a fresh session only after resolution. Do not register partial work.

## Reconcile the whole result before registration

Use authoring discoveries to update the common plan. Review all generated outputs together with
retained Rules and the relevant Skill/global Rule context against the plan and accepted blueprints.
Apply Setup's coverage, responsibility, overlap and loading decisions above to the actual combined
result. An individual `COMPLETE` establishes its Candidate, not whole-set coherence.

Route every needed generated correction through a distinct valid public-writer invocation with the
updated plan and a newly frozen single-Candidate scope. Correct affected earlier outputs as well as
later ones, obtaining a fresh `COMPLETE` for every changed Candidate. Repeat the whole-set check until
all requested outputs and current handoffs agree with the resolved plan. Do not edit an accepted
Candidate behind its handoff or use registration to replace it.

A required correction outside frozen generation requests, including a retained project Rule or
SmartKit global Rule, stops this session. Cancel it, preserve the owner dependency and use the
public writer's owner-dependency/user-assistance route to obtain the separately authorized canonical
correction. Restart from the resulting accepted state. Neither the pinned source nor installation
caches are substitute correction targets; a discovery cannot widen this session or a writer job.

## Register only the final handoffs

After whole-set reconciliation and all corrections, register each request once with its ID and the
exact paths from its current `COMPLETE` handoff:

```text
python "<skill-root>/scripts/workflow.py" register --session "<SESSION>" --request-id "<ID>" --output "<PATH>"
```

Repeat `--output` for supporting files in that handoff. Paths can be absolute beneath `GENERATED` or
target-relative beneath `.agents/`. Registration validates and records one request's outputs; it
does not certify the writer's semantic handoff. Duplicate registration is rejected without replacing
the earlier record.

A registration-input error may be corrected and retried in the same session only while that request
remains unregistered and its claim was released. Inspect the reported session after a claim-cleanup
failure before any retry. Target drift requires cancellation and restart. If a semantic correction
is discovered after registration begins, cancel and restart rather than changing registered outputs.
Once all requests are registered, continue to `finish`.
