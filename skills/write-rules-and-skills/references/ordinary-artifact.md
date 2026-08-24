# Ordinary Artifact

An Ordinary Artifact is a Rule or Skill used directly as policy or as a triggered job. This
reference owns its lifecycle classification, runtime boundary, and representative application.

## Honor the supplied owner boundary

| Caller scope | Contract |
| --- | --- |
| Project-local | Author project behavior from explicitly supplied repository facts and keep it in the narrowest project owner. |
| Shared | Keep only behavior supported by the explicitly supplied shared dependencies and portability evidence. |

Only the project-private shared workflow may claim Shared. Removing project details or invoking the
public workflow alone supplies no source-context or portability proof.

## Prove behavior-shaping need

When a proposed instruction exists only to change default Agent behavior and no observed failure
establishes that need, run one Soft-isolated Behavior Control before writing. Use the previously
accepted artifact for a rewrite or no candidate for a new artifact, and give a fresh Agent the same
task planned for candidate Acceptance. Preserve its raw returned result in controller context for
review.

Do not run a control for policy authority, project facts, reference material, or an already observed
failure. If the control already produces the required behavior, omit the no-op instruction unless
separate accepted evidence requires an explicit policy.

## Author the runtime artifact

- State the final policy or job, not the authoring history, semantic ledger, review process, or
  qualification evidence.
- Keep project facts in a Project-local artifact. In a Shared artifact, name only stable protocols
  and tell the Agent how to discover local facts or stop when discovery cannot resolve them.
- Keep each requirement in one owner. Follow more-specific Rules and supported local overrides
  without copying them into broader prose.
- Include only schema-required or behavior-changing instructions that cannot be derived from a
  reliably loaded owner.

## Accept representative use

The selected `rule-semantics.md` or `skill-semantics.md` supplies the type-specific cases. Apply the
common Acceptance Runner protocol selected by the parent Skill.

- For a Project-local artifact, explicitly supply the repository claims, owner boundary, real entry
  or enforcement point, and relevant local cases.
- For a Shared artifact, use the cases, dependencies, and portability evidence supplied by its
  owning workflow.

Acceptance passes only when the artifact keeps one meaning across its claimed scope, produces one
supported result for each selected case, and requires no invented project fact, action, or exit.
