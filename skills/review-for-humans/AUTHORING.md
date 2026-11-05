# Authoring Decisions

## Keep the decision loop in one place

The entry owns assessment, findings, user intent, and advancement. Preparation handles the conditional PR/workspace branch; Delivery owns inventory, physical effects, and recovery. Delivery returns readiness and observed results rather than deciding what the user requested. This separation keeps an interrupted write or a supplementary finding from silently replacing a pending Pass.

Principles govern uncommon situations; four common-case tables stabilize recommendations and ordering at the actual decision points. One option represents each action type, with IDs defining its scope. Treating each finding as an option would recreate duplicate Optimize choices and obscure the user’s decision.

Pass selects delivery preparation as well as its applicable effects. Requiring prepared delivery before offering Pass would hide that choice after ordinary review and repairs. New supplementary findings pause writes for a decision, while the original selection remains pending so resolving them needs no second Pass.

Necessity and implementation belong in one assessment path through findings, repair, and independent re-review. Splitting them into separate checklists, or treating a previous Fix selection as proof, would let a well-tested mechanism survive after its original premise was disproven. Keep the decisive caller, trigger, obligation, and existing guarantees with the finding without imposing a separate evidence schema.

## Give presentation one owner

Report Format owns the complete layout and explanation depth, and every report kind loads it. This is a presentation boundary, not reduced ordinary reading. The entry retains inspection coverage and finding disclosure so a concise report cannot shrink the review.

Examples supply concrete premises and choices. One complete report demonstrates the format; abbreviated transitions avoid repeatedly reproducing it. Neither examples nor these authoring notes establish operative policy.

## Separate progress, coverage, and effects

Main progress follows the fixed comparison. Delivery can require more non-test review without changing that sequence, while tests remain within inventory/checks rather than semantic coverage. Viewed depends on complete PR-file assessment, not displayed progress or successful checks. Keeping these scopes distinct prevents full-workspace delivery from marking partially reviewed files or losing undisplayed evidence.

The entry preserves pending Pass versus only-deliver; Delivery preserves actual completed and uncertain effects. Their distinct records allow recovery without repeated publication or unintended advancement.

## Keep the mechanical interface beside its implementation

The helper's CLI help owns its capabilities, request schema, state, outputs, and retries. Delivery requires that route for supported effects and retains semantic coverage and authorization. Its manual path covers demonstrated unsupported plans, not failed supported operations; common capability gaps should be repaired in the helper so recovery keeps one owner. Duplicating CLI details in another reference would create a second interface specification without making the helper a semantic reviewer.
