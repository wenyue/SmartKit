# Correctness Review

Start two fresh Reviewers concurrently and keep each one through its correction loop. Give both the
complete Candidate Version, complete accepted user-decision context, preserved obligations,
governing evidence, candidate model, and applicable evidence. Give neither Reviewer the Author's
reasoning, intended fixes, or a diff.

## Semantic Fidelity and Ownership Reviewer

Check that every required meaning is preserved or intentionally changed, every addition has
evidence, and every obligation lives with the correct owner and applicability. Find omissions,
unsupported additions, accidental semantic weakening, contradictory outcomes, hidden dependencies,
and misplaced policy or procedure.

## Agent Executability and Behavioral Closure Reviewer

Check that an eligible Agent can enter, choose a supported branch, use allowed tools and resources,
respect authority and side-effect boundaries, recover or stop, validate, and reach exactly one
prioritized exit. Find missing triggers, preconditions, dependencies, permissions, actions,
failures, recovery, validation, or completion boundaries.

Apply the common Correction Cycle independently to both scopes. A Reviewer may transfer a concern
to the other scope but may not decide it. Correctness Review passes only when both Reviewers report
no finding worth fixing for the same Candidate Version and every note routed to the Correctness pair
is resolved. Notes owned by another stage follow the Correction Cycle queue or rewind and block
only as that contract specifies.
