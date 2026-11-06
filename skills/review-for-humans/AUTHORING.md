# Authoring Decisions

## Keep the decision loop in one place

The entry owns assessment, findings, user intent, and advancement. Preparation handles the conditional PR/workspace branch; Delivery owns inventory, physical effects, and recovery. Delivery returns readiness and observed results rather than deciding what the user requested. This separation keeps an interrupted write or a supplementary finding from silently replacing a pending Pass.

Principles govern uncommon situations; four common-case tables stabilize recommendations and ordering at the actual decision points. One option represents each action type, with IDs defining its scope. Treating each finding as an option would recreate duplicate Optimize choices and obscure the user’s decision.

Pass selects delivery preparation as well as its applicable effects. Requiring prepared delivery before offering Pass would hide that choice after ordinary review and repairs. New supplementary findings pause writes for a decision, while the original selection remains pending so resolving them needs no second Pass.

Necessity and implementation belong in one assessment path. Splitting them into separate checklists would let a well-tested mechanism receive an elegance judgment before its capability has a supported purpose.

## Give presentation one owner

Report Format owns one file-based layout, item depth, closing order, and menu rendering across ordinary, supplementary, repair, and selected-O reports. The entry retains assessment, identity, action semantics, and choice ordering. A separate repair-summary format caused presentation to drift and made supporting changes easy to hide; choosing depth per item keeps compact reports within the same visible coverage.

One complete ordinary report and one complete multi-file repair demonstrate the shared layout, including compact items without a redundant title. Abbreviated transitions illustrate other decisions without reproducing each report. Examples and these notes explain the design; operative requirements stay in the entry and Report Format.

## Separate progress, coverage, and effects

Main progress follows the fixed comparison. Delivery can require more non-test review without changing that sequence, while tests remain within inventory/checks rather than semantic coverage. Viewed depends on complete PR-file assessment, not displayed progress or successful checks. Keeping these scopes distinct prevents full-workspace delivery from marking partially reviewed files or losing undisplayed evidence.

Existing finding IDs remain stable through repair, while additional separately explained M changes consume the next unused IDs. Their relationship belongs in the repair introduction, not repeated item labels or a second numbering system. Consequently, the highest M ID is not a main-progress count. Selected-O supporting files use file explanations rather than new M IDs or invented incidental observations, preserving the separate scope the user selected.

The entry preserves pending Pass versus only-deliver; Delivery preserves actual completed and uncertain effects. Their distinct records allow recovery without repeated publication or unintended advancement.

## Keep the mechanical interface beside its implementation

The helper's CLI help owns its capabilities, request schema, state, outputs, and retries. Delivery retains semantic coverage and authorized-effect requirements and supplies the manual path for unsupported plans. Duplicating CLI details in another reference would create a second interface specification without making the helper a semantic reviewer.

Effect modes freeze the user's chosen history change. Transport remains a run-time choice so a blocked Git endpoint can be bypassed on resume without creating a second publication plan. Both routes bind the same objects and expected old ref. API object reconstruction verifies exact SHAs and refuses metadata it cannot reproduce before changing the ref, preserving the identity required by recovery and review evidence.
