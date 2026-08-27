# Soft-Isolated Role Adapter

Soft isolation is a prompt-enforced behavioral access contract, not a filesystem, process, or
security boundary. Compose the public
[`Role Launch Interface`](../../../../skills/write-rules-and-skills/references/role-launch.md),
[`Frozen Job Design`](../../../../skills/write-rules-and-skills/references/job-design.md),
[`Evaluation Lifecycle`](../../../../skills/write-rules-and-skills/references/evaluation.md), and
conditional
[`Executable Acceptance`](../../../../skills/write-rules-and-skills/references/acceptance.md)
unchanged. Those references solely own bootstrap, capacity and scheduling, common manifests and
reports, callback audits, communication, containment, exits, and finalization. This Adapter owns
only the narrowings below.

## Qualify the behavioral boundary

Statically qualify every public Adapter capability plus enforcement of the prompts, allowlists,
grants, and invocation evidence below. The public closed Envelope remains unchanged and Host
Governance remains execution-only by composition. Qualify the required Probe's termination and
residual-state evidence unconditionally; apply public Runner qualification only when Acceptance is
reachable.

## Bind precise role prompts and allowlists

Freeze each role's complete public prompt plus the following Shared Input and access boundary:

| Role | Prompt and allowlist narrowing |
| --- | --- |
| Controller | The frozen Shared Input, Run Contract, Job Graph, manifests, Candidate fingerprints, lifecycle state, and host audit evidence needed to operate the control plane. Candidate and evidence access is read-only except for exact public control operations; Candidate meaning and finding merit remain outside Controller authority. |
| Probe | Its manifest, mandatory reports, closed Envelope ID, and unique control only. It receives no task evidence, repository or tool access, network authority, peer channel, or delegation. |
| Author | The complete public Author payload, accepted Shared Input, Candidate and owned-resource allowlist, and exact per-path `read`, `write`, `create`, and `delete` grants for the current Authoring or Repair Scope. No unrelated source-project content, Machine work, Acceptance work, network, or delegation. |
| Quality Reviewer | The public Quality payload, complete read-only Candidate resource tree, accepted Shared Input, loading and distribution metadata, selected model, and writing guidance. No Author reasoning, another Reviewer's work, unrelated source content, network, or delegation. |
| Correctness Reviewer | The public Correctness payload, complete read-only Candidate resource tree, declared dependencies, accepted Shared Input, governing evidence, and representative-target portfolio. No Author reasoning, another Reviewer's work, unrelated source content, network, or delegation. |
| Runner | The public read-only Candidate payload, declared inputs and dependencies needed by its immutable representative case, exact fixture, capture contract, and case-owned effects. No unrelated source content, judgment, repair, role control, network, or delegation; a case requiring network or an external effect returns public `EXECUTION_UNAVAILABLE`. |

These allowlists add no communication edge or authority to the public role contracts. A public
bounded update is eligible only while it remains inside the applicable allowlist and preserves the
accepted source-context exclusion and declared dependency closure.

## Bind every invocation

Bind every Probe, Author, Reviewer, and Runner invocation or continuation to the complete public
expected-operation manifest for that exact action. Bind one Adapter-owned **Tool Boundary Record**
in that manifest with exactly these fields: `physically available tools`, `prompt-authorized
subset`, and `boundary`.

Carry the Tool Boundary Record alongside, never inside, the unchanged public three-report
Operation Summary. Before consuming the callback, apply the public Role Boundary Audit to the
manifest, Operation Summary, and companion record together. A physical superset is not itself a
mismatch; behavior outside the prompt-authorized subset is a boundary violation. Host evidence may
corroborate behavior, but this Adapter requires no host hook and makes no host-isolation claim.

## Run the required Probe

After public freeze and static qualification, but before a semantic role, lock, or Candidate write,
use the selected launcher for one disposable Probe. Supply no task context. Through the
authoritative Controller task channel, give one invocation-unique instruction distinct from the
bootstrap envelope and reports, define its exact observable response, and bind both in the Probe
manifest. The Probe performs no file, tool, network, peer, or delegation operation.

Use the host-provided expected envelope fingerprint when available. Otherwise mark the invocation
`PROBE_BASELINE`; require the Probe to report an ordered fingerprint of message roles and content
classes without their contents; it must equal the closed profile and becomes the comparison
baseline for later invocations.

Probe `PASS` requires the exact unique-control response and reports, an inert and separately
identifiable envelope, no inherited or undeclared content, preservation of Controller-channel
authority and bounded updates, established termination and residual state, and no observed
capability contradicting static qualification. Audit the callback first: a manifest or expected-
control mismatch follows the public boundary path, while an audit-admissible failure of a Probe
criterion follows public `PROBE_FAILED`. Launch no semantic role after either result.

## Return to public containment

After adding the Adapter evidence, return every invocation and callback to the public Role Boundary
Audit and the Evaluation Lifecycle's global-exit decision. All public role independence,
communication, capacity, human-stop, terminal precedence, and finalization semantics remain
unchanged. In particular, apply the public contamination-boundary rule: invalidate only its
smallest proven affected unit, and make the incident whole-run only when isolation cannot be
proven. This Adapter adds no classification, incident taxonomy, or recovery procedure.
