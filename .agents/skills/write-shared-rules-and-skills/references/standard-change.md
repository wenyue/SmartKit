# Acceptance Standard Change

When the candidate changes the public authoring Skill, Reviewer rules, or Acceptance Standard, it
must not qualify by grading itself against its weakened candidate text.

Use this basis:

```text
Qualification Basis = Previous Accepted Standard + Accepted Standard Change
```

## Accept the change before candidate review

1. Form one content-frozen Proposed Standard Change from the accepted conversation, Issue, or Spec.
   State its source, explicit changes, preserved obligations, and non-goals. Do not infer allowed
   changes from the candidate.
2. After the top-level Soft-Isolation Probe passes, give a separate tool-free Reviewer one Context
   Packet containing only the Previous Accepted Standard, accepted user goal, Proposed Standard
   Change, and explicitly selected shared Rules. It judges completeness, consistency,
   verifiability, and preservation of every unchanged obligation.
3. On `PASS`, retain the exact reviewed content in controller context as the Accepted Standard
   Change. On `FAIL`, correct the proposal and use a new Soft-isolated Reviewer; the proposal is not
   yet part of the Standard.
4. Evaluate the actual candidate against the Previous Accepted Standard plus that Accepted Standard
   Change. Only a fully qualified canonical Candidate Revision becomes the latest accepted Standard.

The independent change review tests whether the new requirement is sound; later candidate review
tests whether the implementation satisfies it. Persist no proposal, packet, digest manifest, or
review report solely for qualification. The final Standard and ADR retain durable outcomes.
