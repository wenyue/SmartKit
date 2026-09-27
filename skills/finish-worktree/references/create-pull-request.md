# Create a Pull Request

Publish one exact accepted commit and establish its PR through the repository's host interface.
Derive routine title, body and draft state from accepted scope and project conventions. This route
proves a handoff for review; a PR alone does not prove authoritative delivery.

## Bind the intended publication

Identify the remote repository, base branch and observed base OID, head ref and host state. Search
for an existing PR by repository, base and head before creating one. Reuse a matching open PR,
checking its actual head and making only authorized metadata updates. A closed, merged,
incompatible or ambiguous match needs a continuation decision. A missing create response is not
evidence that no PR exists.

Consume [History Preparation](history.md) and its accepted-state binding. Task work outside that
accepted commit returns to the implementation owner unless a successor scope is separately
authorized. Unrelated local work can stay dirty when publication cannot affect it and preservation
is established.

Refresh the binding, remote base and head immediately before publication. A moved base follows
History Preparation's result-preservation boundary. If the authoritative target already contains
the result with **Already Delivered** proof, report that result without an empty PR. If the exact
PR already exists, reuse it without a duplicate push or create.

## Publish and observe each effect

Use a non-force push of the exact delivery OID to the exact head ref. Observe that remote ref equal
to the delivery OID before creating the PR. Push and PR creation are separate effects in the
[recovery receipt](recovery.md), since one can succeed while the other fails.

After a race, rejection, timeout or missing response, inspect server state and resolve the original
attempt before retrying. A proven push with failed PR creation leaves publication as a known effect;
retain the source, ref, receipt and recovery owner needed to finish the PR.

To prove the outcome, bind the remote head and PR head to the delivery OID and verify repository,
base, head ref, open state, required metadata and URL. Retain the items needed for review and
updates, with their owners and release conditions. Preserve independently proven publication in a
failed result even when PR proof remains unavailable.
