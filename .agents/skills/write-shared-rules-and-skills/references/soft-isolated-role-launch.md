# Soft-Isolated Role Launch

Soft isolation is a prompt-enforced behavioral evidence and access contract, not a filesystem,
process, host-governance, or security boundary. Apply the invariant lifecycle in public
[`role-launch.md`](../../../../skills/write-rules-and-skills/references/role-launch.md) unchanged.
This private resource owns the shared evidence restrictions, Tool Boundary Record, Runner
narrowing, and mandatory Probe.

## Preserve mandatory Host Governance

The host-provided AGENTS, recommended-plugin catalog, and environment envelope remains physically
present and mandatory instructions continue to govern execution. Mere envelope presence supplies
no Candidate meaning, evidence, permission, dependency, Acceptance fact, or transition. A
source-project fact is inadmissible as portable meaning unless accepted Shared Input independently
establishes it. The role may observe physically present material without receiving authority to use
it as semantic evidence.

## Qualify the behavioral evidence boundary

Before freeze, establish the common Role Launch readiness plus enforcement of the prompts,
allowlists, grants, and invocation evidence below. Establish the Probe's launch, exact control,
reports, termination, quiescence, and residual-state evidence unconditionally. Establish Runner
termination and quiescence only when Acceptance is reachable.

## Bind precise role prompts and allowlists

Freeze each role's complete public prompt plus the following Shared Input and access boundary:

| Role | Prompt and allowlist restriction |
| --- | --- |
| Controller | The frozen Shared Input, Run Contract, Job Graph, manifests, Candidate fingerprints, lifecycle state, and host audit evidence needed to operate the control plane. Candidate and evidence access is read-only except for exact public control operations; Candidate meaning and finding merit remain outside Controller authority. |
| Probe | Its manifest, mandatory reports, closed Envelope ID, and unique control only. It receives no task evidence, repository or tool access, network authority, peer channel, or delegation. |
| Author | The complete public Author payload, accepted Shared Input, Candidate and owned-resource allowlist, and exact per-path `read`, `write`, `create`, and `delete` grants for the current Authoring or Repair Scope. It receives no unrelated source-project content, Machine work, Acceptance work, network, or delegation. |
| Quality Reviewer | The public Quality payload, complete read-only Candidate resource tree, accepted Shared Input, loading and distribution metadata, selected model, and writing guidance. It receives no Author reasoning, another Reviewer's work, unrelated source content, network, or delegation. |
| Correctness Reviewer | The public Correctness payload, complete read-only Candidate resource tree, declared dependencies, accepted Shared Input, governing evidence, and representative-target portfolio. It receives no Author reasoning, another Reviewer's work, unrelated source content, network, or delegation. |
| Runner | The public read-only Candidate payload, declared inputs and dependencies needed by its immutable representative case, exact fixture, capture contract, and case-owned effects. It receives no unrelated source content, judgment, repair, role control, network, external-effect authority, or delegation. A case that requires network or an external effect returns public `EXECUTION_UNAVAILABLE` before launch. |

These restrictions add no communication edge or authority to the public role contracts. A public
bounded update is eligible only while it remains inside the applicable allowlist and preserves the
accepted source-context exclusion and declared dependency closure.

## Bind every invocation

Bind every Probe, Author, Reviewer, and Runner invocation or continuation to the complete public
expected-operation manifest for that exact action. Bind one private **Tool Boundary Record** in
that manifest with exactly these fields: `physically available tools`, `prompt-authorized subset`,
and `boundary`.

Carry the Tool Boundary Record alongside, never inside, the unchanged public three-report
Operation Summary. Before consuming the callback, apply the public Role Boundary Audit to the
manifest, Operation Summary, and companion record together. A physical superset is not itself a
mismatch; behavior outside the prompt-authorized subset is a boundary violation. Host evidence may
corroborate behavior, but this contract requires no host hook and makes no host-isolation claim.

## Run the mandatory Probe

Statically qualify the complete Probe lifecycle before freeze. After freeze and before Candidate
fingerprinting, lock acquisition, any semantic role, or Candidate write, launch one disposable
Probe through the frozen role launcher. Supply no task context. Through the authoritative
Controller task channel, give one invocation-unique instruction distinct from the bootstrap
envelope and reports, define its exact observable response, and bind both in the Probe manifest.
The Probe performs no file, tool, network, peer, or delegation operation.

Use the host-provided expected envelope fingerprint when available. Otherwise mark the invocation
`PROBE_BASELINE`; require the Probe to report an ordered fingerprint of message roles and content
classes without their contents; it must equal the closed profile and becomes the comparison
baseline for later invocations.

Audit the invocation and callback through the common Role Boundary Audit before consuming the
Probe response, and capture every obtainable response and report. After every Probe return mode,
preserve that evidence, end the Probe, establish quiescence, record exact residual state, and
complete the audit with those finalization facts.

Only then classify the underlying Probe result from the complete record. A manifest,
expected-control, bootstrap, grant, report, or behavioral-boundary mismatch follows common
`ROLE_BOUNDARY_VIOLATION`. Otherwise, failure of the unique response, inert-envelope,
source-exclusion, termination, quiescence, or residual-state criteria returns `PROBE_FAILED`.
Probe `PASS` requires affirmative evidence for every criterion.

Any Probe launch activates common workflow finalization even when no lock or semantic role exists.
When the Probe cannot be ended or proven inactive, common finalization returns `TEARDOWN_FAILED`,
preserves the already-classified underlying Probe result, including `ROLE_BOUNDARY_VIOLATION` or
`PROBE_FAILED`, and blocks a clean terminal report. Start no semantic role, lock, fingerprint, or
Candidate work after `PROBE_FAILED`, `ROLE_BOUNDARY_VIOLATION`, or failed teardown.

Probe evidence establishes the frozen launcher and soft-isolated evidence policy. Candidate edits
cannot affect what it proves, so Revision Impact neither invalidates nor replays it. A material
change to the launcher, evidence policy, Shared Input boundary, or Probe contract requires a new
aligned run.

## Extend private exit precedence

Apply the common Role Boundary Audit and conditional safety finalization first. For otherwise
admissible state, insert `PROBE_FAILED` after the immediate `HUMAN_DECISION_REQUIRED` stop and
before `LOCK_UNAVAILABLE` or `CANDIDATE_CHANGED`. `TEARDOWN_FAILED` preserves the underlying result
and blocks clean success. This resource adds no other classification or recovery procedure.
