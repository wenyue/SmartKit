# Shared Judgment Basis

An artifact is one Rule or Skill; the Candidate is that current artifact and its scoped supporting
resources under authoring and review. Controller, Author, and Quality apply these judgments to
both artifact types within their own responsibilities: alignment and allocation, authoring, and
quality review. Their role contracts retain authority over actions and verdicts.

## Operative meaning

Authoritative accepted requirements establish the artifact's intended meaning; existing Candidate
text is regression evidence. The artifact's governing instructions express the final requirements,
preserving their meaning, scope, conditions, exceptions, and non-goals. Retain intermediate reasoning
or unchosen authoring options only when they materially help the reader understand or execute the
accepted requirements, distilled into useful rationale, a boundary, or an exception. Conversation
history remains evidence for authoring and review; its
presence there does not earn it a place in the artifact. This governs the artifact's own
instructions, including instructions for producing outputs that compare alternatives.

Apply the positive-target guidance from `writing-for-agents`: state the positive target by default.
Retain a negative boundary only as a necessary hard guardrail when positive wording cannot reliably
prevent material confusion, misapplication, or a safety risk. Pair that guardrail with the required
positive behavior. Preserve accepted constraints and
non-goals by expressing the intended scope and behavior positively wherever that is sufficient.

## Responsibility and loading

A Rule owns a clearly bounded area of persistent policy across triggered work; a Skill owns a
triggered job with a bounded outcome and the constraints necessary to that job. Allocate shared
persistent policy to the best existing Rule by meaning and scope, improving that Rule when needed.
Always-loaded status is evidence of availability, not a reason to promote project- or Skill-specific
obligations to global policy. If code, configuration, a schema, or another active owner already owns
a fact, its change belongs there.

Give each policy one complete definition across the relevant Rules and Skills. Rules may reference
other Rules and Skills; Skills may reference other Skills, but must not directly reference Rules.
Use short owner pointers within these reference boundaries and local context needed for a task
decision, keeping the policy definition with its owner.

Assess suitable existing owners using related Rules and Skills, applicable always-loaded project
Rules and SmartKit global Rules, and conditional Rules that can load together in supported usage.
Establish their meaning, scope, triggers, and canonical sources through the environment's supported
discovery and loading routes. The current authoring session alone does not establish availability
to future users.

Compare meaning, including conditions, exceptions, and configuration, rather than matching phrases.
A Skill cannot make a Rule applicable or activate it. It may rely on specific constraints of an
independently applicable Rule only with supported loading guarantees wherever the Skill supports
that behavior. Independent Rule loading supplies those constraints; the Skill retains only the
local context needed for its task decision. Preserve the Rule's scope, conditions, and exceptions
in that reliance. Removing a Skill obligation requires resolved allocation and loading; a pointer
alone does not establish applicability or availability.

Choose the best owner before checking whether it can be changed. Establish canonical-source access
and write authorization separately from readability, using working access as evidence rather than
inferring privilege requirements from location. An editable installation cache or a duplicate in
the Skill cannot substitute for the canonical owner. Missing source, access, or permission leaves
an owner dependency to resolve through the responsible role.
