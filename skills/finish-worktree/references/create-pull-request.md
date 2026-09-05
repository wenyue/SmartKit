# Create a Pull Request

Publish one exact verified and reviewed commit and establish its pull request. The accepted PR
request supplies publication authority; use the repository-approved host interface and infer routine
title, body and draft choices from the accepted scope and project conventions.

Establish the remote repository, base branch and observed base commit, intended head ref, and current
host state. Search for an existing PR by repository, base and head before any creation. A matching
open PR may be reused; check its actual head commit and metadata, updating only fields within the
accepted request. A closed, merged, incompatible or ambiguously identified PR requires a specific
continuation decision; never create a replacement merely because a prior call lacked a response.

Use [history preparation](history.md) to bind the delivery commit and exact tree to required
verification and blocker-free formal review. Task work outside that committed result returns to the
implementation owner unless accepted authority identifies it as a separate preserved successor
scope. Proven unrelated local state can remain outside the publication effect; retain a dirty source.

Before publication, recheck the delivery binding and remote base/head. Base movement invalidating
the frozen boundary returns to implementation for synchronization and renewed verification/review;
preserve any proven history result. If the authoritative base already contains the accepted result,
use history.md's **Already Delivered** proof and create no empty PR. An existing exact PR is a
successful handoff without a duplicate push or creation.

Otherwise push the immutable delivery OID to the exact head ref using a normal non-force push.
Observe that the remote ref equals that OID before creating or updating the PR. Treat publication
and PR establishment as separate effects in the receipt. A race, rejection, timeout or interruption
enters [recovery](recovery.md); observe the server before deciding which effect remains incomplete.

Prove the remote head and PR head equal the delivery OID, and verify repository, base, head ref,
open state, intended metadata and URL. That yields `outcome_result: proven` and
`classification: non-integrating handoff`. A proven push followed by failed PR establishment is
`outcome_result: failed`: retain the publication fact, source, branch, receipt and recovery owner.
Resume PR establishment after observation; do not push again merely because PR creation failed.

Retain the source and required recovery state for review updates. A PR alone does not release them
for cleanup or establish authoritative delivery.
