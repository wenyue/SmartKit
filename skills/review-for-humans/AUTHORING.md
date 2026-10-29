# Authoring Decisions

## Keep review, publication, and Viewed scopes distinct

Displayed review omits some branch content, publication can include it after the required checks and consent, and Viewed certifies whole-file coverage at a specific PR version. Combining these scopes would either hide outgoing content or mark undisplayed hunks as reviewed. Keep fixed evidence after commits so undisplayed groups remain reviewable even when the worktree becomes clean.

## Keep reasonableness and elegance independent

Reasonableness judges supported behavior, contracts, scope, and actual consequences. The main reviewing Agent invests more effort in elegance through relevant context and design comparison, because structural debt is costly to unwind; this effort does not require delegation or a longer report. Required elegance improvements need optimization or explicit acceptance before advancement, worthwhile limited refinements remain optional, and personal preferences or low-benefit polish are filtered out. Keeping these judgments independent gives evidenced structural burden real weight without treating missing extra defense or personal taste as a correctness defect.

## Preserve completion as a resumable operation

Commit, push, and Viewed recording can succeed independently. The selected completion keeps its scope and remaining steps after interruption; ordinary continue cannot substitute for unfinished completion. Explicit readbacks and exact expected remote identity prevent repeated writes or unsupported review claims.

## Retain contrasting menu examples

The examples cover materially different readiness and authorization states, including partial staging, extra outgoing commits, same-file uncovered hunks, and partial Viewed recording. Those differences determine the available actions. Status icons and reusable closing layouts are recommendations that make repeated groups easy to compare; required review content and operation contracts remain separate. Adapting the presentation avoids mechanical repetition without losing those useful defaults. A single generic closing would also hide the scope and recovery distinctions.
