---
type: workflow
title: Rule and Skill authoring and review
description: How SmartKit scopes a Candidate, preserves its baseline, checks the proposed version, and obtains review before handoff.
tags: [authoring, rules, skills, review, evidence]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-12T04:28:05.666Z
sources:
  - id: openwiki-source-539c0c1e0c5f33ac8f162a0d
    resource: repo://skills/write-rules-and-skills/references/artifact-relationships.md
  - id: openwiki-source-5c5c313e9f09d1947a3899f0
    resource: repo://skills/write-rules-and-skills/references/controller.md
  - id: openwiki-source-7169d8309acfa927bda363cb
    resource: repo://skills/write-rules-and-skills/SKILL.md
  - id: openwiki-source-bec839df9e81b363bd6aebf3
    resource: repo://tests/test_write_rules_and_skills_checks.py
  - id: openwiki-source-ccd1dc2b803dedc607db464e
    resource: repo://tests/test_write_rules_and_skills_evidence.py
generated: { by: "smartkit", at: "2026-11-12T04:28:05.666Z" }
---

# Rule and Skill authoring and review

The [writer Skill](../../skills/write-rules-and-skills/SKILL.md) treats one Rule or Skill and its scoped supporting resources as a Candidate. The Controller owns the assignment, accepted scope, version evidence, and user decisions. A resident Author owns design and writing through repairs. Quality, Change, and Correctness reviewers evaluate usability, preservation or deliberate revision of meaning, and fulfillment of the actual request. Correctness can request a bounded Runner observation when behavior needs to be exercised. [Controller contract](../../skills/write-rules-and-skills/references/controller.md) · [Authoring glossary](../../contexts/authoring-evaluation/GLOSSARY.md)

## Evidence and checks

The Controller freezes the exact pre-write scope outside the Candidate root. `candidate_evidence.py` captures present and absent paths, file bytes, and executable mode where supported. Comparison reports additions, changes, deletions, and violations of allowed change paths. Scope additions carry forward the original evidence and require a pre-write supplement. [Evidence helper](../../skills/write-rules-and-skills/scripts/candidate_evidence.py) · [Evidence tests](../../tests/test_write_rules_and_skills_evidence.py)

The candidate checker validates Markdown paragraph boundaries, relative links and anchors, and Skill frontmatter. Its path mapping lets scoped links resolve within a staged Candidate and retained links resolve against the target. It can check exact content required by accepted inputs. Those checks establish document properties. Reviewers assess semantics and the supported environment on the same checked version. Completion requires passing checks and all three judgments on the final Candidate. [Candidate checker](../../skills/write-rules-and-skills/scripts/check_candidate.py) · [Checker tests](../../tests/test_write_rules_and_skills_checks.py)

## Ownership and handoff

Dependencies are based on required behavior and resources. An owned reference is part of its Rule or Skill. Cross-artifact reads use supported interfaces within the provider and project dependency scope. The relationship contract requires an acyclic graph and puts dependencies before consumers when setup authors a generated set. [Artifact relationships](../../skills/write-rules-and-skills/references/artifact-relationships.md) · [Project setup](../configuration/project-setup.md)

This workflow hands a checked artifact to its caller. Installation, distribution, and configuration adoption have their own owners. In this self-hosting repository, corresponding checkout sources govern unless an explicit reference selects another copy. [Source authority](../../.agents/rules/self-hosting-authority.md) · [Plugin distribution](../architecture/plugin-distribution.md)
