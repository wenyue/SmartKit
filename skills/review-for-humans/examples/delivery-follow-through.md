# Resuming Selected Delivery

## Supplementary findings during Pass

In this fictional PR review, the user chooses Pass at 4 / 9 files. The inventory includes a staged deletion, an unpublished commit, and test changes. Supplementary review finds that the deletion breaks a supported caller (M11) and that the unpublished commit duplicates a formatter it could safely reuse (M12). The report offers these choices at the saved 4 / 9 position.

- A. **Fix** (recommended): Restore the export for M11, check the repair, and re-review its affected callers. M12 remains undecided.
- B. **Optimize**: Reuse the formatter for M12, check the change, and re-review. M11 remains unresolved.
- C. **Ignore**: Keep the broken caller under M11 and the duplicate formatter under M12, accepting their stated consequences.

The user selects Fix M11. After its checks and re-review pass, the remaining choices are Optimize M12 or Ignore its duplicate formatter. The user says to keep the duplication. Record that trade-off, finish the review and checks for the full delivery scope, and disclose the concrete plan. Resume the effects already selected with Pass.

After commit and publication are confirmed, verify the resulting PR head and pin the comparison. With only Viewed remaining, review the saved next group read-only while the managed recording process runs. Use the delivery guide's foreground route when managed sessions are unavailable. If the original request was only-deliver, complete recording and stay at 4 / 9.

## Commit and push succeeded but recording is incomplete

In a later delivery, nine main files and one supplementary production file have complete current PR-delta coverage. All ten qualify for Viewed, including earlier reviewed files that have yet to be recorded. Main progress stays 9 / 9.

Commit and push are confirmed, and six of ten paths are verified Viewed. Report the four pending paths, reconcile their actual state for the retained viewer and PR version, and finish recording and readback using the retained plan. Reuse the confirmed commit and push results.
