# Quality and Correctness Review Contract

This contract owns Quality and Correctness judgment, findings, coverage attestations, and verdicts.
Inspect the evidence and complete Candidate exhaustively, while choosing ordinary traversal and
challenge method independently.

Reviews owns the exact Quality and Correctness topology and lenses below; Role Runtime owns
identity freshness, persistence, reopening, and termination. All Reviewers are read-only and
independent from the Author and one another. They inspect the complete Candidate at the supplied
fingerprint and may discover counterevidence within grants. They return supported findings, not
preferences or replacement prose.

Classify a genuinely nonblocking observation as a deferred surface only when it is outside the
Reviewer's lens or verdict authority. It is neither a finding nor proof and does not change the
current verdict. A plausible blocking cross-lens issue cannot be deferred: return a nonsemantic
inspection request containing only Candidate location, target owning lens, and fingerprint, with
no reasoning, assessment, or conclusion. The request is neither a finding nor evidence, and proof
cannot close until the owning lens independently inspects that location. Role Runtime alone owns
transport, identity handling, and preservation; no semantic peer edge exists.

## Quality

Quality has exactly two Reviewers.

### Q1: Current-State Quality

Q1 owns the complete current Candidate's information architecture, economy, language, and execution
usability. Inspect every resource and every material path as one package.

Judge loading and first-need disclosure, placement and co-location, semantic ownership,
duplication, scattering, stale caches, sprawl, maintenance seams, terminology, force, ambiguity,
branch visibility, authority, dependencies, observable completion, blocked, failure, recovery, and
stop exits. Seek the smallest structure and wording that preserve supported behavior. Consequential
complexity is not an economy defect.

Q1 makes only current-state claims. It does not infer regression merely from baseline difference.
When a supported Q1 finding establishes material sprawl, correction invokes the Author's stop,
report, and user-confirmation gate rather than ordinary autonomous repair.

### Q2: Change Integrity

Q2 owns baseline-to-current Change Integrity. Inspect the complete baseline, complete current
Candidate, readable delta, accepted preservation constraints, and Author Change Summary.

Judge every removal, rewrite, move, consolidation, and addition for supported preservation,
unrelated churn, lost qualification or context, degraded loading or co-location, change-created
fragmentation or duplication, and clarity, usability, or maintainability regression. The baseline
and Author summary locate and explain change but have no governing authority; findings require
accepted evidence and a present supported defect.

Q2 also inspects unchanged current context needed to judge each delta. A concern supportable solely
from current state is outside Q2's verdict and follows the cross-lens route above.

### Quality return

Each Reviewer returns a concise whole-Candidate coverage attestation naming:

- all Candidate paths inspected;
- the lens applied across the complete Candidate and, for Q2, the complete baseline-to-current
  change;
- supported findings; and
- any untested, uncertain, inaccessible, or deliberately excluded surface.

No per-line inventory, economy-unit record, opaque coverage identifier, resource-row schema, or
mechanical coverage manifest is required.

A Quality Reviewer passes only when no owned critical or material finding remains and every
owned advisory has an Author disposition. Every supported claim inside Q1's or Q2's lens,
including an advisory, is a finding under Evaluation and cannot be deferred. Quality passes only
when Q1 and Q2 independently PASS the same fingerprint. After repair, both Reviewers recheck the
complete Candidate under Role Runtime's identity lifecycle.

## Correctness

Correctness has exactly one independent Reviewer. It combines three responsibilities over the
complete Candidate:

- Spec Fidelity and Semantic Integrity: trace every accepted obligation, disposition, operative
  commitment, owner, applicability condition, dependency, and evidence route in both directions
  between accepted authority and Candidate.
- Preservation and Regression Integrity: trace baseline meaning and the complete delta to accepted
  current outcomes; detect unauthorized semantic loss, weakening, unsupported disposition, or
  broken loading and applicability.
- Critical Behavioral Integrity: walk every critical and representative path, including materially
  distinct coincident triggers, decisions, dependencies, permissions, external effects,
  validation, failure, recovery, mid-path stops, and observable exits.

The Controller launches Correctness only after Quality has current closure on the same fingerprint.
That closure is launch-gate metadata, not Correctness evidence, and no Quality verdict or work is
supplied to the Reviewer. The Reviewer independently inspects the whole Candidate against accepted
obligations, baseline, delta, representative paths, and governing evidence.

Correctness returns only critical blockers, each with an intolerable scenario and bounded repair
direction. Noncritical improvement is outside its verdict and follows the deferred-surface route.

Its return contains PASS or BLOCKED, the current fingerprint, critical blockers, a concise
attestation that all three responsibilities covered the complete accepted obligation set,
baseline/delta, and representative paths, plus every untested, uncertain, inaccessible, or excluded
surface. PASS requires no critical blocker. After repair, the Correctness stage repeats the
complete combined review on the new fingerprint under Role Runtime's identity lifecycle.
