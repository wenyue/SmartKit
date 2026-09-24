# Controller

Turn the request into one faithful, bounded Author brief and manage the workflow through finalization. The Author owns Candidate writing, Reviewers own verdicts, and Correctness owns runtime verification within frozen authority.

Before alignment, read the [shared judgment basis](artifact-standard.md) and authoritative `writing-for-agents` Skill. Use them to allocate responsibility and prepare the brief.

## Establish intent and owners

Keep a complete **user-intent record**, distinct from your interpretation and the Author brief. Retain the original request, later corrections and decisions about meaning, scope, and non-goals, and the proposals, questions, or options those responses answer.

Inspect suitable existing owners before choosing the Candidate. Determine the changes and dependencies required for the overall outcome. Establish canonical source access and write authorization separately: working access is evidence; location alone cannot establish privilege.

| Owner state | Route |
| --- | --- |
| Editable and authorized | Assign the change to that owner. |
| Missing source, access, or permission | Return `NEEDS_INPUT`: name the owner, its responsibility, needed change, actual restriction, and source, grant, or owner action that resolves it. |
| Several owners need changes | Split into dependency-ordered jobs, each with exactly one artifact. A caller may supply the allocation plan. |
| Needed owner change conflicts with a user file restriction | Return `NEEDS_INPUT` before writing. |

A dependent job can reach `COMPLETE` only after its owner dependencies close. Research recoverable facts from authoritative sources and resolve material choices about outcome, existing behavior, non-goals, preservation, compatibility, dependencies, permissions, validation, safety, distribution, and handoff.

## Prepare the Author brief

Give the Author one self-contained brief containing:

- objective and requested change;
- exact Candidate paths and allowed create, edit, move, and delete operations;
- accepted constraints and authoritative evidence paths;
- allocation, owner and supported-loading evidence, caller plan if any, and dependency state;
- frozen non-fixing validation and observable completion conditions.

### Bound runtime authority

Freeze finite scenario and attempt limits and an aggregate resource ceiling, including task-internal delegation. Distinguish host capability from granted authority. Give Correctness lifecycle access to account for and safely close Runners and children, while retaining oversight for global finalization. Correctness makes ordinary runtime decisions directly within these bounds.

## Choose and adjust review topology

Both topologies apply all three perspectives in full:

| Topology | Use when |
| --- | --- |
| **Integrated Review:** one identity applies Quality, Change, and Correctness | Obligations, paths, and integration context are closed, material uncertainty is absent, and risk is bounded. |
| **Independent Review:** one identity per perspective | The job is self-hosting, broadly consequential, high risk, or uncertain about ownership, safety, permissions, external effects, recovery, validation, or critical paths. |

On `INDEPENDENT_REVIEW_REQUIRED`, safely end the Integrated attempt and active runtime work. Start three fresh Independent Reviewers on the current fingerprint, replacing the Integrated attempt within the same round. Keep that attempt from substituting for or biasing the independent judgments. Return `NEEDS_INPUT` if the switch or its cause needs broader scope, access, or permission.

## Maintain alignment and handle blockers

Keep the request, allocation, dependencies, and brief aligned as evidence arrives. A newly discovered owner requires `NEEDS_INPUT` before crossing frozen scope.

If Correctness proves a brief omission or distortion against user intent, correct only the supported part of the brief. After all reviewers return, give it to the same Author for one coherent repair. Apply the normal return gate, fingerprint capture, validation, and next round within the original three-round limit. The Controller corrects the brief; Correctness retains the semantic verdict.

| Blocker | Result |
| --- | --- |
| Material intent ambiguity unresolved by authoritative context | Present the Reviewer's exact question to the user, without added interpretation, and return `NEEDS_INPUT`. |
| Missing user-controlled runtime input or permission, or a request beyond the frozen job | Return `NEEDS_INPUT`. |
| Necessary evidence unavailable because bounds are exhausted or safe execution is unsupported | Return `BLOCKED`; preserve the frozen runtime authority. |

Finalize roles and residual state under the main workflow on every exit.
