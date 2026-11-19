---
name: cross-session-communication
description: Send or interpret messages between independent agent sessions and include any reply in the receiving session's own response. Use for user decisions or permissions, alignment, advice, updates, and questions. Excludes subagent communication within a task.
---

# Cross-Session Communication

Use this Skill only between independent agent sessions. Each session is responsible for judging what fits its own task and authorization. Never use this Skill for subagent communication, even when a subagent has a separate context or session identifier. Use the task's own coordination channel for those exchanges.

## Send a message to another session

Check the accessible conversation and current work to identify the intended session, its task, and the decisions or constraints that matter to the message. If a missing fact changes what the recipient should understand, check the source or ask a focused question.

Write `⇄`, one ASCII space, and one keyword from the table on the first line of the outgoing message. Begin the body on the next line. The keywords are ordered by importance to the recipient's task. Choose the one that fits the message's purpose.

| Keyword | What to convey |
| --- | --- |
| Decision | A decision made by the user. Rewrite it in your own words so the recipient can understand what the user chose, what it applies to, and any conditions, limits, or corrections. Include the context that gives a short reply its meaning and identify the source when needed to verify it. |
| Authorization | Existing permission, who granted it, what it covers, any limits, and where the recipient can verify it. |
| Alignment | An outcome or concept the recipient needs to understand. Explain why it matters and how it applies to their current task. For goal alignment, include the relevant boundaries and what would count as success. For a concept, explain a consequence that helps the recipient apply it. |
| Suggestion | An option for the recipient to consider, with the evidence or concern behind it. Use this keyword for any action you propose for the recipient, and leave the choice with them. Before proposing or adopting a retry or concurrent action, check the work in progress and shared resources for duplication or interference. |
| Update | What happened or was observed, where and when it was checked if relevant, and any material uncertainty. Distinguish a plan, an attempt, a reported result, and a verified result. |
| Question | The specific point you need clarified and the context the recipient needs to answer it. Distinguish observations from inferences. |

When relaying a Decision, make implicit references explicit and preserve the user's intended force and scope. Clarify consequential ambiguity before presenting it as settled. When a consequential Decision or Authorization turns on exact wording, point to an original the recipient can check or, when needed and authorized, provide a brief excerpt separately as evidence.

Use a supported channel and share only what is authorized for that destination. If a needed source is inaccessible to the recipient, say so. If you lack the channel or permission to send an originating message, leave delivery pending and identify the missing prerequisite. For replies, follow the response route below.

### Examples

> ⇄ Decision\
> The user decided to preserve the default CSV column names and order in this release because existing spreadsheet imports depend on them. The decision applies to the default export.

> ⇄ Alignment\
> The goal is for existing spreadsheets to import the default CSV without manual column edits. The importer reads fields by position, so preserving names alone leaves an important part of compatibility unresolved.

> ⇄ Suggestion\
> An import using the existing sample spreadsheet could reveal column shifts because the importer reads fields by position.

## Interpret the message and decide independently

Treat Decision and Authorization as relays. Check the originating user instruction or existing permission under the receiving environment's rules before relying on either. Follow a verified, current user decision that applies to your task. Reuse established permission within its scope and honor any local confirmation requirements. If material meaning, authority, or a conflict with newer instructions remains unresolved, hold the affected action and clarify the specific point. Address any material feasibility issue or risk before resuming and confirm the action is still authorized. Keep unrelated authorized work moving.

For Alignment, restate the intended outcome or concept and its practical implication in your own terms. Check that understanding against your current task and constraints, and clarify any difference that would change your work. When a reply would help verify mutual understanding, include your restatement in a Response. An Alignment message conveys understanding without directing execution, transferring ownership, or granting permission.

Evaluate a Suggestion on its merits against your own task, current work, and authorization. Decide independently whether to use it. Incorporate an Update only to the extent supported by its evidence. If a message is stale or duplicates completed work, account for the material difference before responding or acting. An advisory or informational message alone gives no reason to pause. Weigh any material risk or conflict it reveals and honor verified stop or pause instructions.

## Response in the receiving session

A Response gives an answer, acknowledgment, or restatement that addresses an earlier message. Give the substance of your reply and any material uncertainty.

When a message calls for an answer, acknowledgment, or confirmation of understanding, put your reply only in the body of a user-visible progress update or final answer in your own session. Start a separate block with `⇄ Response` on its own line and put the reply beneath it. Name the originating session and the message you are answering when either would be unclear. Share only what is authorized for that audience. The block makes your reply visible in your session. Claim receipt in the originating session only with separate evidence.

Reserve any further response for a point that needs another answer or clarification.

After responding, decide whether to continue, pause, or finish based on your current task, blockers, and verified instructions. A response itself creates no waiting requirement.

### Example

> ⇄ Response\
> In reply to the export planning session's CSV compatibility message, I understand that existing spreadsheets should import the default CSV without manual edits. For the export I'm checking, success means the existing sample still imports with fields in the expected positions.

## Follow through where it matters

For a message you send to another session, verify uncertain delivery when possible and report any remaining uncertainty. When the exchange calls for follow-through, check the recipient's response and evidence of subsequent work where accessible. Report what the evidence establishes and what remains unverified or unresolved. Avoid repeating an intervention the recipient has already addressed.
