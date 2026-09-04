# Create a Pull Request

Publish the verified delivery head without force, then establish at most one exact pull request.
This remains a non-integrating handoff until the authoritative target contains the accepted result.

1. Require explicit authority for every remote effect. Freeze the repository, base branch and
   observed commit, head ref, delivery commit, title, body, draft state, repository-approved host
   interface, and success proof. Authorized observation must also establish any existing remote head
   and pull request.
2. Recheck the source, immutable `history_result`, owned range, delivery head and tree, review
   binding, publication, and remote base and head. A moved base is target drift after history; never
   repeat the history policy. Reprove **Already Delivered** when possible. Otherwise retain
   `history_result` for the target-movement owner and stop with `outcome_result: stopped`. An
   incompatible head, uncertain publication, unavailable host proof, or ambiguous earlier attempt
   also stops before another effect.
3. If the base contains every accepted effect, return **Already Delivered** without a push or empty
   pull request. If one open pull request already matches every frozen field and exact delivery
   commit, verify and return that existing handoff without duplication.
4. Otherwise push the exact delivery commit once to the frozen head ref with a normal, non-force
   push as one logical attempt. Only after proving that result, create the pull request once through
   the approved interface as a second logical attempt. Re-observe before and after each. An
   ambiguous result remains in-flight, is retained, and is never retried.
5. Prove the remote head commit and the pull request's repository, base, head, title, body, draft
   state, open state, and URL. A pushed branch without a created and verified pull request is
   a failed `outcome_result`; report the proven push and branch as residual publication with the
   continuation owner and exact action. Preserve `history_result`.

Retain the source branch, worktree, and required recovery refs for review updates. Pull-request
creation alone never authorizes cleanup; a later independently proven integration may do so. A
verified pull request produces `outcome_result: proven`, classified `non-integrating handoff`.
