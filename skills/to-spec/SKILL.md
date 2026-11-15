---
name: to-spec
description: "Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed."
disable-model-invocation: true
---

Synthesize the current conversation and codebase understanding into a spec. Carry forward the latest agreed goals, scope, design, and testing decisions, including corrections that supersede earlier ones. Do not restart an interview or ask the user to reconfirm settled decisions. Ask only about unresolved facts or choices that materially affect scope, safety, or acceptance and cannot be recovered from the available context.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Carry forward agreed testing decisions and fill any gaps from the codebase. Prefer existing seams; choose the smallest sufficient set of test levels that verifies the accepted behavior and material risks with useful failure signals, reasonable cost, and stable tests. Use a higher-level test where it can establish the behavior reliably; add a narrower test where it provides necessary coverage or diagnosis. A new seam needs a concrete coverage gap, not a preference for one ideal level.

3. Write the spec using the template below, then publish it to the project issue tracker within the user's authorization. Apply `ready-for-agent` only when material decisions needed for implementation and acceptance are settled; no additional triage is needed then. If a material decision remains open, identify it and leave the spec as a draft without that label rather than inventing an answer.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A numbered list of user stories covering the agreed scope. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

Cover the accepted outcomes and relevant boundary cases without adding features or splitting stories merely to lengthen the list.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>
