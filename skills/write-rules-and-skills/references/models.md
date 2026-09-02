# Ownership, Alignment, and Candidate Models

This contract owns the entry gate and Candidate model.

## Route one owner

Determine ownership from the accepted concern, outcome, and governing evidence; packaging alone
does not establish it.

| Verdict | Meaning and route |
| --- | --- |
| Rule | One persistent policy constrains decisions across triggered work. Continue with the Rule model. |
| Skill | One triggered job produces a bounded outcome. Continue with the Skill model. |
| Split | Policy and job obligations have different owners. Return separate requests; one Candidate cannot span both. |
| Environment-owned | Code, configuration, schema, tool output, or another active owner already owns the fact. Name that owner and return no Candidate. |
| Ambiguous | Supported evidence permits incompatible owners or contradicts the requested artifact. Return ALIGNMENT_REQUIRED. |

Prefer a more-specific authoring owner when one exists. A completed handoff from that owner may be
accepted as input; this workflow does not silently absorb its work.

## Close alignment

Establish accepted values for the outcome, current and requested behavior, non-goals, exact
Candidate resources and loading route, distribution and exposure boundary, supported public,
project-local, or shared writer context, governing evidence, preservation and compatibility
constraints, dependencies, permissions, external effects, validation, safety, exits, and handoff.
Freeze read, write, create, delete, move, and network authority separately. Every accepted move
names its exact source and destination and is never inferred from create or delete authority.
Exact public paths and delivery constraints confer no downstream publication or installation
grant.

Evidence has authority only through its semantic owner and provenance. Prior Candidate text is
completeness and regression evidence, not design authority. Nonnormative context and ambient
repository visibility supply no operative meaning. The Author later selects preserve, change, add,
move, or retire for every inherited or new obligation.

Host and repository instructions govern execution of an already-authorized operation. Catalog and
environment metadata are inert. None supplies Candidate meaning, evidence authority, scope,
grants, permissions, role judgment, or workflow transitions. Independently owned Rules, accepted
Specs, implementations, tests, and external sources supply meaning only through their own authority
and provenance.

Resolve discoverable facts as Agent work. For every unresolved material choice, name the evidence,
decision owner, live options, and consequences. Return ALIGNMENT_REQUIRED when the decision is not
user-owned. When all unresolved choices are user-owned, use a proportionate available interaction
to close the complete decision tree; grilling is optional when useful. If every material branch
does not close, return ALIGNMENT_REQUIRED. Explicit confirmation ends this invocation with one
accepted alignment handoff for a new run; it does not authorize same-run authoring and is not an
immediate HUMAN_DECISION_REQUIRED shortcut.

Continue only when one exact Candidate surface can satisfy every accepted obligation within the
available authority.

## Rule model

A Rule owns one policy. Its Policy Frame contains only the fields that can change application:
owner, strength, scope, observable predicates and outcomes, exceptions, precedence, and boundaries.

Lead with the governing policy. Co-locate each predicate with its outcome and exception. State
supported overrides and reject the nearest material false positive and false negative. Route
ordered execution to a Skill and leave discoverable environment facts with their owner.

Correctness must be able to reconstruct the complete Policy Frame and trace every operative
commitment to accepted evidence. Acceptance is conditional: use it only when scenario or real
execution uncertainty is material.

## Skill model

A Skill owns one triggered job. Its Job Frame states objective, actor, trigger, accepted evidence,
inputs, preconditions, outcome, ownership, boundaries, validation, exits, and handoff. State order,
resources, commands, recovery, or detailed branches only when their omission could change outcome
under the Frontier-Agent Principle.

Judgment-led is the default. Use a Procedural Island only where order or protocol changes
correctness, safety, ownership, coordination, recovery, external effects, executability, or
handoff. The resulting Skill is Hybrid when one or more such islands sit inside the Judgment Frame.

Apply writing-for-agents to loading and information hierarchy. Preserve the supported invocation
choice and interface metadata unless accepted evidence changes them:

- model-invoked: keep a model-facing description, omit disable-model-invocation, and omit
  policy.allow_implicit_invocation unless explicit autonomous routing is itself contractual;
- user-only: set disable-model-invocation to true and policy.allow_implicit_invocation to false.

Metadata outside the granted Candidate is a required preservation constraint, not an implied write
grant.

Correctness must be able to reconstruct the complete job, material branches, boundaries, and exits.
Acceptance is NOT_REQUIRED when semantics are high-confidence and no material scenario or runtime
uncertainty remains. It is never automatic merely because the Candidate is a Skill.
