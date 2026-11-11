# Constraints

## Purpose and evidence

For an independent request to create or revise `.agents/rules/constraints.md`, use `write-rules-and-skills` to produce one target-owned Rule titled `Constraints`. Give an Agent the project-specific constraints, exceptions, and entry conditions needed before choosing an implementation or running a tool. Installed shared policy and existing project owners retain their meaning; this Rule supplies the project's additional decisions.

Establish the target from the accepted request. Inspect its entry guidance, existing Rules and relevant Skills, accepted Issues and ADRs, schemas and interfaces, configuration, generators, preparation and verification owners, and representative implementation and tests. Qualify evidence by owner and provenance. Existing instructions reveal project intent and regression risks; current code alone cannot authorize changing that intent. An existing Wiki can locate sources and explain relationships, but consequential claims require checking their canonical owners. Authoring remains usable without a Wiki.

When consolidating earlier Rules, read their complete content, including current project additions and exceptions, and the existing destination. Account for each consequential obligation as retained here, already owned elsewhere with a usable loading route, deliberately changed or retired under accepted intent, or unresolved. Resolve unsupported dispositions before writing; a shorter result does not justify losing a constraint.

## Decisions to guide

Include the project-specific meaning that affects an Agent's choice:

- **Behavior and evolution:** accepted compatibility, persistence, lifecycle, concurrency, cancellation, recovery, and cleanup obligations, including supported exceptions and the owner of the decision.
- **Placement:** choices between competing product owners, local and shared implementations, consumer adaptation, or established extension seams. Ground them in responsibilities and actual consumers, not a directory tour or generic layering advice.
- **Canonical sources and delivery:** which changes require generation or synchronized consumers, which independently owned or delivered surfaces must remain separate, and how the accepted result is established.
- **Execution and acceptance:** consequential working-directory or runtime requirements, project-specific effect restrictions, required verification evidence, and the conditions that activate an existing preparation, verification, or maintenance capability.

Write only the additional project requirement or exception where shared policy or an existing owner already supplies the rest. A capability pointer states its relevant trigger and required result; leave its commands, sequence, recovery, and detailed success criteria with that capability. In particular, the preparation and change-set verification Skills own their execution workflows. Preserve their project-specific activation conditions without restating their procedures.

Keep durable accepted decisions and their rationale in ADRs, vocabulary with its domain owner, deterministic mechanics with scripts, and conditional policy with its applicable owner. Architecture explanations, module and dependency maps, runtime flows, tool internals, and troubleshooting background belong in the project's knowledge documentation, including `openwiki/` when used. This authoring job does not generate that documentation. Required policy remains reachable before its decision even when Wiki retrieval is skipped or unavailable; a Wiki summary does not become policy authority.

Use the smallest coherent Rule that carries those decisions and necessary pointers. Do not fill headings to imitate the retired Tools, Contracts, and Structure files, concatenate them, or restate shared policy to make the Rule look complete.

## Refresh focus

Preserve valid project decisions, conditions, exceptions, and useful wording while their meaning remains sound. Recheck changed interfaces, source ownership, tool requirements, generator relationships, verification duties, and Skill entry conditions against their current owners. Update the affected fact without copying its owner's full procedure.

A new accepted decision or a demonstrated duplication can justify revision; a new blueprint fingerprint or wording preference alone cannot. Preserve specialized project Skills, custom scripts, ADRs, and unrelated Rules. When a responsibility already has an authoritative home, retain that home and a sufficient route rather than creating another definition in this Rule.

## Authoring boundary and acceptance

The Author may inspect target evidence, run owner-supported read-only or non-fixing checks, and create or replace `.agents/rules/constraints.md` beneath the Candidate root authorized for this request. Settle that root, exact path, and operation through the public writer. Source retirement, other-file changes, live-target writes, and downstream effects remain with their separately authorized owners. Read-only access to earlier Rules supplies evidence, not permission to delete them.

The public writer owns authoring, review, and terminal results. Acceptance requires every consequential project obligation to have a supported disposition and reachable owner; each included condition must lead to a usable decision with its exceptions intact. Check representative behavior, placement, tool execution, verification, and insufficient-evidence cases, as applicable to the project. Confirm the Rule remains sufficient without a Wiki and does not duplicate the two execution Skills. Required checks must pass; an omitted check needs evidence that it is inapplicable.

Include evidence owners, obligation dispositions, check results, preserved additions and constraints, and unresolved or untested surfaces in the handoff. Identify any unavailable evidence, authority, or owner correction that prevents completion. The handoff must be independently usable and grants no generation, installation, retirement, publication, commit, or push outside this Candidate.
