# Shared Judgment Basis

An artifact is one Rule or Skill; the Candidate is that current artifact and its scoped supporting
resources under authoring and review. Controller, Author, and Quality apply these judgments to
both artifact types within their own responsibilities: alignment, allocation, and the Author brief;
authoring; and quality review. Their role contracts retain authority over actions and verdicts.

## Operative meaning

Authoritative accepted requirements establish the artifact's intended meaning; existing Candidate
text is regression evidence. The artifact's governing instructions express the final requirements,
preserving their meaning, conditions, exceptions, and non-goals. Retain intermediate reasoning
or unchosen authoring options only when they materially help the reader understand or execute the
accepted requirements, distilled into useful rationale, a boundary, or an exception. Conversation
history remains evidence for authoring and review; its
presence there does not earn it a place in the artifact. This governs the artifact's own
instructions, including instructions for producing outputs that compare alternatives.

Organize around meaningful decisions, co-locating each requirement with the evidence, action, and
verification needed to apply it within the appropriate loading boundary. Fix sequence where outcomes depend on it; otherwise leave method
to the Agent. Disclose real branches through precise pointers, not arbitrary length thresholds.
Judge coherence and completeness without requiring headings, checklists, word budgets, or a second
workflow that repeats the policy.

A negative boundary is justified only as a necessary hard guardrail when positive wording cannot
reliably prevent material confusion, misapplication, or a safety risk.

## Responsibility and loading

Installed SmartKit core governance owns applicability, strength, precedence, and composition for
Rules, rule-led Skills, and task Skills. Rely on that owner rather than restating or redefining its
comparisons. Make intentional task alternatives and project delegation explicit where they affect
a supported decision, including the relevant conditions, intended departure or delegated outcome,
and remaining constraints.

A Rule owns a clearly bounded area of persistent policy across relevant work. A task Skill owns a
triggered job with a bounded outcome and the constraints necessary to that job; a rule-led Skill
owns policy applied to existing work. Rule-led Skills are Rules exposed through native Skill
discovery, not task workflows competing for a separate deliverable. Allocate shared persistent
policy to the best existing policy owner by meaning, whether a Rule file or a rule-led
Skill, improving that owner when needed.
Always-loaded status is evidence of availability, not a reason to promote project- or Skill-specific
obligations to global policy. If code, configuration, a schema, or another active owner already owns
a fact, its change belongs there.

Give each policy one complete definition across the relevant Rules and Skills. Match references to
their supported routes: Rule files may reference Rules and Skills; Skills may invoke or reference
other Skills, including rule-led Skills, but must not directly reference independently loaded Rule
files. Use short owner pointers within these boundaries and local context needed for a decision,
keeping the policy definition with its owner. Consolidating ownership preserves useful conditional
loading boundaries inside that owner; one public Skill need not have one monolithic entry. A Skill
route can load a rule-led policy; it does not change that policy's conditions or exceptions.

Assess suitable existing owners using related Rules and Skills, applicable always-loaded project
Rules and SmartKit global Rules, and conditional Rules that can load together in supported usage.
Establish their meaning, triggers, and canonical sources through the environment's supported
discovery and loading routes. The current authoring session alone does not establish availability
to future users.

Compare meaning, including conditions, exceptions, and configuration, rather than matching phrases.
For independently loaded Rule files, a Skill cannot establish applicability or activation. It may
rely on their specific constraints only with supported independent loading guarantees wherever it
supports that behavior, retaining only the local context needed for its decision. Preserve the
policy's conditions and exceptions under either loading route. Removing a Skill obligation
requires resolved allocation and loading; a pointer alone does not establish applicability or
availability.

An editable installation cache or a duplicate in the Skill cannot substitute for the canonical
owner. Missing source, access, or permission leaves an owner dependency to resolve through the
responsible role.

## Artifact forms

Choose the form that fits the allocated work. Apply the common judgments above to every form and
the relevant criteria below when selecting, writing, or evaluating its shape.

### Rules

For a Rule, lead with the governing policy.

A Rule's owner, strength, observable conditions and outcomes, exceptions, and precedence must be
reconstructable.

### Skills

For a Skill, apply `SKILL-MECHANICS.md` to invocation and packaging. A description should supply
only what is needed to choose the Skill from its name and the task and context normally visible
before loading; body instructions cannot repair a missed entrance. For model discovery, minimize
fixed context cost while preserving reliable choice; user-invoked descriptions support human
selection. Check representative intended uses, nearby nonmatches, and easily missed necessary uses.
Static traces suffice for this judgment, without measuring loading accuracy.

Choose the shape that fits the work from three parallel writing styles:

- A **principle-led Skill** states the outcome, governing principles, consequential constraints,
	and completion conditions while leaving method to the Agent.
- A **procedure-led Skill** fixes steps and order where sequence or protocol affects the result,
	correctness, safety, ownership, coordination, recovery, or external effects.
- A **rule-led Skill** governs relevant work with requirements and exceptions.

Principle-led and procedure-led task Skills are reached for a concrete job. Prioritize accurate
task matching, complete needed context, and coherent execution. Keep universally needed methods
or steps accessible together when that best serves the task; splitting mandatory method solely to
shorten the entry adds indirection without avoiding needed context. General economy, relevance,
and reliable progressive disclosure still apply.

A **Hybrid Skill** combines these styles where their roles are consequential. Apply policy-loading
and task-execution considerations to the respective parts, rather than one whole-artifact size
target. Integrate their meaning around decisions rather than concatenating a rule narrative and a
workflow.

### Rule-led Skills

Reserve `rule-<domain>` names for this writing style, independently of strength. These Skills are
conditionally loaded Rules for broad relevant work. Use a model-facing description that triggers
on relevance to the governed domain before governed decisions, rather than restricting discovery
to a list of coding actions or policy topics. Declare default Strength in the entry and keep
behavior-changing conditions beside the requirements they govern. Keep explicit invocation and
supported dedicated assessment discoverable.

Normal activation constrains the current work rather than starting another audit or report. A
requested assessment has its own stated coverage and outcome, subject to the policy's conditions
and the request's authority. Neither route grants additional permission.

Low first-activation token cost is an authoring and acceptance requirement for these broadly
triggered policy Skills, subject to complete obligations, correct decisions, and reliable loading.
Distinguish the costs that matter to their design:

- **Discovery:** the description and other always-present pointers. Economize wording while
  preserving broad domain reach.
- **First activation:** the entry and all required reads reached unconditionally, including
  transitive dependencies. Branch-only instructions still cost upfront when they are in the entry;
  an unconditional resource chain merely relocates that cost.
- **Later branches:** additional content reached only when its condition holds, before dependent
  decisions or actions.

Keep fundamental policy, Strength, and decision-sufficient evidence, conditions, and exceptions
in the entry. It should support ordinary substantive work, including simple, clear
modifications and routine review, through the resulting action and completion judgment. An entry
that supports only abstention, unchanged propagation, or routing has not met this requirement.
Co-locate the common policy and context needed to apply it; keep content needed across all or
nearly all supported work inline, or reconsider the loading boundary that makes it unavoidable.

Defer content to an owned resource when a branch needs additional knowledge or constraints to make
its decision correctly. Writing, reviewing, diagnosis, or assessment alone does not establish that
need. Name the facts that distinguish the branch, recognizable before reading the resource,
rather than relying on subjective complexity or a general instruction to read it when needed.
Each precise pointer names what to read and when, reaching every obligation before the dependent
decision or action, including review judgments. Establish availability through supported routes.
Loading grants no additional permission.

For authoring and acceptance, trace representative ordinary substantive work and deeper paths
through the actual reachable files and transitive resource chains. Check what each decision needs
and whether the entry lets ordinary modifications and routine review finish without unnecessary
reads, while deeper branches reach their complete obligations in time. A nominally conditional
chain that ordinary work must effectively always traverse defeats low first-activation cost.
In a revision or ownership merge, preserve required meaning and use prior loading boundaries as
regression evidence so consolidation does not silently make conditional methods unconditional.
Judge clarity, completeness, and the whole reading path without arbitrary token or line budgets,
quotas, mechanical scoring, or forced fragmentation. Static source traces suffice without empirical
task-frequency claims, a separate report, or runtime experiments.

Use core governance's inheritance for owned normative resources; distinguish them from illustrative
material and independently owned policies, which retain their own contracts. Native Skill discovery
and public exposure retain their existing owners; writing a rule-led entry neither registers it nor migrates another policy into it.
