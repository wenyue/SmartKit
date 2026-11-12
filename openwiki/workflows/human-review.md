---
type: workflow
title: Human review and verified completion
description: How grouped human review pins its comparison and how the PR completion helper verifies delivery and GitHub Viewed state.
tags: [review, github, git, diffs, viewed, delivery]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:28:05.666Z
sources:
  - id: openwiki-source-06c529150bf650bb6b122ad2
    resource: repo://skills/review-for-humans/scripts/complete_review.py
  - id: openwiki-source-08fee7ad8b02424a0a7c7490
    resource: repo://skills/review-for-humans/SKILL.md
  - id: openwiki-source-597eeef93d9bf96a3851f49f
    resource: repo://tests/test_review_completion.py
generated: { by: "smartkit", at: "2026-11-12T04:28:05.666Z" }
---

# Human review and verified completion

[Review for Humans](../../skills/review-for-humans/SKILL.md) pins a PR's base and head and reads the authenticated viewer's file-level Viewed state. Branch reviews use a fixed tip and established merge-base. Local review defaults to index versus worktree. File and test filters define assessment coverage. Review orders eligible files by directory, explains complete groups with stable modification IDs, and assesses reasonableness and implementation quality independently.

The local web CLI generates links for the reviewed files. A fixed before version and a verified display workspace bind the link. The review still uses its captured evidence when the live editor workspace differs. A review's display filters do not narrow the actual scope of a later commit or its checks. [Local web service](../operations/local-web.md) · [Review delivery contract](../../skills/review-for-humans/references/delivery.md)

## PR completion

The completion helper prepares a private plan using the selected workspace, PR source and viewer, reviewed contents, effect set, and verification evidence. Its run revalidates that state before mutation. For publication it compares the expected tree and outgoing ancestry, uses normal hooks, and publishes conditionally to the verified source ref. It reads back the remote source and PR version before recording Viewed. In Viewed-only mode it validates the saved workspace and PR without staging or publication. [Completion helper](../../skills/review-for-humans/scripts/complete_review.py)

Viewed recording uses bounded retries for transient failures. Each attempt rereads the PR and revalidates the workspace, evidence, and PR version. It skips files already marked Viewed, then checks the entire requested set. Progress records support resuming after partial or uncertain effects. The tests cover lost commit and push responses, racing source refs, partial Viewed results, and retry exhaustion. [Completion tests](../../tests/test_review_completion.py)
