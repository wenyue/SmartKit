# Ownership, Alignment, and Candidate Models

While this gate is open, permit only `Close alignment`'s conditional `grilling` invocation and the
read-only Agent fact discovery it requires, including fact-finding dispatch, as alignment-owned
operations. Begin no Candidate mutation, lock, validation stage, Author/Reviewer/Runner role, or
other downstream authoring or proof effect until alignment and modeling close.

## Route one owner

Discover ownership from the concern, capability, artifact, and governing evidence. Packaging does
not confer semantic ownership. When a more-specific authoring owner applies, route the request
there unless its completed handoff is present.

Classify every accepted obligation:

| Verdict | Meaning and route |
| --- | --- |
| `rule` | Persistent policy constraining decisions across triggered jobs; continue with one supported Rule owner. |
| `skill` | Triggered work producing one bounded outcome; continue with one supported Skill owner. |
| `split` | Independently owned policy and job obligations; return separate Rule and Skill requests. No Candidate Version spans both. |
| `environment-owned` | A reliable fact belongs to code, configuration, schema, tool output, or another active owner; name that owner and return no Candidate. |
| `ambiguous` | Evidence supports incompatible owners or conflicts with the requested artifact; return `ALIGNMENT_REQUIRED`. |

For an ownership conflict, report the governing evidence, loading and behavioral effects,
supported retain/move/split outcomes, live choice, and decision owner. A human preference cannot
turn policy into a triggered job or waive the supported model and proof contract.

An explicitly read-only Ownership Review reports each artifact's current and supported owner,
obligation classifications, evidence, effects, recommendation, and missing decision. Return `PASS`
when aligned; otherwise return `ALIGNMENT_REQUIRED`. Confirm that no file changed and stop before
loading or completing a Candidate model.

## Close alignment

Establish one accepted value for:

- outcome, current and preserved behavior, changes, non-goals, safety, and prioritized exits;
- owner, exact Candidate resources, loading route, distribution boundary, and every obligation's
  `preserve`, `change`, `add`, `move`, or `retire` disposition;
- dependencies, permissions, external effects, validation duties, applicable operating contexts,
  and final handoff; and
- separate `read`, `write`, `create`, and `delete` authority.

Align evidence-complete requirements directly. An accepted Issue or Spec may supply these values;
a uniquely supported local repair may close them. Resolve discoverable facts as Agent work, then
establish the complete set of material answers still open and each answer's decision owner. An empty
set closes alignment without `grilling` or `ALIGNMENT_REQUIRED`. If a nonempty set contains any
non-user-owned decision, return `ALIGNMENT_REQUIRED` with each unresolved choice, its evidence,
decision owner, and material consequences, without invoking `grilling`. If every decision in the
nonempty set is user-owned, require exactly one model-invoked `grilling` session over the complete
unresolved design tree. If the Skill is unavailable or the session cannot close every remaining
material branch and obtain explicit user confirmation, return `ALIGNMENT_REQUIRED` with the same
payload. On explicit confirmation of the complete shared understanding, end the current run with
exactly one handoff: that understanding becomes accepted human-decision context for a new authoring
run. Every operative term and meaning requires independent accepted support; an ambient or
nonnormative glossary is never authority.

Select exactly one Candidate model below.

## Rule model

A Rule owns one persistent policy. Resolve its **Policy Frame**: class, owner, strength, scope and
applicability, observable predicate-to-outcome mappings, exceptions, precedence, and boundaries.
Give every applicable field one supported value; omit one only when evidence proves it cannot
affect policy.

- Lead with the governing policy and co-locate each predicate, outcome, and exception.
- Keep each requirement in its narrowest owner and state supported overrides explicitly.
- Use observable predicates and outcomes. For every threshold, overlap, exception, and exclusion,
  reject the nearest false positive and false negative.
- Route ordered execution to a Skill. Leave discoverable facts in their environment owner and
  history in documentation unless it changes application.
- Use headings for stable policy regions or real branches, lists for peers, and tables for exact
  repeated mappings.

Correctness reconstructs the complete Policy Frame. It fails implicit or conflicting fields,
invented predicates, unsupported inapplicability, duplicate ownership, unstated overrides, ambient
dependencies, and missing outcomes. When Acceptance applies, it exercises the real policy seam and
observes a decision or action.

## Skill model

A Skill owns one complete triggered job. Resolve objective, actor, trigger, evidence, inputs,
preconditions, outcome, owner, boundaries, completion, blocked, failure, validation, and handoff.
Resolve order, recovery, resources, and commands only when they can alter execution. Choose one
evidenced shape:

- **Judgment-led** by default: a Judgment Frame supplies evidence, principles, invariants,
  decision boundaries, and prioritized exits while leaving method to capable judgment.
- **Procedure-led** when order changes correctness, safety, protocol compliance, coordination,
  recovery, or outcome: one canonical Job Graph owns every path.
- **Hybrid** when a Judgment Frame contains bounded Procedural Islands that return to judgment.

Historical sequence and apparent completeness do not justify procedure. Project the whole job
from entry, place branches beside their triggers, order only consequential actions, and give every
path observable completion, blocked, failure, and stop outcomes. Completion includes validation,
cleanup, preservation, and handoff. Claim only supported recovery.

Use a script only for repeated, fragile, deterministic work with explicit dependencies, inputs,
outputs, failures, recovery, and safe representative tests. Apply `writing-for-agents` to
information architecture and invocation. Preserve the supported invocation choice unless accepted
evidence changes it, and align metadata in one Candidate Version:

- **model-invoked:** omit `disable-model-invocation` from `SKILL.md` and omit
  `policy.allow_implicit_invocation` from `agents/openai.yaml`;
- **user-only:** set `disable-model-invocation: true` and
  `policy.allow_implicit_invocation: false`.

When autonomous routing is itself contractual, preserve an accepted explicit
`policy.allow_implicit_invocation: true`; it is not equivalent to omission. Preserve supported
interface metadata and create `agents/openai.yaml` when absent.

Correctness reconstructs the complete job, shape, boundaries, branches, and exits. Full-job
execution is normal Skill Acceptance. A **Finite Execution Projection** is eligible only when full
execution would re-enter this Acceptance graph or require identity control forbidden to a Runner;
Design must record eligibility and preauthorize the harness.
