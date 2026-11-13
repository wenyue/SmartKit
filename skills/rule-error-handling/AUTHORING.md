# Authoring Decisions

## Separate evidence retention from public recognition

Keep diagnostic evidence and caller-inspectable failure identities as separate decisions. Unwrapping may expose an implementation dependency, while preserving a cause for diagnosis need not make it public API. The faithful-refinement exception therefore preserves concrete native category handling instead of treating any shared exception base as compatibility.

## Explain broad interception at its site

Keep the maintainer comment requirement tied to broad interception with a common disposition. A broad catch can silently absorb unrelated defects unless the reader can see why every covered failure is safe to handle. Routine returned-error propagation is deliberately excluded; applying the requirement there would produce repetitive comments without the same risk.

## Give each recovery strategy one home

Keep common outcome, propagation, diagnosis, authority, responsibility, and recovery criteria in the entry. Disclose strategies through five decision-based references, loading several for overlapping cases. Domain policy may retain its state invariants and completion contracts; duplicating recovery methods there would create competing owners.

## Simplify within the accepted outcome

Prefer direct handling and an established bounded recovery over additional protective machinery when both meet the accepted outcome. Deletion of invalid stored data is conditional on loss authority and a valid resulting state: a project's migration and reconstruction guarantees cannot establish that permission for other projects. Losing this distinction would turn a useful simplification into unauthorized data loss.
