# Create a Pull Request

Publish the exact accepted commit and establish its PR through the repository's host interface. A PR hands the work off for review; it does not establish authoritative delivery.

## Establish the accepted commit and PR destination

Read [History Preparation](history.md), then identify the remote repository, base branch and OID, head ref and accepted commit. Remote writes require the user's request for that outcome; a PR request includes its necessary publication. Derive routine title, body and draft state from the accepted scope and project conventions.

Search for an existing PR by repository, base and head. Reuse a matching open PR, checking its actual head and making only authorized updates. A closed, merged, incompatible or ambiguous match needs a continuation decision. If the target already contains the whole result under History Preparation's delivery check, report that instead of opening an empty PR.

## Publish and verify each independent effect

Refresh local and remote refs before publication. A moved base needs a fresh check that acceptance still applies; otherwise return to the implementation workflow. Push the exact accepted OID to the intended head ref without force, then observe that the remote ref matches before creating or updating the PR. Skip an already satisfied push or create.

After rejection, interruption or a missing response, inspect remote refs and PR state before retrying. Push and PR creation can succeed independently. Preserve a successful publication in the report even if PR creation fails, and retain the source and remote ref for continuation.

Verify the remote and PR heads equal the accepted OID, with the intended repository, base, head ref, open state, metadata and URL. Retain what review and future updates need. Report the PR and any remaining work; worktree cleanup must preserve that ability to continue.
