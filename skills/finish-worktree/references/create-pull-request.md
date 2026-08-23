# Create a Pull Request

Publish the verified delivery head and retain its local worktree for follow-up.
When the scope is **Already Delivered**, recheck that the resolved pull-request base still has no
scope diff, retain the source branch and worktree, report the proof and skipped publication, and stop
without pushing or creating an empty pull request.

1. Resolve the exact remote, base branch, head branch, pull-request title, body, and draft state.
   Ask for any value that repository evidence and the accepted request do not determine.
2. Reconfirm the source worktree is clean, the resolved pull-request base is the required history
   boundary of the complete owned range, and review and verification remain current. A moved base
   returns to finalization.
3. Push the exact source branch without force, then create the pull request through the available
   host-native or repository-authorized interface.
4. Verify the remote branch commit, pull-request base and head, draft state, and returned URL.
5. Keep the local source branch and worktree for review updates. Preserve later published review-fix
   commits as review history; leave repository-host finalization to the repository's pull-request policy.
   Remove local state only after a later, separately authorized completion outcome.
