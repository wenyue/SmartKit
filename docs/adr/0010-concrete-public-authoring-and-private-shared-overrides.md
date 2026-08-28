# Keep Public Authoring Concrete and Shared Authoring Private

Status: Superseded by [ADR 0011](0011-unified-authoring-discovery-runtime.md)

Date: 2026-08-27

## Context

ADR 0009 separated generic authoring behavior from role launch by exposing a public Role Launch
Interface with selectable implementations. That design kept common evaluation behavior local, but
made every public caller understand selection, qualification, and fallback rules even though
ordinary authoring had one normal project-aware behavior. It also left cross-project portability
meaning in the public Skill while the project-private shared Skill owned the evidence restrictions
needed to establish that meaning.

The result was a shallow public Interface: role-launch composition decisions spread into setup
callers, the public workflow, and shared authoring. The private shared entry existed but project
policy routed shared candidates around it. Older ADR references to public selectable Adapters
describe that historical contract.

## Decision

SmartKit keeps `write-rules-and-skills` as one complete public Module with one entry and no
configuration knobs. Its fixed Implementation authors or reviews one ordinary Rule or Skill using
project-aware repository evidence, one concrete fresh-role lifecycle, the existing Author and
Reviewer correction protocol, conditional Machine Validation, conditional Executable Acceptance,
Revision Impact replay, and safe workflow finalization.

The public Interface contains no role-launch injection, external selection, fallback, Probe, or
cross-project portability behavior. Its document structure separates invariant Role Launch
runtime from the concrete project-aware evidence policy for Locality inside the Implementation;
public callers always receive both as one behavior.

Project-private `write-shared-rules-and-skills` is the direct entry and sole owner for a
cross-project SmartKit Rule or Skill. It owns shared portability, dependency closure,
source-project exclusion, representative targets, soft-isolated evidence access, and its mandatory
post-freeze Probe. That Skill alone records its exhaustive relationship to the public workflow.
Unchanged authoring, review, correction, Acceptance, exit, and finalization behavior remains with
the public owners and is not duplicated privately.

The physical host envelope remains present for every role. Mandatory host and project instructions
govern execution of already-authorized operations but acquire no Candidate meaning, evidence,
permission, dependency, or transition merely from their presence. Soft isolation restricts
semantic evidence and prompt-authorized access; it is a behavioral qualification rather than a
filesystem, process, or security boundary.

The shared Probe runs after the complete contract freezes and before Candidate fingerprinting,
lock acquisition, semantic roles, or Candidate writes. Its invocation uses the common manifest and
audit lifecycle. A boundary or control mismatch follows `ROLE_BOUNDARY_VIOLATION`; an otherwise
admissible criterion failure follows `PROBE_FAILED`. Every started Probe receives termination,
quiescence, residual-state capture, and common workflow finalization. Candidate edits do not
invalidate launcher-policy evidence.

Project Contracts route ordinary governed Rules and Skills directly to the public entry and shared
SmartKit candidates directly to the private entry. The private Skill remains outside plugin
registries, manifests, setup catalogs, installation, and distribution. Setup-generated
project-local targets invoke the concrete public workflow without selecting role mechanics. Setup
Authoring Contracts reuse the same concrete Role Launch runtime through their separately owned
Author, Machine, and Static Reviewer sequence.

## Consequences

The public Module gains Depth: callers learn one authoring entry while role coordination,
evaluation, and finalization stay behind it. The internal role-document seam preserves Locality for
the two evidenced environments without exposing a choice through the public Interface. Shared
semantics and shared qualification now change in one private owner.

Removing a public portability resource and the former private Adapter resource removes their paths
and mirrors without aliases or shims. Required Simplified-Chinese mirrors follow only after the
canonical English sources finish through the separately owned translation handoff. This decision
supersedes ADR 0009; ADR 0009 and the earlier records remain historical evidence rather than current
runtime policy.
