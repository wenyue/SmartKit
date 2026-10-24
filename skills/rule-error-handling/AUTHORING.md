# Authoring Decisions

## Separate evidence retention from public recognition

Keep diagnostic evidence and caller-inspectable failure identities as separate decisions. Unwrapping may expose an implementation dependency, while preserving a cause for diagnosis need not make it public API. The faithful-refinement exception therefore preserves concrete native category handling instead of treating any shared exception base as compatibility.

## Explain broad interception at its site

Keep the maintainer comment requirement tied to broad interception with a common disposition. A broad catch can silently absorb unrelated defects unless the reader can see why every covered failure is safe to handle. Routine returned-error propagation is deliberately excluded; applying the requirement there would produce repetitive comments without the same risk.

## Disclose recovery guidance by the decision it serves

Keep ordinary handling, ownership, and feedback policy in the entry. Load the longer recovery, persisted-data, and remediation references only for their stated decisions. Making them universal reads would burden routine propagation; hiding fundamental policy there would make ordinary reviews incomplete.
