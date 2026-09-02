# Create a Pull Request

Publish the verified delivery head without force and establish at most one exact pull request. This
is a non-integrating handoff until the authoritative target contains the accepted result.

1. Require explicit remote authority. Freeze the repository, base branch and observed commit, head
   ref, delivery commit, title, body, draft state, repository-approved host interface, and the
   success proof. Authorized observations must also establish any existing remote head and pull
   request.
2. Recheck the source, immutable `history_result`, owned range, delivery head/tree, review binding,
   publication, and remote base/head. A moved base is target drift after history: do not repeat the
   history policy. Reprove **Already Delivered** when possible; otherwise stop with
   `history_result` retained for the target-movement owner and record a stopped `outcome_result`. An
   incompatible head, uncertain publication, unavailable host proof, or ambiguous prior attempt
   stops before another effect.
3. If the base contains every accepted effect, return **Already Delivered** without a push or empty
   pull request. If one open pull request already matches every frozen field and exact delivery
   commit, verify and return that existing handoff without duplication.
4. Otherwise push the exact delivery commit once to the frozen head ref with a normal non-force
   push as one logical attempt. After proving that result, create the pull request once through the
   approved interface as a second logical attempt. Re-observe before and after each; an ambiguous
   result remains in-flight, is retained, and is not retried.
5. Prove the remote head commit and the pull request's repository, base, head, title, body, draft
   state, open state, and URL. A pushed branch without a created and verified pull request is
   a failed `outcome_result`; report the proven push and branch as residual publication with the
   continuation owner and exact action. Preserve `history_result`.

Retain the source branch, worktree, and required recovery refs for review updates. A later
independently proven integration may authorize cleanup; pull-request creation alone does not.
A verified pull request produces a proven `outcome_result` classified `non-integrating handoff`.
