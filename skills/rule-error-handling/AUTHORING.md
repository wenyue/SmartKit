# Authoring Decisions

## Separate evidence retention from public recognition

Keep diagnostic evidence and caller-inspectable failure identities as separate decisions. Unwrapping may expose an implementation dependency, while preserving a cause for diagnosis need not make it public API. The faithful-refinement exception therefore preserves concrete native category handling instead of treating any shared exception base as compatibility.

## Explain broad interception at its site

Keep the maintainer comment requirement tied to broad interception with a common disposition. A broad catch can silently absorb unrelated defects unless the reader can see why every covered failure is safe to handle. Routine returned-error propagation is deliberately excluded; applying the requirement there would produce repetitive comments without the same risk.

## Disclose recovery guidance by the decision it serves

Keep general handling, recovery, ownership, and feedback in the entry. Disclose persisted-data guidance for decisions about loss and later reads, and retries and side effects for decisions about replay, partial effects, and interruption. An operation can need both references.
