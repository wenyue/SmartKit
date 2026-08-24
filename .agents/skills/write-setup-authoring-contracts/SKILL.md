---
name: write-setup-authoring-contracts
description: Author or materially revise this repository's Setup Authoring Contracts under setup-assets/blueprints; generated project Rules or Skills and shared SmartKit Rules or Skills have separate owners.
---

# Write Setup Authoring Contracts

Create the smallest complete generation input that lets `setup-project-agents` use the public
`write-rules-and-skills` Skill to author one project-local Rule or Skill from target-repository
evidence. Apply `writing-for-agents` to the contract. This project-private Hybrid Skill owns
contract authoring and its static qualification.

## Establish the contract

Use the accepted change, the current blueprint when one exists, the setup catalog entry, and
representative target evidence. Read
[`references/setup-authoring-contract.md`](references/setup-authoring-contract.md) completely before
writing.

Stop when the referenced frame still has more than one supported meaning. Apply the public
authoring Skill's Soft-Isolation Probe, then give one tool-free Author a complete project-aware
Context Packet containing the accepted change, current contract, setup catalog evidence, selected
target evidence, referenced frame, and canonical target. The Author returns complete replacement
content or `CONTEXT_REQUIRED`; the controller applies returned content unchanged only under
`setup-assets/blueprints/` and verifies it.

## Validate and review

Run and require the repository machine checks for every affected surface to pass. Then give one new
Soft-isolated, tool-free Reviewer a complete Context Packet containing the accepted outcome, the
complete contract, the future target semantic type, governing evidence, and one representative
walkthrough input. Give it no intended answer, suspected defect, or author reasoning.

The same Reviewer returns separate judgments for:

- minimality: no instruction can be removed without changing a supported generation-or-stop outcome;
- semantic completeness: the contract obtains or stops for every target obligation that can change
  behavior; and
- representative walkthrough: one supported target input reaches exactly one generation or stop
  outcome without inventing project facts.

Do not start a Pruning Agent or Acceptance Runner and do not generate a target merely to qualify the
contract. A content change invalidates the machine results and the whole static review. Apply all
`uniquely-forced` findings together through the Author and use a new Soft-isolated Reviewer for the
revised candidate; stop on any `decision-required` finding or repeated unchanged finding.

Success requires machine validation and all three static judgments to pass for the same Candidate
Revision. Hand the accepted contract to `setup-project-agents`.
