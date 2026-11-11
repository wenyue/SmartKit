# Following a Selected Delivery through New Findings and Partial Effects

This fictional PR review is at 4 / 9 files. The displayed group has no unresolved finding, but the selected workspace contains staged deletions that have not been reviewed. The user has not yet selected delivery.

## Offer the work that Pass will start

- A. **Pass** (recommended): Inventory and review the remaining delivery scope, complete its checks, commit and publish the complete outgoing changes, record eligible Viewed files, and continue from the saved next group.
- B. **Continue**: Review the next group without delivery, keeping the staged deletions untouched.

**User:** Pass.

The inventory now includes the staged deletions, an unpublished commit, and tests from another conversation. Those contents enter delivery coverage even though the main review filter did not display them. If this supplementary review and its checks reveal no new actionable item, the Agent completes the selected delivery without asking for Pass again.

## Supplementary review finds a defect and an optional simplification

In this branch, deleting a still-used export breaks an existing caller (M11), while another changed file duplicates a formatter that it could safely reuse (M12). The supplementary report explains both before offering:

- A. **Fix** (recommended): Restore M11's supported export, check the repair, and re-review its affected callers; M12 remains undecided.
- B. **Optimize**: Apply M12's formatter simplification, check it, and re-review; M11 remains unresolved.
- C. **Ignore**: Retain M11's broken caller and M12's duplicate formatter, accepting the disclosed consequences.

**User:** Fix M11.

After the repair checks and dedicated re-review pass, M12 is still an outstanding choice. The Agent offers Optimize for M12 or Ignore its duplicate formatter; it does not ask for another Pass.

**User:** Keep the duplication for now.

M12's burden remains documented as accepted. With both decisions resolved and all required coverage and checks complete, the Agent resumes the original commit, publication, and Viewed work, then advances from the saved position.

## The original request was only-deliver

If the user had said “Deliver the full scope you described, but do not start the next review group” at the first choice, the same inventory, supplementary findings, checks, and repairs would be needed. After completion, the Agent would stay at 4 / 9 rather than starting the next group. The retained request determines that final position; resolving M11 and M12 supplies no separate continuation instruction.

## A subset request with no delivery selected

In a different group, M2 can omit a promised flush and M7 has a supported cleanup simplification. The user says, “Only optimize M7 first.” The Agent changes and re-reviews M7, reports its resolved burden and checks, and keeps M2's flush defect visible. No delivery or advancement was selected, so that optimization ends at the updated decision.

## A scope conflict or publication failure interrupts delivery

In another branch of the staged-deletion inventory, the user had explicitly asked to retain an exported fixture that the staged changes delete. The Agent cannot derive a coherent final version satisfying both. It names that fixture and asks which intended content to deliver, keeping Pass pending while the user-owned choice is unresolved.

If instead the scope is settled but publication is unavailable with no supported recovery route, the Agent reports that external blocker and the confirmed local state. The selected Pass remains pending; replacing it with Continue would change the user's requested effect without a decision. Before any delivery selection, the same publication limit could leave a read-only Continue option available.

## Recording covers more than the last displayed group

Later in the PR review, all nine main files and one supplementary production file have complete current PR-delta coverage. Four main files were advanced earlier with Continue. Only recording remains. The eligible Viewed set contains all ten files, while main progress stays 9 / 9; unreviewed tests and files with only repair-fragment coverage remain unmarked.

In a partial-success branch, commit and push are confirmed and six of those ten Viewed updates succeed. The Agent reports the remaining four as pending, reconciles their actual GitHub state, and resumes recording. It does not repeat the confirmed commit or push. After an interrupted run, the retained version, viewer, path set, and confirmed results identify what remains to be done.

## Local delivery has a smaller selected effect

A separate user requested preparation for a local commit. A label edit is the complete delivery inventory, its checks and review are ready, and no remote publication was requested. At scope end, Pass commits, verifies, and finishes; Finish ends with the edit uncommitted. This local choice has no PR publication or Viewed effect to inherit from the PR scenario above.
