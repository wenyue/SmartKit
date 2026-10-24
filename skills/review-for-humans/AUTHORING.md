# Authoring Decisions

## Keep review, publication, and Viewed scopes distinct

Displayed review omits some branch content, publication can include it after the required checks and consent, and Viewed certifies whole-file coverage at a specific PR version. Combining these scopes would either hide outgoing content or mark undisplayed hunks as reviewed. Keep fixed evidence after commits so undisplayed groups remain reviewable even when the worktree becomes clean.

## Keep reasonableness and elegance independent

A correctness or scope defect can block advancement, while a supported simplification remains optional unless it exposes a separate defect. Merging the judgments would turn taste into a repair gate or let an elegant implementation disguise an unreasonable change.

## Preserve completion as a resumable operation

Commit, push, and Viewed recording can succeed independently. The selected completion keeps its scope and remaining steps after interruption; ordinary continue cannot substitute for unfinished completion. Explicit readbacks and exact expected remote identity prevent repeated writes or unsupported review claims.

## Retain contrasting menu examples

The examples cover materially different readiness and authorization states, including partial staging, extra outgoing commits, same-file uncovered hunks, and partial Viewed recording. Their shared presentation is intentional, while the differing available actions carry the teaching value. A single generic closing would hide those distinctions.
